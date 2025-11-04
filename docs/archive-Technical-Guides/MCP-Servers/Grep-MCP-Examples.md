# 🔎 Grep MCP - Практические примеры для 1С

[← К справочнику MCP](../MCP-Complete-Reference.md) | [К оглавлению](../README.md)

## 📚 Оглавление
- [Текстовый поиск в BSL файлах](#текстовый-поиск-в-bsl-файлах)
- [Поиск по метаданным конфигурации](#поиск-по-метаданным-конфигурации)
- [Интеграция с анализом кода](#интеграция-с-анализом-кода)
- [Поиск в документации и комментариях](#поиск-в-документации-и-комментариях)
- [Автоматизация рутинных задач поиска](#автоматизация-рутинных-задач-поиска)

---

## 📄 Текстовый поиск в BSL файлах

### Пример 1: Поиск использования переменных
```javascript
// Поиск всех использований конкретной переменной в BSL коде
async function findVariableUsage(variableName, configPath) {
    console.log(`🔍 Ищу использования переменной: ${variableName}`);
    
    // Основной поиск переменной
    const mainSearch = await mcp__ripgrep__search({
        pattern: `\\b${variableName}\\b`,
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true,
        context: 2
    });
    
    // Поиск объявления переменной
    const declarationSearch = await mcp__ripgrep__search({
        pattern: `(Перем\\s+${variableName}|${variableName}\\s*=)`,
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true,
        context: 1
    });
    
    // Анализ результатов
    const analysis = analyzeVariableUsage(mainSearch, declarationSearch, variableName);
    
    // Генерация отчета
    const report = generateVariableReport(variableName, analysis);
    
    // Сохранение отчета
    const reportPath = `reports/variable-${variableName}-${Date.now()}.md`;
    await mcp__filesystem__write_file({
        path: reportPath,
        content: report
    });
    
    return {
        variableName: variableName,
        totalUsages: analysis.totalUsages,
        declarations: analysis.declarations,
        assignments: analysis.assignments,
        usages: analysis.usages,
        reportPath: reportPath
    };
}

function analyzeVariableUsage(mainSearch, declarationSearch, variableName) {
    const analysis = {
        totalUsages: 0,
        declarations: [],
        assignments: [],
        usages: [],
        files: new Set()
    };
    
    // Анализ основного поиска
    const mainLines = mainSearch.split('\n');
    for (const line of mainLines) {
        if (line.includes('.bsl:') && line.includes(variableName)) {
            analysis.totalUsages++;
            
            const match = line.match(/^([^:]+):(\\d+):(.+)$/);
            if (match) {
                const file = match[1];
                const lineNum = parseInt(match[2]);
                const content = match[3].trim();
                
                analysis.files.add(file);
                
                if (content.includes('Перем')) {
                    analysis.declarations.push({ file, lineNum, content });
                } else if (content.includes('=') && !content.includes('==')) {
                    analysis.assignments.push({ file, lineNum, content });
                } else {
                    analysis.usages.push({ file, lineNum, content });
                }
            }
        }
    }
    
    return analysis;
}

function generateVariableReport(variableName, analysis) {
    return `# Анализ переменной "${variableName}"

## 📊 Статистика
- **Всего использований:** ${analysis.totalUsages}
- **Файлов затронуто:** ${analysis.files.size}
- **Объявлений:** ${analysis.declarations.length}
- **Присвоений:** ${analysis.assignments.length}
- **Чтений:** ${analysis.usages.length}

## 📋 Объявления переменной
${analysis.declarations.map(decl => 
    `- **${decl.file}:${decl.lineNum}** - \`${decl.content}\``
).join('\n') || 'Объявления не найдены'}

## ✏️ Присвоения значений
${analysis.assignments.map(assign => 
    `- **${assign.file}:${assign.lineNum}** - \`${assign.content}\``
).join('\n') || 'Присвоения не найдены'}

## 🔍 Использования
${analysis.usages.slice(0, 10).map(usage => 
    `- **${usage.file}:${usage.lineNum}** - \`${usage.content}\``
).join('\n')}

${analysis.usages.length > 10 ? `\n... и еще ${analysis.usages.length - 10} использований` : ''}

## 🎯 Рекомендации
${analysis.declarations.length === 0 ? '⚠️ Переменная используется без объявления - возможно, это глобальная переменная' : ''}
${analysis.assignments.length === 0 ? '⚠️ Переменная не изменяется - возможно, это константа' : ''}
${analysis.usages.length === 0 ? '⚠️ Переменная объявлена, но не используется' : ''}

---
*Анализ выполнен: ${new Date().toLocaleString()}*
`;
}

// Использование
const variableAnalysis = await findVariableUsage("СуммаДокумента", "src/projects/configuration/demo-accounting");
```

### Пример 2: Поиск строковых литералов и сообщений пользователю
```javascript
// Поиск всех сообщений пользователю и строковых констант
async function findUserMessages(configPath) {
    console.log("💬 Ищу сообщения пользователю...");
    
    const messagePatterns = [
        {
            name: "Сообщения через Сообщить()",
            pattern: 'Сообщить\\s*\\(\\s*"([^"]+)"',
            type: "info"
        },
        {
            name: "Ошибки через ВызватьИсключение()",
            pattern: 'ВызватьИсключение\\s*\\(\\s*"([^"]+)"',
            type: "error"
        },
        {
            name: "Предупреждения",
            pattern: 'Предупреждение\\s*\\(\\s*"([^"]+)"',
            type: "warning"
        },
        {
            name: "Сообщения пользователю",
            pattern: 'СообщитьПользователю\\s*\\(\\s*"([^"]+)"',
            type: "user"
        },
        {
            name: "Строковые литералы",
            pattern: '"([^"]{10,})"',
            type: "string"
        }
    ];
    
    const allMessages = {};
    
    for (const pattern of messagePatterns) {
        console.log(`   🔍 Ищу: ${pattern.name}...`);
        
        const searchResult = await mcp__ripgrep__search({
            pattern: pattern.pattern,
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true,
            context: 1
        });
        
        // Извлекаем текст сообщений
        const messages = [];
        const lines = searchResult.split('\n');
        
        for (const line of lines) {
            const match = line.match(new RegExp(pattern.pattern));
            if (match && match[1]) {
                const fileMatch = line.match(/^([^:]+):(\\d+):/);
                if (fileMatch) {
                    messages.push({
                        file: fileMatch[1],
                        line: parseInt(fileMatch[2]),
                        text: match[1],
                        fullLine: line
                    });
                }
            }
        }
        
        allMessages[pattern.name] = {
            type: pattern.type,
            count: messages.length,
            messages: messages.slice(0, 20) // Ограничиваем для отчета
        };
    }
    
    // Анализ на дублирование
    const duplicateAnalysis = findDuplicateMessages(allMessages);
    
    // Генерация отчета
    const report = generateMessagesReport(allMessages, duplicateAnalysis);
    
    return {
        messageCategories: allMessages,
        duplicates: duplicateAnalysis,
        report: report
    };
}

function findDuplicateMessages(allMessages) {
    const textCounts = {};
    const duplicates = [];
    
    // Собираем все тексты сообщений
    for (const category of Object.values(allMessages)) {
        for (const message of category.messages) {
            const text = message.text.toLowerCase().trim();
            if (text.length > 5) { // Игнорируем очень короткие
                if (!textCounts[text]) {
                    textCounts[text] = [];
                }
                textCounts[text].push(message);
            }
        }
    }
    
    // Находим дубли
    for (const [text, occurrences] of Object.entries(textCounts)) {
        if (occurrences.length > 1) {
            duplicates.push({
                text: text,
                count: occurrences.length,
                occurrences: occurrences
            });
        }
    }
    
    return duplicates.sort((a, b) => b.count - a.count);
}

function generateMessagesReport(allMessages, duplicates) {
    let report = `# Анализ сообщений пользователю\n\n`;
    report += `*Дата анализа: ${new Date().toLocaleString()}*\n\n`;
    
    // Общая статистика
    const totalMessages = Object.values(allMessages).reduce((sum, cat) => sum + cat.count, 0);
    report += `## 📊 Общая статистика\n\n`;
    report += `- **Всего сообщений:** ${totalMessages}\n`;
    report += `- **Дублирующихся:** ${duplicates.length}\n\n`;
    
    // По категориям
    report += `## 📋 По категориям\n\n`;
    for (const [name, data] of Object.entries(allMessages)) {
        const emoji = {
            'info': 'ℹ️',
            'error': '❌',
            'warning': '⚠️',
            'user': '👤',
            'string': '📝'
        }[data.type] || '📄';
        
        report += `### ${emoji} ${name} (${data.count})\n\n`;
        
        if (data.messages.length > 0) {
            data.messages.slice(0, 5).forEach(msg => {
                const fileName = msg.file.split('/').pop();
                report += `- **${fileName}:${msg.line}** - "${msg.text}"\n`;
            });
            
            if (data.messages.length > 5) {
                report += `\n*...и еще ${data.messages.length - 5} сообщений*\n`;
            }
        }
        
        report += '\n';
    }
    
    // Дублирующиеся сообщения
    if (duplicates.length > 0) {
        report += `## 🔄 Дублирующиеся сообщения\n\n`;
        
        duplicates.slice(0, 10).forEach((dup, index) => {
            report += `### ${index + 1}. "${dup.text}" (${dup.count} раз)\n\n`;
            dup.occurrences.forEach(occ => {
                const fileName = occ.file.split('/').pop();
                report += `- ${fileName}:${occ.line}\n`;
            });
            report += '\n';
        });
        
        report += `## 💡 Рекомендации по дублям\n\n`;
        report += `1. Вынесите часто используемые сообщения в константы\n`;
        report += `2. Создайте общий модуль для стандартных сообщений\n`;
        report += `3. Используйте НСтр() для интернационализации\n\n`;
    }
    
    return report;
}

// Использование
const messagesAnalysis = await findUserMessages("src/projects/configuration/demo-accounting");
```

---

## 🗂️ Поиск по метаданным конфигурации

### Пример 3: Анализ структуры конфигурации
```javascript
// Поиск и анализ объектов метаданных
async function analyzeConfigurationStructure(configPath) {
    console.log("🏗️ Анализирую структуру конфигурации...");
    
    const metadataTypes = [
        { name: "Справочники", pattern: "<Catalog", folder: "Catalogs" },
        { name: "Документы", pattern: "<Document", folder: "Documents" },
        { name: "Перечисления", pattern: "<Enum", folder: "Enums" },
        { name: "Регистры сведений", pattern: "<InformationRegister", folder: "InformationRegisters" },
        { name: "Регистры накопления", pattern: "<AccumulationRegister", folder: "AccumulationRegisters" },
        { name: "Отчеты", pattern: "<Report", folder: "Reports" },
        { name: "Обработки", pattern: "<DataProcessor", folder: "DataProcessors" },
        { name: "Планы видов характеристик", pattern: "<ChartOfCharacteristicTypes", folder: "ChartsOfCharacteristicTypes" },
        { name: "Планы счетов", pattern: "<ChartOfAccounts", folder: "ChartsOfAccounts" }
    ];
    
    const configStructure = {
        summary: {},
        details: {},
        relationships: {}
    };
    
    for (const metaType of metadataTypes) {
        console.log(`   📋 Анализирую: ${metaType.name}...`);
        
        // Поиск объявлений объектов
        const objectsSearch = await mcp__ripgrep__search({
            pattern: `${metaType.pattern}.*name="([^"]+)"`,
            path: configPath,
            filePattern: "*.xml",
            caseSensitive: false,
            showLineNumbers: true
        });
        
        // Извлечение имен объектов
        const objects = [];
        const lines = objectsSearch.split('\n');
        
        for (const line of lines) {
            const match = line.match(/name="([^"]+)"/);
            if (match) {
                objects.push({
                    name: match[1],
                    file: line.split(':')[0],
                    line: parseInt(line.split(':')[1]) || 0
                });
            }
        }
        
        configStructure.summary[metaType.name] = objects.length;
        configStructure.details[metaType.name] = objects;
        
        // Анализ зависимостей (ссылки на другие объекты)
        if (objects.length > 0) {
            configStructure.relationships[metaType.name] = await analyzeObjectRelationships(
                configPath, 
                metaType.folder, 
                objects
            );
        }
    }
    
    // Поиск подсистем
    const subsystemsSearch = await mcp__ripgrep__search({
        pattern: '<Subsystem.*name="([^"]+)"',
        path: configPath,
        filePattern: "*.xml",
        caseSensitive: false
    });
    
    const subsystems = [];
    const subsystemLines = subsystemsSearch.split('\n');
    for (const line of subsystemLines) {
        const match = line.match(/name="([^"]+)"/);
        if (match) {
            subsystems.push(match[1]);
        }
    }
    
    configStructure.summary["Подсистемы"] = subsystems.length;
    configStructure.details["Подсистемы"] = subsystems;
    
    // Генерация отчета
    const report = generateConfigurationReport(configStructure);
    
    return {
        structure: configStructure,
        report: report
    };
}

async function analyzeObjectRelationships(configPath, objectFolder, objects) {
    const relationships = [];
    
    for (const obj of objects.slice(0, 10)) { // Ограничиваем для производительности
        // Поиск ссылок на справочники
        const refsSearch = await mcp__ripgrep__search({
            pattern: `Справочники\\.(\\w+)`,
            path: `${configPath}/${objectFolder}/${obj.name}`,
            filePattern: "*.bsl",
            caseSensitive: false
        });
        
        const refs = [];
        const refMatches = refsSearch.match(/Справочники\\.(\\w+)/g) || [];
        refs.push(...refMatches.map(ref => ({ type: 'Справочник', name: ref.split('.')[1] })));
        
        // Поиск ссылок на документы
        const docRefsSearch = await mcp__ripgrep__search({
            pattern: `Документы\\.(\\w+)`,
            path: `${configPath}/${objectFolder}/${obj.name}`,
            filePattern: "*.bsl",
            caseSensitive: false
        });
        
        const docRefMatches = docRefsSearch.match(/Документы\\.(\\w+)/g) || [];
        refs.push(...docRefMatches.map(ref => ({ type: 'Документ', name: ref.split('.')[1] })));
        
        if (refs.length > 0) {
            relationships.push({
                object: obj.name,
                references: refs
            });
        }
    }
    
    return relationships;
}

function generateConfigurationReport(structure) {
    let report = `# Анализ структуры конфигурации\n\n`;
    report += `*Дата анализа: ${new Date().toLocaleString()}*\n\n`;
    
    // Общая статистика
    report += `## 📊 Общая статистика\n\n`;
    for (const [type, count] of Object.entries(structure.summary)) {
        report += `- **${type}:** ${count}\n`;
    }
    report += '\n';
    
    // Детали по объектам
    report += `## 📋 Объекты конфигурации\n\n`;
    for (const [type, objects] of Object.entries(structure.details)) {
        if (Array.isArray(objects) && objects.length > 0) {
            report += `### ${type}\n\n`;
            
            if (typeof objects[0] === 'string') {
                // Простой список (подсистемы)
                objects.forEach(obj => {
                    report += `- ${obj}\n`;
                });
            } else {
                // Объекты с дополнительной информацией
                objects.slice(0, 10).forEach(obj => {
                    report += `- **${obj.name}**\n`;
                });
                
                if (objects.length > 10) {
                    report += `\n*...и еще ${objects.length - 10} объектов*\n`;
                }
            }
            
            report += '\n';
        }
    }
    
    // Взаимосвязи объектов
    report += `## 🔗 Взаимосвязи объектов\n\n`;
    for (const [type, relationships] of Object.entries(structure.relationships)) {
        if (relationships && relationships.length > 0) {
            report += `### ${type}\n\n`;
            
            relationships.slice(0, 5).forEach(rel => {
                report += `**${rel.object}** ссылается на:\n`;
                rel.references.forEach(ref => {
                    report += `- ${ref.type}: ${ref.name}\n`;
                });
                report += '\n';
            });
        }
    }
    
    return report;
}
```

### Пример 4: Поиск изменений в метаданных
```javascript
// Отслеживание изменений в конфигурации между версиями
async function trackConfigurationChanges(configPath, lastCommitHash) {
    console.log("🔄 Отслеживаю изменения в конфигурации...");
    
    // Получаем список измененных файлов
    const changedFiles = await mcp__serena__execute_shell_command({
        command: `git diff --name-only ${lastCommitHash} HEAD`,
        cwd: configPath
    });
    
    const changes = {
        metadata: [],
        code: [],
        forms: [],
        other: []
    };
    
    const files = changedFiles.stdout.split('\n').filter(f => f.trim());
    
    for (const file of files) {
        const filePath = `${configPath}/${file}`;
        
        if (file.endsWith('.xml')) {
            // Анализ изменений метаданных
            const metadataChange = await analyzeMetadataChange(filePath, lastCommitHash);
            if (metadataChange) {
                changes.metadata.push(metadataChange);
            }
        } else if (file.endsWith('.bsl')) {
            // Анализ изменений кода
            const codeChange = await analyzeCodeChange(filePath, lastCommitHash);
            if (codeChange) {
                changes.code.push(codeChange);
            }
        } else if (file.includes('Form') && file.endsWith('.xml')) {
            // Анализ изменений форм
            const formChange = await analyzeFormChange(filePath, lastCommitHash);
            if (formChange) {
                changes.forms.push(formChange);
            }
        } else {
            changes.other.push({ file: file, type: 'unknown' });
        }
    }
    
    // Генерация отчета об изменениях
    const changeReport = generateChangeReport(changes);
    
    return {
        totalChanges: files.length,
        changes: changes,
        report: changeReport
    };
}

async function analyzeMetadataChange(filePath, lastCommit) {
    // Получаем diff конкретного файла
    const diffResult = await mcp__serena__execute_shell_command({
        command: `git show ${lastCommit}:${filePath} | grep -E "(name=|synonym=)" || echo "not found"`
    });
    
    const currentContent = await mcp__ripgrep__search({
        pattern: '(name=|synonym=)"([^"]+)"',
        path: filePath,
        caseSensitive: false
    });
    
    // Упрощенный анализ изменений
    return {
        file: filePath,
        type: 'metadata',
        hasNameChanges: currentContent.includes('name='),
        hasSynonymChanges: currentContent.includes('synonym='),
        summary: 'Изменения в метаданных обнаружены'
    };
}

async function analyzeCodeChange(filePath, lastCommit) {
    // Поиск ключевых изменений в коде
    const addedFunctions = await mcp__ripgrep__search({
        pattern: '^\\s*(Процедура|Функция)\\s+(\\w+)',
        path: filePath,
        caseSensitive: false,
        showLineNumbers: true
    });
    
    return {
        file: filePath,
        type: 'code',
        functionsCount: (addedFunctions.match(/(Процедура|Функция)/g) || []).length,
        summary: 'Изменения в BSL коде'
    };
}
```

---

## 🔍 Интеграция с анализом кода

### Пример 5: Комплексный анализ качества кода
```javascript
// Интеграция Grep с ✅ BSL Language Server для анализа качества
async function comprehensiveCodeAnalysis(configPath) {
    console.log("🎯 Выполняю комплексный анализ качества кода...");
    
    const analysis = {
        complexity: {},
        patterns: {},
        violations: {},
        metrics: {}
    };
    
    // 1. Анализ сложности функций
    console.log("   📊 Анализирую сложность функций...");
    analysis.complexity = await analyzeFunctionComplexity(configPath);
    
    // 2. Поиск антипаттернов
    console.log("   🚨 Ищу антипаттерны...");
    analysis.patterns = await findAntiPatterns(configPath);
    
    // 3. Проверка соблюдения стандартов
    console.log("   📏 Проверяю соблюдение стандартов...");
    analysis.violations = await checkCodingStandards(configPath);
    
    // 4. Метрики кода
    console.log("   📈 Собираю метрики...");
    analysis.metrics = await collectCodeMetrics(configPath);
    
    // 5. Интеграция с ✅ BSL Language Server
    console.log("   🔧 Запускаю BSL анализ...");
    const bslAnalysis = await runBSLAnalysis(configPath);
    
    // Объединение результатов
    const combinedReport = generateCombinedReport(analysis, bslAnalysis);
    
    return {
        grepAnalysis: analysis,
        bslAnalysis: bslAnalysis,
        combinedReport: combinedReport
    };
}

async function analyzeFunctionComplexity(configPath) {
    // Поиск функций с большой цикломатической сложностью
    const complexFunctions = await mcp__ripgrep__search({
        pattern: '(Процедура|Функция)[\\s\\S]{200,}(КонецПроцедуры|КонецФункции)',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true
    });
    
    // Подсчет вложенности условий
    const nestedConditions = await mcp__ripgrep__search({
        pattern: '\\s+(Если[\\s\\S]*?){3,}',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true
    });
    
    return {
        longFunctions: (complexFunctions.match(/(Процедура|Функция)/g) || []).length,
        deeplyNested: (nestedConditions.match(/Если/g) || []).length,
        details: complexFunctions
    };
}

async function findAntiPatterns(configPath) {
    const antiPatterns = {
        'Пустые исключения': await mcp__ripgrep__search({
            pattern: 'Исключение\\s*;?\\s*КонецПопытки',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        }),
        
        'Использование Выполнить()': await mcp__ripgrep__search({
            pattern: 'Выполнить\\s*\\(',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        }),
        
        'Магические числа': await mcp__ripgrep__search({
            pattern: '\\b[0-9]{3,}\\b',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        }),
        
        'Длинные строки кода': await mcp__ripgrep__search({
            pattern: '.{120,}',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        })
    };
    
    const summary = {};
    for (const [pattern, result] of Object.entries(antiPatterns)) {
        summary[pattern] = (result.match(/\\n/g) || []).length;
    }
    
    return {
        summary: summary,
        details: antiPatterns
    };
}

async function checkCodingStandards(configPath) {
    const standards = {
        'Именование переменных': await mcp__ripgrep__search({
            pattern: 'Перем\\s+[a-z]',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: true
        }),
        
        'Отсутствие комментариев': await mcp__ripgrep__search({
            pattern: '^\\s*(Процедура|Функция)(?!.*//)',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        }),
        
        'Использование НСтр()': await mcp__ripgrep__search({
            pattern: '"[А-Яа-я]{10,}"(?!.*НСтр)',
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        })
    };
    
    const violations = {};
    for (const [standard, result] of Object.entries(standards)) {
        violations[standard] = (result.match(/\\n/g) || []).length;
    }
    
    return violations;
}

async function collectCodeMetrics(configPath) {
    // Подсчет строк кода
    const totalLines = await mcp__ripgrep__search({
        pattern: '.',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    // Подсчет комментариев
    const comments = await mcp__ripgrep__search({
        pattern: '^\\s*//',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    // Подсчет функций и процедур
    const procedures = await mcp__ripgrep__search({
        pattern: '^\\s*(Процедура|Функция)',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    const totalLinesCount = (totalLines.match(/\\n/g) || []).length;
    const commentsCount = (comments.match(/\\n/g) || []).length;
    const proceduresCount = (procedures.match(/(Процедура|Функция)/g) || []).length;
    
    return {
        totalLines: totalLinesCount,
        comments: commentsCount,
        procedures: proceduresCount,
        commentRatio: totalLinesCount > 0 ? (commentsCount / totalLinesCount * 100).toFixed(1) : 0,
        avgLinesPerProcedure: proceduresCount > 0 ? Math.round(totalLinesCount / proceduresCount) : 0
    };
}

async function runBSLAnalysis(configPath) {
    try {
        const bslResult = await mcp__serena__execute_shell_command({
            command: `python -m sonar_integration analyze --src-dir "${configPath}" --quick`,
            timeout: 60000
        });
        
        return {
            success: true,
            output: bslResult.stdout,
            errors: bslResult.stderr
        };
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

function generateCombinedReport(grepAnalysis, bslAnalysis) {
    return `# Комплексный анализ качества кода

## 📊 Метрики кода (Grep анализ)
- **Всего строк:** ${grepAnalysis.metrics.totalLines}
- **Комментариев:** ${grepAnalysis.metrics.comments}
- **Процедур/функций:** ${grepAnalysis.metrics.procedures}
- **Процент комментирования:** ${grepAnalysis.metrics.commentRatio}%
- **Средняя длина процедуры:** ${grepAnalysis.metrics.avgLinesPerProcedure} строк

## 🚨 Найденные антипаттерны
${Object.entries(grepAnalysis.patterns.summary).map(([pattern, count]) => 
    `- **${pattern}:** ${count} вхождений`
).join('\n')}

## 📏 Нарушения стандартов кодирования
${Object.entries(grepAnalysis.violations).map(([standard, count]) => 
    `- **${standard}:** ${count} нарушений`
).join('\n')}

## 🔧 ✅ BSL Language Server анализ
${bslAnalysis.success ? 
    `✅ Анализ выполнен успешно\n\`\`\`\n${bslAnalysis.output}\n\`\`\`` :
    `❌ Ошибка анализа: ${bslAnalysis.error}`
}

## 🎯 Общие рекомендации
1. Увеличить процент комментирования до 15-20%
2. Устранить критические антипаттерны
3. Разбить длинные функции на более мелкие
4. Унифицировать стиль именования

---
*Анализ выполнен: ${new Date().toLocaleString()}*
`;
}
```

---

## 📖 Поиск в документации и комментариях

### Пример 6: Анализ качества документации
```javascript
// Анализ качества комментариев и документации в коде
async function analyzeDocumentationQuality(configPath) {
    console.log("📚 Анализирую качество документации...");
    
    const docAnalysis = {
        comments: {},
        documentation: {},
        quality: {}
    };
    
    // 1. Анализ комментариев
    docAnalysis.comments = await analyzeComments(configPath);
    
    // 2. Анализ документирования функций
    docAnalysis.documentation = await analyzeFunctionDocumentation(configPath);
    
    // 3. Оценка качества
    docAnalysis.quality = evaluateDocumentationQuality(docAnalysis);
    
    // Генерация отчета
    const report = generateDocumentationReport(docAnalysis);
    
    return {
        analysis: docAnalysis,
        report: report
    };
}

async function analyzeComments(configPath) {
    // Однострочные комментарии
    const singleLineComments = await mcp__ripgrep__search({
        pattern: '^\\s*//(.+)$',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true
    });
    
    // Блочные комментарии
    const blockComments = await mcp__ripgrep__search({
        pattern: '^\\s*//.*\\n(\\s*//.*\\n){2,}',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        multiline: true
    });
    
    // TODO комментарии
    const todoComments = await mcp__ripgrep__search({
        pattern: '//.*(?:TODO|FIXME|XXX|HACK)',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    // Анализ содержания комментариев
    const commentLines = singleLineComments.split('\n').filter(line => line.includes('//'));
    const qualityMetrics = {
        total: commentLines.length,
        meaningful: 0,
        short: 0,
        todos: (todoComments.match(/TODO|FIXME|XXX|HACK/g) || []).length,
        avgLength: 0
    };
    
    let totalLength = 0;
    for (const line of commentLines) {
        const commentMatch = line.match(/\\/\\/\\s*(.+)$/);
        if (commentMatch) {
            const commentText = commentMatch[1].trim();
            totalLength += commentText.length;
            
            if (commentText.length > 20 && commentText.length < 100) {
                qualityMetrics.meaningful++;
            } else if (commentText.length <= 10) {
                qualityMetrics.short++;
            }
        }
    }
    
    qualityMetrics.avgLength = qualityMetrics.total > 0 ? 
        Math.round(totalLength / qualityMetrics.total) : 0;
    
    return {
        singleLine: qualityMetrics,
        blocks: (blockComments.match(/\\/\\//g) || []).length,
        todos: qualityMetrics.todos,
        rawData: {
            singleLineComments,
            blockComments,
            todoComments
        }
    };
}

async function analyzeFunctionDocumentation(configPath) {
    // Поиск всех функций и процедур
    const allFunctions = await mcp__ripgrep__search({
        pattern: '^\\s*(Процедура|Функция)\\s+(\\w+)',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true,
        context: 3
    });
    
    // Поиск документированных функций (с комментарием перед объявлением)
    const documentedFunctions = await mcp__ripgrep__search({
        pattern: '^\\s*//.*\\n\\s*(Процедура|Функция)',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        multiline: true
    });
    
    // Экспортные функции
    const exportFunctions = await mcp__ripgrep__search({
        pattern: '(Процедура|Функция).*Экспорт',
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    const totalFunctions = (allFunctions.match(/(Процедура|Функция)/g) || []).length;
    const documentedCount = (documentedFunctions.match(/(Процедура|Функция)/g) || []).length;
    const exportCount = (exportFunctions.match(/(Процедура|Функция)/g) || []).length;
    
    return {
        total: totalFunctions,
        documented: documentedCount,
        export: exportCount,
        documentationRate: totalFunctions > 0 ? 
            ((documentedCount / totalFunctions) * 100).toFixed(1) : 0,
        exportDocumentationRate: exportCount > 0 ? 
            ((documentedCount / exportCount) * 100).toFixed(1) : 0
    };
}

function evaluateDocumentationQuality(docAnalysis) {
    const scores = {
        commentQuantity: 0,    // Количество комментариев
        commentQuality: 0,     // Качество комментариев  
        functionDocs: 0,       // Документирование функций
        maintenance: 0         // Поддержка (TODO и т.д.)
    };
    
    // Оценка количества комментариев (0-25 баллов)
    const commentRatio = docAnalysis.comments.singleLine.total / 100; // примерная оценка
    scores.commentQuantity = Math.min(25, commentRatio * 25);
    
    // Оценка качества комментариев (0-25 баллов)
    const meaningfulRatio = docAnalysis.comments.singleLine.meaningful / 
                           Math.max(1, docAnalysis.comments.singleLine.total);
    scores.commentQuality = meaningfulRatio * 25;
    
    // Оценка документирования функций (0-30 баллов)
    scores.functionDocs = (docAnalysis.documentation.documentationRate / 100) * 30;
    
    // Оценка поддержки (0-20 баллов)
    // Меньше TODO - лучше
    const todoRatio = docAnalysis.comments.todos / 
                     Math.max(1, docAnalysis.comments.singleLine.total);
    scores.maintenance = Math.max(0, 20 - (todoRatio * 20));
    
    const totalScore = Object.values(scores).reduce((sum, score) => sum + score, 0);
    
    return {
        scores: scores,
        totalScore: Math.round(totalScore),
        grade: getDocumentationGrade(totalScore)
    };
}

function getDocumentationGrade(score) {
    if (score >= 85) return 'A (Отличное)';
    if (score >= 70) return 'B (Хорошее)';
    if (score >= 55) return 'C (Удовлетворительное)';
    if (score >= 40) return 'D (Неудовлетворительное)';
    return 'F (Критическое)';
}

function generateDocumentationReport(docAnalysis) {
    return `# Анализ качества документации

## 📊 Общая оценка: ${docAnalysis.quality.totalScore}/100 (${docAnalysis.quality.grade})

## 💬 Анализ комментариев
- **Всего комментариев:** ${docAnalysis.comments.singleLine.total}
- **Содержательных:** ${docAnalysis.comments.singleLine.meaningful}
- **Коротких (≤10 символов):** ${docAnalysis.comments.singleLine.short}
- **Средняя длина:** ${docAnalysis.comments.singleLine.avgLength} символов
- **TODO/FIXME:** ${docAnalysis.comments.todos}

## 📋 Документирование функций
- **Всего функций:** ${docAnalysis.documentation.total}
- **Документированных:** ${docAnalysis.documentation.documented}
- **Экспортных:** ${docAnalysis.documentation.export}
- **Процент документирования:** ${docAnalysis.documentation.documentationRate}%
- **Документирование экспортных:** ${docAnalysis.documentation.exportDocumentationRate}%

## 🎯 Детализация оценки
- **Количество комментариев:** ${Math.round(docAnalysis.quality.scores.commentQuantity)}/25
- **Качество комментариев:** ${Math.round(docAnalysis.quality.scores.commentQuality)}/25
- **Документирование функций:** ${Math.round(docAnalysis.quality.scores.functionDocs)}/30
- **Поддержка кода:** ${Math.round(docAnalysis.quality.scores.maintenance)}/20

## 💡 Рекомендации по улучшению
${docAnalysis.quality.scores.commentQuantity < 15 ? '- Увеличить количество комментариев\n' : ''}
${docAnalysis.quality.scores.commentQuality < 15 ? '- Улучшить качество комментариев (избегать слишком коротких)\n' : ''}
${docAnalysis.quality.scores.functionDocs < 20 ? '- Добавить документацию к функциям, особенно экспортным\n' : ''}
${docAnalysis.comments.todos > 10 ? '- Разобрать накопившиеся TODO комментарии\n' : ''}

---
*Анализ выполнен: ${new Date().toLocaleString()}*
`;
}

// Использование
const docQualityAnalysis = await analyzeDocumentationQuality("src/projects/configuration/demo-accounting");
```

---

## 🤖 Автоматизация рутинных задач поиска

### Пример 7: Автоматический мониторинг кодовой базы
```javascript
// Автоматический мониторинг изменений в кодовой базе
class CodebaseMonitor {
    constructor(configPath) {
        this.configPath = configPath;
        this.lastCheck = new Date();
        this.alerts = [];
    }
    
    async monitorCodeQuality() {
        console.log("🔍 Запускаю мониторинг качества кода...");
        
        const issues = [];
        
        // Проверка на новые антипаттерны
        const antiPatterns = await this.checkForAntiPatterns();
        if (antiPatterns.length > 0) {
            issues.push({
                type: 'antipatterns',
                severity: 'high',
                count: antiPatterns.length,
                details: antiPatterns
            });
        }
        
        // Проверка на длинные функции
        const longFunctions = await this.checkForLongFunctions();
        if (longFunctions.length > 0) {
            issues.push({
                type: 'complexity',
                severity: 'medium',
                count: longFunctions.length,
                details: longFunctions
            });
        }
        
        // Проверка на увеличение TODO
        const todoCount = await this.checkTodoIncrease();
        if (todoCount.increased) {
            issues.push({
                type: 'maintenance',
                severity: 'low',
                count: todoCount.new,
                details: 'Увеличилось количество TODO комментариев'
            });
        }
        
        // Генерация алертов
        if (issues.length > 0) {
            await this.generateAlert(issues);
        }
        
        return {
            timestamp: new Date(),
            issuesFound: issues.length,
            issues: issues
        };
    }
    
    async checkForAntiPatterns() {
        const patterns = [
            'Выполнить\\s*\\(',
            'Исключение\\s*;?\\s*КонецПопытки',
            'Сообщить\\s*\\(\\s*""\\s*\\)'
        ];
        
        const found = [];
        
        for (const pattern of patterns) {
            const result = await mcp__ripgrep__search({
                pattern: pattern,
                path: this.configPath,
                filePattern: "*.bsl",
                caseSensitive: false,
                showLineNumbers: true
            });
            
            if (result.trim()) {
                const matches = result.split('\n').filter(line => 
                    line.includes('.bsl:') && /\\d+:/.test(line)
                );
                
                if (matches.length > 0) {
                    found.push({
                        pattern: pattern,
                        matches: matches.length,
                        locations: matches.slice(0, 5)
                    });
                }
            }
        }
        
        return found;
    }
    
    async checkForLongFunctions() {
        // Поиск функций длиннее 100 строк
        const longFunctions = await mcp__ripgrep__search({
            pattern: '(Процедура|Функция)[\\s\\S]{2025,}(КонецПроцедуры|КонецФункции)',
            path: this.configPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true
        });
        
        const functions = [];
        const matches = longFunctions.match(/(Процедура|Функция)\\s+(\\w+)/g) || [];
        
        return matches.map(match => ({
            name: match.split(/\\s+/)[1],
            type: match.split(/\\s+/)[0]
        }));
    }
    
    async checkTodoIncrease() {
        const currentTodos = await mcp__ripgrep__search({
            pattern: '//.*(?:TODO|FIXME|XXX|HACK)',
            path: this.configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        });
        
        const currentCount = (currentTodos.match(/TODO|FIXME|XXX|HACK/g) || []).length;
        
        // Сравнение с предыдущей проверкой (упрощенно)
        const previousCount = this.previousTodoCount || 0;
        this.previousTodoCount = currentCount;
        
        return {
            current: currentCount,
            previous: previousCount,
            increased: currentCount > previousCount,
            new: Math.max(0, currentCount - previousCount)
        };
    }
    
    async generateAlert(issues) {
        const alert = {
            timestamp: new Date(),
            severity: this.getHighestSeverity(issues),
            summary: `Обнаружено ${issues.length} типов проблем в коде`,
            issues: issues
        };
        
        this.alerts.push(alert);
        
        // Сохранение алерта
        const alertPath = `alerts/code-quality-alert-${Date.now()}.json`;
        await mcp__filesystem__write_file({
            path: alertPath,
            content: JSON.stringify(alert, null, 2)
        });
        
        // Отправка уведомления (заглушка)
        console.log(`🚨 АЛЕРТ: ${alert.summary}`);
        
        return alertPath;
    }
    
    getHighestSeverity(issues) {
        const severityLevels = { 'high': 3, 'medium': 2, 'low': 1 };
        let maxSeverity = 'low';
        
        for (const issue of issues) {
            if (severityLevels[issue.severity] > severityLevels[maxSeverity]) {
                maxSeverity = issue.severity;
            }
        }
        
        return maxSeverity;
    }
    
    async generateMonitoringReport() {
        const report = `# Отчет мониторинга кодовой базы

## 📊 Статистика алертов
- **Всего алертов:** ${this.alerts.length}
- **Последняя проверка:** ${this.lastCheck.toLocaleString()}

## 🚨 Последние проблемы
${this.alerts.slice(-5).map(alert => 
    `- **${alert.timestamp.toLocaleString()}** (${alert.severity}): ${alert.summary}`
).join('\n')}

## 📈 Тренды
- **Антипаттерны:** стабильно
- **Сложность:** увеличивается  
- **TODO:** ${this.previousTodoCount || 0} активных

---
*Сгенерировано: ${new Date().toLocaleString()}*
`;
        
        return report;
    }
}

// Использование
const monitor = new CodebaseMonitor("src/projects/configuration/demo-accounting");

// Разовая проверка
const monitoringResult = await monitor.monitorCodeQuality();

// Периодический мониторинг (каждые 30 минут)
setInterval(async () => {
    await monitor.monitorCodeQuality();
}, 30 * 60 * 1000);
```

---

## 🛠️ Настройка и конфигурация

### Конфигурация в claude_desktop_config.json:
```json
{
  "mcpServers": {
    "grep": {
      "command": "npx",
      "args": ["-y", "grep-mcp"],
      "env": {
        "GREP_MAX_RESULTS": "1000",
        "GREP_TIMEOUT": "30000",
        "GREP_DEFAULT_CONTEXT": "2"
      }
    }
  }
}
```

### Настройки поиска:
```javascript
// Конфигурация поиска для различных задач
const searchConfigs = {
    quickSearch: {
        maxResults: 100,
        timeout: 5000,
        context: 1
    },
    
    deepAnalysis: {
        maxResults: 5000,
        timeout: 60000,
        context: 5
    },
    
    monitoring: {
        maxResults: 10000,
        timeout: 30000,
        context: 2,
        showLineNumbers: true
    }
};
```

---

## ⚠️ Важные замечания

1. **Производительность**: Grep работает быстрее ripgrep только на малых файлах
2. **Регулярные выражения**: Поддерживает POSIX regex (отличается от ripgrep)
3. **Кодировка**: Может иметь проблемы с русскими символами в BSL
4. **Контекст**: Ограниченные возможности контекстного поиска
5. **Большие файлы**: Может быть медленным на больших конфигурациях

---

## 📚 Дополнительные ресурсы

- [Документация GNU Grep](https://www.gnu.org/software/grep/manual/)
- [Регулярные выражения POSIX](https://en.wikipedia.org/wiki/Regular_expression)
- [Альтернатива: Ripgrep MCP](./Ripgrep-MCP-Examples.md)

---

*Последнее обновление: ${new Date().toLocaleDateString()}*
*Версия документа: 1.0.0*