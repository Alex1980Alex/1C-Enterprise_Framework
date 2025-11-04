// === Configuration ===
const API_BASE_URL = 'http://localhost:8000';

// === DOM Elements ===
const searchInput = document.getElementById('search-input');
const clearBtn = document.getElementById('clear-btn');
const searchBtn = document.getElementById('search-btn');
const topKSelect = document.getElementById('top-k');
const thresholdSelect = document.getElementById('threshold');
const exampleBtns = document.querySelectorAll('.example-btn');

const loading = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');
const resultsContainer = document.getElementById('results-container');
const noResults = document.getElementById('no-results');

const queryText = document.getElementById('query-text');
const resultsCount = document.getElementById('results-count');
const searchTime = document.getElementById('search-time');

const collectionName = document.getElementById('collection-name');
const vectorsCount = document.getElementById('vectors-count');
const healthStatus = document.getElementById('health-status');

// === Initialization ===
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadHealth();
    setupEventListeners();
});

// === Event Listeners ===
function setupEventListeners() {
    // Search button
    searchBtn.addEventListener('click', performSearch);

    // Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Clear button
    searchInput.addEventListener('input', () => {
        clearBtn.style.display = searchInput.value ? 'flex' : 'none';
    });

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearBtn.style.display = 'none';
        searchInput.focus();
    });

    // Example buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-query');
            searchInput.value = query;
            clearBtn.style.display = 'flex';
            performSearch();
        });
    });
}

// === API Functions ===
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/stats`);
        const data = await response.json();

        collectionName.textContent = data.collection_name;
        vectorsCount.textContent = data.points_count.toLocaleString();
    } catch (error) {
        console.error('Error loading stats:', error);
        collectionName.textContent = 'Error';
        vectorsCount.textContent = '-';
    }
}

async function loadHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            healthStatus.textContent = '✓ Healthy';
            healthStatus.style.color = 'var(--secondary-color)';
        } else {
            healthStatus.textContent = '⚠ Degraded';
            healthStatus.style.color = 'var(--warning-color)';
        }
    } catch (error) {
        console.error('Error loading health:', error);
        healthStatus.textContent = '✗ Offline';
        healthStatus.style.color = 'var(--danger-color)';
    }
}

async function performSearch() {
    const query = searchInput.value.trim();

    if (!query) {
        alert('Пожалуйста, введите поисковый запрос');
        searchInput.focus();
        return;
    }

    const topK = parseInt(topKSelect.value);
    const threshold = parseFloat(thresholdSelect.value);

    // Show loading, hide results
    loading.style.display = 'block';
    resultsSection.style.display = 'none';
    noResults.style.display = 'none';

    try {
        const url = `${API_BASE_URL}/api/v1/search?query=${encodeURIComponent(query)}&top_k=${topK}&score_threshold=${threshold}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Hide loading
        loading.style.display = 'none';

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Search error:', error);
        loading.style.display = 'none';
        alert(`Ошибка поиска: ${error.message}`);
    }
}

// === Display Functions ===
function displayResults(data) {
    queryText.textContent = data.query;
    resultsCount.textContent = data.total_found;
    searchTime.textContent = data.search_time_ms.toLocaleString();

    if (data.results.length === 0) {
        noResults.style.display = 'block';
        return;
    }

    // Clear container
    resultsContainer.innerHTML = '';

    // Create result cards
    data.results.forEach((result, index) => {
        const card = createResultCard(result, index + 1);
        resultsContainer.appendChild(card);
    });

    resultsSection.style.display = 'block';
}

function createResultCard(result, rank) {
    const card = document.createElement('div');
    card.className = 'result-card';

    // Score percentage
    const scorePercent = (result.score * 100).toFixed(1);
    const scoreClass = getScoreClass(result.score);

    // File name from path
    const fileName = result.file_path.split(/[\\/]/).pop();

    // Truncate searchable text
    const codePreview = result.searchable_text.substring(0, 500);

    card.innerHTML = `
        <div class="result-header">
            <div class="result-title">
                <span class="result-rank">${rank}</span>
                <span class="result-filename">${escapeHtml(fileName)}</span>
            </div>
            <div class="result-score ${scoreClass}">${scorePercent}%</div>
        </div>

        <div class="result-meta">
            <div class="meta-badge">
                <svg class="meta-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <polyline points="13 2 13 9 20 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                ${escapeHtml(result.module_type)}
            </div>
            <div class="meta-badge">
                <svg class="meta-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Функций: ${result.functions_count}
            </div>
            <div class="meta-badge">
                <svg class="meta-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                Переменных: ${result.variables_count}
            </div>
        </div>

        <div class="result-path">${escapeHtml(result.file_path)}</div>

        <div class="result-code">
            <pre><code class="language-bsl">${escapeHtml(codePreview)}${result.searchable_text.length > 500 ? '\n...' : ''}</code></pre>
        </div>
    `;

    return card;
}

// === Utility Functions ===
function getScoreClass(score) {
    if (score >= 0.7) return 'score-high';
    if (score >= 0.5) return 'score-medium';
    return 'score-low';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// === Prism.js Syntax Highlighting ===
// Define BSL language for Prism
Prism.languages.bsl = {
    'comment': [
        {
            pattern: /(^|[^\\])\/\/.*/,
            lookbehind: true
        }
    ],
    'string': {
        pattern: /"(?:\\.|[^\\"\r\n])*"/,
        greedy: true
    },
    'keyword': /\b(?:Процедура|Функция|КонецПроцедуры|КонецФункции|Если|Тогда|Иначе|ИначеЕсли|КонецЕсли|Для|По|Цикл|КонецЦикла|Пока|Попытка|Исключение|КонецПопытки|Возврат|Прервать|Продолжить|И|Или|Не|Новый|Перем|Экспорт|Знач|Procedure|Function|EndProcedure|EndFunction|If|Then|Else|ElseIf|EndIf|For|To|Do|While|Try|Except|EndTry|Return|Break|Continue|And|Or|Not|New|Var|Export|Val)\b/i,
    'boolean': /\b(?:Истина|Ложь|True|False|Неопределено|Undefined)\b/i,
    'number': /\b\d+(?:\.\d+)?\b/,
    'operator': /[+\-*/%=<>!&|]+/,
    'punctuation': /[{}[\];(),.:]/
};

// Auto-highlight code after rendering
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.addedNodes.length) {
            Prism.highlightAll();
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
