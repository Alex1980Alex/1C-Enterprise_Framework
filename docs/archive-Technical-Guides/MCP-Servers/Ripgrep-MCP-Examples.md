# 🔍 Ripgrep MCP - Практические примеры для 1С

[← К справочнику MCP](../MCP-Complete-Reference.md) | [К оглавлению](../README.md)

## 📚 Оглавление
- [Поиск в конфигурациях 1С](#поиск-в-конфигурациях-1с)
- [Анализ BSL кода](#анализ-bsl-кода)
- [Поиск зависимостей и дублирующегося кода](#поиск-зависимостей-и-дублирующегося-кода)
- [Code Review и анализ качества](#code-review-и-анализ-качества)
- [Рефакторинг и миграция кода](#рефакторинг-и-миграция-кода)

---

## 🏗️ Поиск в конфигурациях 1С

### Пример 1: Поиск использования справочников
```javascript
// Поиск всех мест использования конкретного справочника
async function findCatalogUsage(catalogName, configPath) {
    const searchPattern = `Справочники\\.${catalogName}`;
    
    const result = await mcp__ripgrep__search({
        pattern: searchPattern,
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true,
        context: 2
    });
    
    // Анализируем результаты
    const usageAnalysis = {
        totalFiles: 0,
        totalMatches: 0,
        usageTypes: {
            creation: 0,      // СоздатьЭлемент(), СоздатьГруппу()
            selection: 0,     // НайтиПоКоду(), НайтиПоНаименованию()
            comparison: 0,    // СсылочныеПоля = Справочники.ХХХ
            queries: 0,       // В текстах запросов
            forms: 0          // В формах объектов
        },
        files: []
    };
    
    const lines = result.split('\n');
    let currentFile = '';
    
    for (const line of lines) {
        if (line.includes('.bsl:')) {
            currentFile = line.split(':')[0];
            if (!usageAnalysis.files.includes(currentFile)) {
                usageAnalysis.files.push(currentFile);
                usageAnalysis.totalFiles++;
            }
        }
        
        if (line.includes(searchPattern)) {
            usageAnalysis.totalMatches++;
            
            // Анализируем тип использования
            if (line.includes('Создать')) {
                usageAnalysis.usageTypes.creation++;
            } else if (line.includes('НайтиПо')) {
                usageAnalysis.usageTypes.selection++;
            } else if (line.includes('ВЫБРАТЬ') || line.includes('ИЗ')) {
                usageAnalysis.usageTypes.queries++;
            } else if (line.includes('=') || line.includes('Ссылка')) {
                usageAnalysis.usageTypes.comparison++;
            }
        }
    }
    
    // Генерируем отчет
    const report = `
# Анализ использования справочника "${catalogName}"

## 📊 Статистика
- **Всего файлов:** ${usageAnalysis.totalFiles}
- **Всего вхождений:** ${usageAnalysis.totalMatches}
- **Дата анализа:** ${new Date().toLocaleString()}

## 🔍 Типы использования
- **Создание объектов:** ${usageAnalysis.usageTypes.creation}
- **Поиск элементов:** ${usageAnalysis.usageTypes.selection}
- **Сравнения и присвоения:** ${usageAnalysis.usageTypes.comparison}
- **Запросы к БД:** ${usageAnalysis.usageTypes.queries}

## 📝 Детальные результаты
\`\`\`
${result}
\`\`\`

## 🎯 Рекомендации по рефакторингу
${usageAnalysis.totalMatches > 50 ? 
  '⚠️ Высокая связанность - рассмотрите возможность декомпозиции' : 
  '✅ Нормальный уровень использования'}

## 📂 Затронутые файлы
${usageAnalysis.files.map(file => `- ${file}`).join('\n')}
`;
    
    // Сохраняем отчет
    const reportPath = `reports/catalog-usage-${catalogName}-${Date.now()}.md`;
    await mcp__filesystem__write_file({
        path: reportPath,
        content: report
    });
    
    return {
        analysis: usageAnalysis,
        report: reportPath,
        rawResults: result
    };
}

// Использование
const analysis = await findCatalogUsage("Номенклатура", "src/projects/configuration/demo-accounting");
console.log(`✅ Найдено ${analysis.analysis.totalMatches} использований в ${analysis.analysis.totalFiles} файлах`);
```

### Пример 2: Анализ регистров и их использования
```javascript
// Поиск работы с регистрами накопления и сведений
async function analyzeRegistersUsage(configPath) {
    const registerTypes = [
        { pattern: 'РегистрыНакопления\\.\\w+', type: 'AccumulationRegister' },
        { pattern: 'РегистрыСведений\\.\\w+', type: 'InformationRegister' },
        { pattern: 'РегистрыБухгалтерии\\.\\w+', type: 'AccountingRegister' }
    ];
    
    const analysisResults = {};
    
    for (const regType of registerTypes) {
        console.log(`🔍 Анализирую ${regType.type}...`);
        
        const result = await mcp__ripgrep__search({
            pattern: regType.pattern,
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true,
            context: 1
        });
        
        // Парсим результаты для поиска конкретных регистров
        const registers = new Set();
        const lines = result.split('\n');
        
        for (const line of lines) {
            const match = line.match(new RegExp(regType.pattern));
            if (match) {
                registers.add(match[0]);
            }
        }
        
        analysisResults[regType.type] = {
            totalUsages: (result.match(new RegExp(regType.pattern, 'g')) || []).length,
            uniqueRegisters: Array.from(registers),
            rawResults: result
        };
    }
    
    // Генерация сводного отчета
    let report = `# Анализ использования регистров\n\n`;
    report += `*Дата анализа: ${new Date().toLocaleString()}*\n\n`;
    
    for (const [type, data] of Object.entries(analysisResults)) {
        report += `## ${type}\n\n`;
        report += `- **Всего использований:** ${data.totalUsages}\n`;
        report += `- **Уникальных регистров:** ${data.uniqueRegisters.length}\n\n`;
        
        if (data.uniqueRegisters.length > 0) {
            report += `### Найденные регистры:\n`;
            data.uniqueRegisters.forEach(reg => {
                report += `- \`${reg}\`\n`;
            });
            report += '\n';
        }
    }
    
    return {
        results: analysisResults,
        report: report
    };
}

// Использование
const registersAnalysis = await analyzeRegistersUsage("src/projects/configuration/demo-accounting");
```

---

## 📋 Анализ BSL кода

### Пример 3: Поиск проблемных конструкций
```javascript
// Поиск анти-паттернов и проблемных конструкций в BSL
async function findCodeSmells(configPath) {
    const codeSmells = [
        {
            name: "Пустые блоки исключений",
            pattern: "Исключение\\s*;?\\s*КонецПопытки",
            severity: "HIGH",
            description: "Пустая обработка исключений скрывает ошибки"
        },
        {
            name: "Использование Выполнить()",
            pattern: "Выполнить\\s*\\(",
            severity: "CRITICAL", 
            description: "Динамическое выполнение кода - потенциальная уязвимость"
        },
        {
            name: "Длинные запросы в коде",
            pattern: "Запрос\\.Текст\\s*=\\s*\"[\\s\\S]{500,}\"",
            severity: "MEDIUM",
            description: "Очень длинный запрос в коде - рассмотрите вынос в отдельный метод"
        },
        {
            name: "Много вложенных условий",
            pattern: "(Если[\\s\\S]*?){4,}КонецЕсли",
            severity: "MEDIUM",
            description: "Глубокая вложенность условий снижает читаемость"
        },
        {
            name: "Использование устаревших функций",
            pattern: "(ПолучитьURL|ПоместитьФайл|ИмяВременногоФайла)\\s*\\(",
            severity: "LOW",
            description: "Использование устаревших функций API"
        }
    ];
    
    const results = {};
    
    for (const smell of codeSmells) {
        console.log(`🔍 Ищу: ${smell.name}...`);
        
        const searchResult = await mcp__ripgrep__search({
            pattern: smell.pattern,
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true,
            context: 3
        });
        
        const matches = searchResult.split('\n').filter(line => 
            line.includes('.bsl:') && /\\d+:/.test(line)
        ).length;
        
        results[smell.name] = {
            severity: smell.severity,
            description: smell.description,
            matches: matches,
            details: searchResult
        };
    }
    
    // Генерация отчета о качестве
    let qualityReport = `# Отчет о качестве BSL кода\n\n`;
    qualityReport += `*Анализ выполнен: ${new Date().toLocaleString()}*\n\n`;
    
    // Сортируем по критичности
    const severityOrder = { 'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0 };
    const sortedResults = Object.entries(results).sort(([,a], [,b]) => 
        severityOrder[b.severity] - severityOrder[a.severity]
    );
    
    let totalIssues = 0;
    
    for (const [name, data] of sortedResults) {
        if (data.matches > 0) {
            totalIssues += data.matches;
            
            const emoji = {
                'CRITICAL': '🚨',
                'HIGH': '⚠️',
                'MEDIUM': '⚡',
                'LOW': '💡'
            }[data.severity];
            
            qualityReport += `## ${emoji} ${name}\n\n`;
            qualityReport += `- **Критичность:** ${data.severity}\n`;
            qualityReport += `- **Найдено случаев:** ${data.matches}\n`;
            qualityReport += `- **Описание:** ${data.description}\n\n`;
            
            if (data.matches > 0) {
                qualityReport += `### Детали:\n\`\`\`\n${data.details}\n\`\`\`\n\n`;
            }
        }
    }
    
    // Добавляем общую статистику
    qualityReport = `## 📊 Общая статистика\n\n` +
                   `- **Всего проблем:** ${totalIssues}\n` +
                   `- **Критических:** ${results['Использование Выполнить()']?.matches || 0}\n` +
                   `- **Высокой важности:** ${results['Пустые блоки исключений']?.matches || 0}\n\n` +
                   qualityReport;
    
    return {
        totalIssues: totalIssues,
        results: results,
        report: qualityReport
    };
}

// Использование
const qualityAnalysis = await findCodeSmells("src/projects/configuration/demo-accounting");
console.log(`🔍 Обнаружено ${qualityAnalysis.totalIssues} потенциальных проблем в коде`);
```

### Пример 4: Поиск неиспользуемого кода
```javascript
// Поиск неиспользуемых процедур и функций
async function findUnusedCode(configPath) {
    console.log("🔍 Сканирую процедуры и функции...");
    
    // Находим все объявления процедур и функций
    const declarationsResult = await mcp__ripgrep__search({
        pattern: "^\\s*(Процедура|Функция)\\s+(\\w+)",
        path: configPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true
    });
    
    // Парсим объявления
    const declarations = [];
    const lines = declarationsResult.split('\n');
    
    for (const line of lines) {
        const match = line.match(/^([^:]+):(\\d+):\\s*(Процедура|Функция)\\s+(\\w+)/);
        if (match) {
            declarations.push({
                file: match[1],
                line: parseInt(match[2]),
                type: match[3],
                name: match[4]
            });
        }
    }
    
    console.log(`📋 Найдено ${declarations.length} процедур и функций`);
    
    // Проверяем использование каждой процедуры/функции
    const unusedCode = [];
    
    for (const decl of declarations) {
        // Ищем вызовы (исключая объявление)
        const usageResult = await mcp__ripgrep__search({
            pattern: `\\b${decl.name}\\s*\\(`,
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false
        });
        
        const usageLines = usageResult.split('\n').filter(line => {
            // Исключаем строки с объявлениями
            return line.includes(decl.name) && 
                   !line.includes(`${decl.type} ${decl.name}`) &&
                   line.trim() !== '';
        });
        
        // Если использований нет или только в том же файле (локальные функции)
        if (usageLines.length === 0) {
            unusedCode.push({
                ...decl,
                usageCount: 0,
                isExported: false // TODO: определить по ключевому слову Экспорт
            });
        } else if (usageLines.length === 1 && usageLines[0].includes(decl.file)) {
            // Возможно локальная неиспользуемая функция
            unusedCode.push({
                ...decl,
                usageCount: 1,
                localOnly: true
            });
        }
    }
    
    // Генерация отчета
    let report = `# Анализ неиспользуемого кода\n\n`;
    report += `*Анализ выполнен: ${new Date().toLocaleString()}*\n\n`;
    report += `## 📊 Статистика\n\n`;
    report += `- **Всего процедур/функций:** ${declarations.length}\n`;
    report += `- **Неиспользуемых:** ${unusedCode.length}\n`;
    report += `- **Процент очистки:** ${((unusedCode.length / declarations.length) * 100).toFixed(1)}%\n\n`;
    
    if (unusedCode.length > 0) {
        report += `## 🗑️ Неиспользуемый код\n\n`;
        
        // Группируем по файлам
        const byFiles = {};
        unusedCode.forEach(code => {
            if (!byFiles[code.file]) byFiles[code.file] = [];
            byFiles[code.file].push(code);
        });
        
        for (const [file, codes] of Object.entries(byFiles)) {
            report += `### ${file}\n\n`;
            codes.forEach(code => {
                const warning = code.localOnly ? ' (только локальное использование)' : '';
                report += `- **${code.type}** \`${code.name}\` (строка ${code.line})${warning}\n`;
            });
            report += '\n';
        }
        
        report += `## 🔄 Рекомендации по очистке\n\n`;
        report += `1. Проверьте, не используются ли функции через \`Выполнить()\`\n`;
        report += `2. Убедитесь, что функции не вызываются из других конфигураций\n`;
        report += `3. Проверьте использование в формах и отчетах\n`;
        report += `4. Удаляйте код постепенно, с тестированием\n\n`;
    }
    
    return {
        totalDeclarations: declarations.length,
        unusedCount: unusedCode.length,
        unusedCode: unusedCode,
        report: report
    };
}

// Использование
const unusedAnalysis = await findUnusedCode("src/projects/configuration/demo-accounting");
```

---

## 🔗 Поиск зависимостей и дублирующегося кода

### Пример 5: Анализ зависимостей между модулями
```javascript
// Построение карты зависимостей между модулями
async function buildDependencyMap(configPath) {
    console.log("🗺️ Строю карту зависимостей...");
    
    // Находим все вызовы методов других модулей
    const dependencyPatterns = [
        "\\w+\\.\\w+\\s*\\(",  // Модуль.Метод()
        "Справочники\\.\\w+",  // Справочники.ХХХ
        "Документы\\.\\w+",    // Документы.ХХХ
        "ОбщиеМодули\\.\\w+"   // ОбщиеМодули.ХХХ
    ];
    
    const dependencies = {};
    
    // Получаем список всех BSL файлов
    const filesResult = await mcp__ripgrep__list_files({
        path: configPath,
        filePattern: "*.bsl"
    });
    
    const bslFiles = filesResult.split('\n').filter(f => f.trim());
    
    for (const file of bslFiles) {
        dependencies[file] = new Set();
        
        for (const pattern of dependencyPatterns) {
            const result = await mcp__ripgrep__search({
                pattern: pattern,
                path: file,
                caseSensitive: false
            });
            
            const matches = result.match(new RegExp(pattern, 'g')) || [];
            matches.forEach(match => {
                dependencies[file].add(match);
            });
        }
        
        // Конвертируем Set в Array для дальнейшей обработки
        dependencies[file] = Array.from(dependencies[file]);
    }
    
    // Анализируем циклические зависимости
    const cycles = findCyclicDependencies(dependencies);
    
    // Генерируем отчет
    let report = `# Карта зависимостей модулей\n\n`;
    report += `*Построена: ${new Date().toLocaleString()}*\n\n`;
    
    // Статистика
    const totalDeps = Object.values(dependencies)
        .reduce((sum, deps) => sum + deps.length, 0);
    
    report += `## 📊 Общая статистика\n\n`;
    report += `- **Всего модулей:** ${bslFiles.length}\n`;
    report += `- **Всего зависимостей:** ${totalDeps}\n`;
    report += `- **Среднее на модуль:** ${(totalDeps / bslFiles.length).toFixed(1)}\n`;
    report += `- **Циклических зависимостей:** ${cycles.length}\n\n`;
    
    // Топ модулей по количеству зависимостей
    const sortedByDeps = Object.entries(dependencies)
        .sort(([,a], [,b]) => b.length - a.length)
        .slice(0, 10);
    
    report += `## 🔝 Модули с наибольшим количеством зависимостей\n\n`;
    sortedByDeps.forEach(([file, deps]) => {
        const fileName = file.split('/').pop();
        report += `- **${fileName}**: ${deps.length} зависимостей\n`;
    });
    report += '\n';
    
    // Циклические зависимости
    if (cycles.length > 0) {
        report += `## ⚠️ Циклические зависимости\n\n`;
        cycles.forEach((cycle, index) => {
            report += `### Цикл ${index + 1}\n`;
            report += cycle.map(file => `- ${file.split('/').pop()}`).join('\n');
            report += '\n\n';
        });
    }
    
    // Граф в формате Mermaid
    report += `## 📈 Граф зависимостей (Mermaid)\n\n`;
    report += generateMermaidDiagram(dependencies);
    
    return {
        dependencies: dependencies,
        cycles: cycles,
        report: report,
        stats: {
            totalModules: bslFiles.length,
            totalDependencies: totalDeps,
            averageDependencies: totalDeps / bslFiles.length,
            cyclicDependencies: cycles.length
        }
    };
}

function findCyclicDependencies(dependencies) {
    // Упрощенный алгоритм поиска циклов
    const cycles = [];
    const visited = new Set();
    const recursionStack = new Set();
    
    function dfs(node, path) {
        if (recursionStack.has(node)) {
            // Найден цикл
            const cycleStart = path.indexOf(node);
            cycles.push(path.slice(cycleStart));
            return;
        }
        
        if (visited.has(node)) return;
        
        visited.add(node);
        recursionStack.add(node);
        path.push(node);
        
        const deps = dependencies[node] || [];
        for (const dep of deps) {
            // Ищем соответствующий файл модуля
            const depFile = Object.keys(dependencies).find(file => 
                file.includes(dep.replace(/\\./g, '/'))
            );
            
            if (depFile) {
                dfs(depFile, [...path]);
            }
        }
        
        recursionStack.delete(node);
        path.pop();
    }
    
    for (const file of Object.keys(dependencies)) {
        if (!visited.has(file)) {
            dfs(file, []);
        }
    }
    
    return cycles;
}

function generateMermaidDiagram(dependencies) {
    let diagram = '```mermaid\ngraph TD\n';
    
    const processedPairs = new Set();
    
    for (const [file, deps] of Object.entries(dependencies)) {
        const shortName = file.split('/').pop().replace('.bsl', '');
        
        for (const dep of deps.slice(0, 5)) { // Ограничиваем для читаемости
            const depShort = dep.replace(/\\./g, '_');
            const pair = `${shortName}_${depShort}`;
            
            if (!processedPairs.has(pair)) {
                diagram += `    ${shortName} --> ${depShort}\n`;
                processedPairs.add(pair);
            }
        }
    }
    
    diagram += '```\n';
    return diagram;
}
```

### Пример 6: Поиск дублирующегося кода
```javascript
// Поиск похожих блоков кода
async function findDuplicatedCode(configPath) {
    console.log("🔍 Ищу дублирующийся код...");
    
    // Паттерны для поиска потенциальных дублей
    const duplicatePatterns = [
        {
            name: "Похожие запросы",
            pattern: "ВЫБРАТЬ[\\s\\S]{50,200}ИЗ[\\s\\S]{20,100}ГДЕ",
            minLength: 100
        },
        {
            name: "Похожие циклы",
            pattern: "Для Каждого[\\s\\S]{20,150}КонецЦикла",
            minLength: 50
        },
        {
            name: "Похожие условия",
            pattern: "Если[\\s\\S]{30,200}Тогда[\\s\\S]{30,200}КонецЕсли",
            minLength: 80
        },
        {
            name: "Инициализация структур",
            pattern: "Структура\\s*=\\s*Новый\\s*Структура[\\s\\S]{20,150};",
            minLength: 40
        }
    ];
    
    const duplicates = {};
    
    for (const patternInfo of duplicatePatterns) {
        console.log(`   🔍 Ищу: ${patternInfo.name}...`);
        
        const result = await mcp__ripgrep__search({
            pattern: patternInfo.pattern,
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true,
            context: 0
        });
        
        // Парсим найденные блоки
        const blocks = [];
        const lines = result.split('\n');
        
        for (const line of lines) {
            const match = line.match(/^([^:]+):(\\d+):(.+)$/);
            if (match) {
                const block = match[3].trim();
                if (block.length >= patternInfo.minLength) {
                    blocks.push({
                        file: match[1],
                        line: parseInt(match[2]),
                        code: block,
                        normalizedCode: normalizeCode(block)
                    });
                }
            }
        }
        
        // Ищем похожие блоки
        const similarBlocks = findSimilarBlocks(blocks);
        
        if (similarBlocks.length > 0) {
            duplicates[patternInfo.name] = similarBlocks;
        }
    }
    
    // Генерируем отчет
    let report = `# Анализ дублирующегося кода\n\n`;
    report += `*Анализ выполнен: ${new Date().toLocaleString()}*\n\n`;
    
    let totalDuplicates = 0;
    
    for (const [category, dups] of Object.entries(duplicates)) {
        totalDuplicates += dups.length;
        
        report += `## ${category}\n\n`;
        report += `Найдено групп дублей: ${dups.length}\n\n`;
        
        dups.forEach((group, index) => {
            report += `### Группа ${index + 1} (${group.length} экземпляров)\n\n`;
            
            group.forEach(block => {
                const fileName = block.file.split('/').pop();
                report += `**${fileName}:${block.line}**\n`;
                report += `\`\`\`bsl\n${block.code}\n\`\`\`\n\n`;
            });
        });
    }
    
    report += `## 📊 Итоговая статистика\n\n`;
    report += `- **Всего групп дублей:** ${totalDuplicates}\n`;
    report += `- **Потенциальная экономия:** ${totalDuplicates * 20} строк кода\n\n`;
    
    if (totalDuplicates > 0) {
        report += `## 🔄 Рекомендации\n\n`;
        report += `1. Вынесите общую логику в отдельные функции\n`;
        report += `2. Создайте библиотеки для часто используемых операций\n`;
        report += `3. Используйте общие модули для переиспользования кода\n`;
        report += `4. Рассмотрите применение паттерна "Шаблонный метод"\n\n`;
    }
    
    return {
        totalGroups: totalDuplicates,
        duplicates: duplicates,
        report: report
    };
}

function normalizeCode(code) {
    // Нормализация кода для сравнения
    return code
        .replace(/\\s+/g, ' ')           // Заменяем множественные пробелы
        .replace(/[\\r\\n]/g, ' ')        // Заменяем переносы строк
        .toLowerCase()                 // Приводим к нижнему регистру
        .replace(/\\b\\d+\\b/g, 'NUM')    // Заменяем числа
        .replace(/"[^"]*"/g, 'STR')    // Заменяем строки
        .trim();
}

function findSimilarBlocks(blocks) {
    const groups = [];
    const processed = new Set();
    
    for (let i = 0; i < blocks.length; i++) {
        if (processed.has(i)) continue;
        
        const currentGroup = [blocks[i]];
        processed.add(i);
        
        for (let j = i + 1; j < blocks.length; j++) {
            if (processed.has(j)) continue;
            
            const similarity = calculateSimilarity(
                blocks[i].normalizedCode, 
                blocks[j].normalizedCode
            );
            
            if (similarity > 0.8) { // 80% похожести
                currentGroup.push(blocks[j]);
                processed.add(j);
            }
        }
        
        if (currentGroup.length > 1) {
            groups.push(currentGroup);
        }
    }
    
    return groups;
}

function calculateSimilarity(str1, str2) {
    // Упрощенный алгоритм Левенштейна
    const matrix = [];
    const len1 = str1.length;
    const len2 = str2.length;
    
    for (let i = 0; i <= len1; i++) {
        matrix[i] = [i];
    }
    
    for (let j = 0; j <= len2; j++) {
        matrix[0][j] = j;
    }
    
    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
            matrix[i][j] = Math.min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost
            );
        }
    }
    
    const maxLen = Math.max(len1, len2);
    return (maxLen - matrix[len1][len2]) / maxLen;
}
```

---

## 📊 Code Review и анализ качества

### Пример 7: Подготовка к Code Review
```javascript
// Генерация отчета для Code Review
async function generateCodeReviewReport(configPath, changedFiles = []) {
    const report = {
        overview: {},
        codeSmells: {},
        complexityAnalysis: {},
        securityIssues: {},
        recommendations: []
    };
    
    // Если указаны конкретные файлы - анализируем только их
    const searchPath = changedFiles.length > 0 ? changedFiles.join(' ') : configPath;
    
    console.log("📋 Генерирую отчет для Code Review...");
    
    // 1. Анализ сложности функций
    const complexFunctions = await mcp__ripgrep__search({
        pattern: "(Процедура|Функция)[\\s\\S]{500,}(КонецПроцедуры|КонецФункции)",
        path: searchPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true
    });
    
    // 2. Поиск потенциальных проблем безопасности
    const securityPatterns = [
        "Выполнить\\s*\\(",
        "ОбработкаПрерыванияПользователя\\s*=\\s*Ложь",
        "УстановитьПривилегированныйРежим",
        "XMLReader|XMLWriter",
        "InternetProxy"
    ];
    
    for (const pattern of securityPatterns) {
        const result = await mcp__ripgrep__search({
            pattern: pattern,
            path: searchPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true,
            context: 2
        });
        
        if (result.trim()) {
            report.securityIssues[pattern] = result;
        }
    }
    
    // 3. Поиск TODO и FIXME
    const todoResult = await mcp__ripgrep__search({
        pattern: "(TODO|FIXME|XXX|HACK):",
        path: searchPath,
        filePattern: "*.bsl",
        caseSensitive: false,
        showLineNumbers: true,
        context: 1
    });
    
    // 4. Анализ комментариев
    const commentsResult = await mcp__ripgrep__search({
        pattern: "^\\s*//",
        path: searchPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    const commentsCount = (commentsResult.match(/^\\s*\\/\\//gm) || []).length;
    
    // 5. Статистика кода
    const totalLinesResult = await mcp__ripgrep__search({
        pattern: ".",
        path: searchPath,
        filePattern: "*.bsl",
        caseSensitive: false
    });
    
    const totalLines = totalLinesResult.split('\n').length;
    const commentRatio = (commentsCount / totalLines * 100).toFixed(1);
    
    // Формируем итоговый отчет
    let reviewReport = `# Code Review Report\n\n`;
    reviewReport += `*Дата: ${new Date().toLocaleString()}*\n`;
    reviewReport += `*Проверяемые файлы: ${changedFiles.length || 'все файлы'}*\n\n`;
    
    reviewReport += `## 📊 Общая статистика\n\n`;
    reviewReport += `- **Всего строк кода:** ${totalLines}\n`;
    reviewReport += `- **Строк комментариев:** ${commentsCount}\n`;
    reviewReport += `- **Процент комментирования:** ${commentRatio}%\n\n`;
    
    // Проблемы безопасности
    const securityIssuesCount = Object.keys(report.securityIssues).length;
    if (securityIssuesCount > 0) {
        reviewReport += `## 🔒 Проблемы безопасности (${securityIssuesCount})\n\n`;
        
        for (const [pattern, details] of Object.entries(report.securityIssues)) {
            reviewReport += `### ${pattern}\n\`\`\`\n${details}\n\`\`\`\n\n`;
        }
    }
    
    // TODO и FIXME
    if (todoResult.trim()) {
        const todoCount = (todoResult.match(/(TODO|FIXME|XXX|HACK):/g) || []).length;
        reviewReport += `## 📝 Незавершенные задачи (${todoCount})\n\n`;
        reviewReport += `\`\`\`\n${todoResult}\n\`\`\`\n\n`;
    }
    
    // Рекомендации
    reviewReport += `## 💡 Рекомендации\n\n`;
    
    if (commentRatio < 10) {
        reviewReport += `- ⚠️ **Низкий уровень комментирования** (${commentRatio}%) - рекомендуется добавить комментарии\n`;
    }
    
    if (securityIssuesCount > 0) {
        reviewReport += `- 🔒 **Найдены потенциальные проблемы безопасности** - требуется детальный анализ\n`;
    }
    
    if (todoResult.trim()) {
        reviewReport += `- 📝 **Есть незавершенные задачи** - необходимо закрыть перед релизом\n`;
    }
    
    reviewReport += `\n## ✅ Чек-лист для ревьюера\n\n`;
    reviewReport += `- [ ] Код соответствует стандартам проекта\n`;
    reviewReport += `- [ ] Все функции имеют комментарии\n`;
    reviewReport += `- [ ] Нет дублирования кода\n`;
    reviewReport += `- [ ] Обработаны все исключения\n`;
    reviewReport += `- [ ] Нет проблем безопасности\n`;
    reviewReport += `- [ ] Код покрыт тестами\n`;
    reviewReport += `- [ ] Производительность оптимальна\n`;
    
    return {
        report: reviewReport,
        stats: {
            totalLines: totalLines,
            commentsCount: commentsCount,
            commentRatio: parseFloat(commentRatio),
            securityIssues: securityIssuesCount,
            todoCount: (todoResult.match(/(TODO|FIXME|XXX|HACK):/g) || []).length
        }
    };
}

// Использование
const reviewReport = await generateCodeReviewReport(
    "src/projects/configuration/demo-accounting",
    ["CommonModules/РаботаСКачеством/Module.bsl", "Documents/ПоступлениеТоваров/ObjectModule.bsl"]
);
```

---

## 🔄 Рефакторинг и миграция кода

### Пример 8: Поиск устаревших конструкций
```javascript
// Поиск устаревших API и конструкций для миграции
async function findDeprecatedCode(configPath) {
    const deprecatedPatterns = [
        {
            pattern: "ТекущаяДата\\s*\\(\\s*\\)",
            replacement: "ТекущаяДатаСеанса()",
            reason: "ТекущаяДата() устарела, используйте ТекущаяДатаСеанса()",
            version: "8.3.14"
        },
        {
            pattern: "ПолучитьURL\\s*\\(",
            replacement: "ПолучитьНавигационнуюСсылку()",
            reason: "ПолучитьURL() устарела",
            version: "8.3.10"
        },
        {
            pattern: "ИмяВременногоФайла\\s*\\(\\s*\\)",
            replacement: "ПолучитьИмяВременногоФайла()",
            reason: "ИмяВременногоФайла() устарела",
            version: "8.3.5"
        },
        {
            pattern: "Сообщить\\s*\\(",
            replacement: "ОбщегоНазначения.СообщитьПользователю()",
            reason: "Используйте стандартную библиотеку",
            version: "рекомендация"
        },
        {
            pattern: "XMLЧтение|XMLЗапись",
            replacement: "ЧтениеXML|ЗаписьXML", 
            reason: "Устаревшие объекты для работы с XML",
            version: "8.3.8"
        }
    ];
    
    const migrationReport = {
        totalFiles: 0,
        totalIssues: 0,
        byPattern: {},
        priorityFiles: []
    };
    
    console.log("🔍 Ищу устаревшие конструкции...");
    
    for (const deprecatedItem of deprecatedPatterns) {
        const result = await mcp__ripgrep__search({
            pattern: deprecatedItem.pattern,
            path: configPath,
            filePattern: "*.bsl",
            caseSensitive: false,
            showLineNumbers: true,
            context: 1
        });
        
        if (result.trim()) {
            const matches = result.split('\n')
                .filter(line => line.includes('.bsl:') && /\\d+:/.test(line));
            
            migrationReport.byPattern[deprecatedItem.pattern] = {
                ...deprecatedItem,
                matchCount: matches.length,
                details: result
            };
            
            migrationReport.totalIssues += matches.length;
        }
    }
    
    // Определяем файлы с наибольшим количеством проблем
    const fileIssues = {};
    
    for (const patternData of Object.values(migrationReport.byPattern)) {
        const lines = patternData.details.split('\n');
        
        for (const line of lines) {
            const match = line.match(/^([^:]+\\.bsl):/);
            if (match) {
                const file = match[1];
                fileIssues[file] = (fileIssues[file] || 0) + 1;
            }
        }
    }
    
    migrationReport.priorityFiles = Object.entries(fileIssues)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10)
        .map(([file, count]) => ({ file, issueCount: count }));
    
    // Генерируем отчет о миграции
    let report = `# Отчет о необходимой миграции кода\n\n`;
    report += `*Анализ выполнен: ${new Date().toLocaleString()}*\n\n`;
    
    report += `## 📊 Общая статистика\n\n`;
    report += `- **Всего проблем:** ${migrationReport.totalIssues}\n`;
    report += `- **Типов проблем:** ${Object.keys(migrationReport.byPattern).length}\n`;
    report += `- **Файлов требуют изменений:** ${Object.keys(fileIssues).length}\n\n`;
    
    // Детализация по типам проблем
    report += `## 🔍 Найденные проблемы\n\n`;
    
    const sortedPatterns = Object.entries(migrationReport.byPattern)
        .sort(([,a], [,b]) => b.matchCount - a.matchCount);
    
    for (const [pattern, data] of sortedPatterns) {
        report += `### ${pattern} (${data.matchCount} вхождений)\n\n`;
        report += `- **Замена:** \`${data.replacement}\`\n`;
        report += `- **Причина:** ${data.reason}\n`;
        report += `- **С версии:** ${data.version}\n\n`;
        
        // Показываем несколько примеров
        const exampleLines = data.details.split('\n')
            .filter(line => line.includes('.bsl:') && /\\d+:/.test(line))
            .slice(0, 3);
        
        if (exampleLines.length > 0) {
            report += `**Примеры:**\n`;
            exampleLines.forEach(line => {
                report += `- \`${line}\`\n`;
            });
            report += '\n';
        }
    }
    
    // Приоритетные файлы для рефакторинга
    if (migrationReport.priorityFiles.length > 0) {
        report += `## 🎯 Приоритетные файлы для рефакторинга\n\n`;
        
        migrationReport.priorityFiles.forEach((item, index) => {
            const fileName = item.file.split('/').pop();
            report += `${index + 1}. **${fileName}** - ${item.issueCount} проблем\n`;
        });
        report += '\n';
    }
    
    // План миграции
    report += `## 📋 План миграции\n\n`;
    report += `### Этап 1: Критичные изменения\n`;
    report += `- Замена ТекущаяДата() на ТекущаяДатаСеанса()\n`;
    report += `- Обновление XML API\n\n`;
    
    report += `### Этап 2: Оптимизация\n`;
    report += `- Замена устаревших функций файловой системы\n`;
    report += `- Переход на стандартную библиотеку\n\n`;
    
    report += `### Этап 3: Стилистические улучшения\n`;
    report += `- Унификация обработки сообщений\n`;
    report += `- Стандартизация обработки ошибок\n\n`;
    
    report += `## 🛠️ Автоматизация миграции\n\n`;
    report += `Для автоматизации замен можно использовать следующие команды:\n\n`;
    
    for (const [pattern, data] of sortedPatterns) {
        const searchPattern = pattern.replace(/\\\\/g, '\\\\');
        report += `\`\`\`bash\n`;
        report += `# Замена ${pattern}\n`;
        report += `ripgrep "${searchPattern}" --files-with-matches --type bsl | `;
        report += `xargs sed -i 's/${searchPattern}/${data.replacement.replace(/\\\\/g, '\\\\\\\\')}/'g\n`;
        report += `\`\`\`\n\n`;
    }
    
    return {
        migrationData: migrationReport,
        report: report
    };
}

// Использование  
const migrationAnalysis = await findDeprecatedCode("src/projects/configuration/demo-accounting");
console.log(`🔄 Найдено ${migrationAnalysis.migrationData.totalIssues} мест для миграции`);
```

---

## 🛠️ Настройка и конфигурация

### Конфигурация в claude_desktop_config.json:
```json
{
  "mcpServers": {
    "ripgrep": {
      "command": "npx",
      "args": ["-y", "ripgrep-mcp"],
      "env": {
        "RIPGREP_CONFIG_PATH": ".ripgreprc",
        "RIPGREP_MAX_RESULTS": "10000",
        "RIPGREP_TIMEOUT": "30000"
      }
    }
  }
}
```

### Файл конфигурации .ripgreprc:
```
# Игнорируем бинарные файлы и временные папки
--type-add=bsl:*.bsl
--type-add=mdo:*.mdo
--type-add=xml:*.xml

# Исключаем из поиска
--glob=!*/bin/*
--glob=!*/obj/*
--glob=!*/.git/*
--glob=!*/node_modules/*
--glob=!*/cache/*

# Настройки производительности
--max-filesize=10M
--max-count=1000
```

---

## ⚠️ Важные замечания

1. **Производительность**: Большие конфигурации могут требовать времени на анализ
2. **Регулярные выражения**: Сложные паттерны могут давать ложные срабатывания
3. **Кодировка**: Убедитесь в корректной кодировке BSL файлов (UTF-8)
4. **Контекст**: Используйте параметр `context` для лучшего понимания
5. **Лимиты**: Устанавливайте разумные лимиты на количество результатов

---

## 📚 Дополнительные ресурсы

- [Официальная документация ripgrep](https://github.com/BurntSushi/ripgrep)
- [✅ BSL Language Server](../BSL-Integration/README.md)
- [Инструменты анализа кода 1С](../Examples/CodeAnalysis/)

---

*Последнее обновление: ${new Date().toLocaleDateString()}*
*Версия документа: 1.0.0*