# AI Memory System - Architecture Document

**Version**: 1.0
**Date**: 31 октября 2025
**Status**: In Development

---

## 🎯 Цель

Создать систему **долгосрочной памяти** для Claude AI, которая:
- Сохраняет историю разговоров между сессиями
- Векторизует важные факты и контекст
- Автоматически восстанавливает релевантный контекст
- Строит knowledge graph из разговоров

---

## 🏗️ Архитектура

### Компоненты Системы

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude AI Session                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Conversation Memory Service                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Capture    │  │  Vectorize   │  │   Restore    │      │
│  │  Messages    │→ │   Context    │→ │   Context    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ TimescaleDB  │ │   Qdrant     │ │    Neo4j     │
│              │ │              │ │              │
│ - Messages   │ │ - Embeddings │ │ - Entities   │
│ - Sessions   │ │ - Semantic   │ │ - Relations  │
│ - Metadata   │ │   Search     │ │ - Graph      │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📦 Data Models

### 1. Conversation (TimescaleDB)

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    user_id VARCHAR(255),
    project_context VARCHAR(500),
    total_messages INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_started ON conversations(started_at DESC);
```

### 2. Messages (TimescaleDB)

```sql
CREATE TABLE messages (
    id BIGSERIAL,
    conversation_id UUID REFERENCES conversations(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens_count INT,
    importance_score FLOAT DEFAULT 0.0,
    has_code BOOLEAN DEFAULT FALSE,
    has_entities BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    PRIMARY KEY (timestamp, id)
);

-- Hypertable для time-series
SELECT create_hypertable('messages', 'timestamp');

CREATE INDEX idx_messages_conversation ON messages(conversation_id, timestamp DESC);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_importance ON messages(importance_score DESC);
```

### 3. Message Embeddings (Qdrant)

```python
# Collection: conversation_memory
{
    "id": "msg_<uuid>",
    "vector": [768-dim embedding],
    "payload": {
        "message_id": "bigint",
        "conversation_id": "uuid",
        "timestamp": "iso8601",
        "role": "user|assistant",
        "content_preview": "first 500 chars",
        "importance": 0.0-1.0,
        "entities": ["entity1", "entity2"],
        "topics": ["topic1", "topic2"]
    }
}
```

### 4. Knowledge Graph (Neo4j)

```cypher
// Nodes
(:Conversation {id, session_id, started_at})
(:Message {id, timestamp, role, content_preview})
(:Entity {name, type, first_seen})
(:Topic {name, category})
(:Project {name, path})
(:Person {name, email})
(:Task {title, status})

// Relationships
(:Conversation)-[:CONTAINS]->(:Message)
(:Message)-[:MENTIONS]->(:Entity)
(:Message)-[:RELATES_TO]->(:Topic)
(:Message)-[:REFERENCES]->(:Message)
(:Conversation)-[:ABOUT]->(:Project)
(:Entity)-[:CONNECTED_TO]->(:Entity)
```

---

## 🔄 Data Flow

### 1. Message Capture

```
User Message → Conversation Service
    ↓
1. Save to TimescaleDB
2. Create embedding (Ollama)
3. Store vector in Qdrant
4. Extract entities
5. Update Neo4j graph
```

### 2. Context Restoration

```
New Session Started
    ↓
1. Query recent conversations (TimescaleDB)
2. Semantic search similar messages (Qdrant)
3. Load related entities (Neo4j)
4. Build context summary
5. Inject into new session
```

---

## 🛠️ Services

### 1. ConversationStorage Service

**Responsibilities**:
- Save/load conversations
- Message persistence
- Session management

**API**:
```python
class ConversationStorage:
    def create_conversation(session_id, metadata) -> UUID
    def add_message(conv_id, role, content, metadata) -> int
    def get_conversation(conv_id) -> Conversation
    def get_recent_conversations(limit=10) -> List[Conversation]
    def close_conversation(conv_id)
```

### 2. MessageVectorization Service

**Responsibilities**:
- Create embeddings
- Store in Qdrant
- Semantic search

**API**:
```python
class MessageVectorization:
    def vectorize_message(message) -> List[float]
    def store_vector(message_id, vector, payload)
    def search_similar(query, limit=10) -> List[Message]
```

### 3. ContextRestoration Service

**Responsibilities**:
- Load relevant history
- Build context
- Inject into session

**API**:
```python
class ContextRestoration:
    def get_relevant_context(query, session_id) -> str
    def get_related_entities(conv_id) -> List[Entity]
    def build_context_summary(messages) -> str
```

### 4. EntityExtraction Service

**Responsibilities**:
- Extract entities from text
- Build knowledge graph
- Track relationships

**API**:
```python
class EntityExtraction:
    def extract_entities(text) -> List[Entity]
    def create_relationships(msg_id, entities)
    def query_entity_graph(entity_name) -> Graph
```

---

## 🔌 Integration Points

### 1. Memory MCP Server

```python
# MCP Tools для Claude
- save_conversation_fact(text, importance)
- search_memory(query, limit)
- get_session_context(session_id)
- create_entity(name, type, metadata)
- relate_entities(entity1, entity2, relation_type)
```

### 2. REST API Endpoints

```
POST   /api/v1/memory/conversations
POST   /api/v1/memory/conversations/{id}/messages
GET    /api/v1/memory/conversations/{id}
GET    /api/v1/memory/conversations/{id}/context
POST   /api/v1/memory/search
GET    /api/v1/memory/entities
GET    /api/v1/memory/entities/{name}/graph
```

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Message save | < 50ms |
| Vector creation | < 2s |
| Context retrieval | < 100ms |
| Semantic search | < 200ms |
| Entity extraction | < 500ms |

---

## 🔒 Security

- **Encryption**: All messages encrypted at rest
- **Access Control**: Session-based isolation
- **Privacy**: PII detection & masking
- **Retention**: Configurable retention policies

---

## 🚀 Implementation Plan

### Week 2, Day 4 (Current)
- ✅ Architecture design
- 🔄 ConversationStorage service
- 🔄 TimescaleDB schema
- 🔄 Basic message persistence

### Week 2, Day 5
- MessageVectorization service
- Qdrant integration
- ContextRestoration service
- Entity extraction

### Week 3, Day 1
- Neo4j knowledge graph
- MCP server integration
- REST API endpoints

### Week 3, Day 2
- Testing & optimization
- Documentation
- Production deployment

---

## 📝 Usage Example

```python
# Start new conversation
conv_id = storage.create_conversation(
    session_id="session_2025_10_31",
    metadata={"project": "1C Framework"}
)

# Save user message
storage.add_message(
    conv_id=conv_id,
    role="user",
    content="Как работает BSL индексация?",
    metadata={"importance": 0.8}
)

# Save assistant response
storage.add_message(
    conv_id=conv_id,
    role="assistant",
    content="BSL индексация использует Qdrant...",
    metadata={"has_code": True}
)

# Later: Restore context
context = restoration.get_relevant_context(
    query="BSL indexing",
    session_id="session_2025_10_31"
)

# Returns:
"""
Previous conversation context:
- User asked about BSL indexing
- Discussed Qdrant integration
- Showed code examples
Related entities: Qdrant, BSL, Indexing
"""
```

---

## 🎯 Success Criteria

1. ✅ Conversations persist между сессиями
2. ✅ Context восстанавливается автоматически
3. ✅ Semantic search работает < 200ms
4. ✅ Entity graph строится корректно
5. ✅ MCP integration функционирует

---

**Document Status**: Draft → In Implementation
**Last Updated**: 31 октября 2025, 03:00
**Author**: AI Memory System Team
