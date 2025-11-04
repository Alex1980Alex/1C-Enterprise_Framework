# 🎭 Playwright MCP - Практические примеры для 1С

[← К справочнику MCP](../MCP-Complete-Reference.md) | [К оглавлению](../README.md)

## 📚 Оглавление
- [Автотестирование веб-клиента 1С](#автотестирование-веб-клиента-1с)
- [Тестирование HTTP API](#тестирование-http-api)
- [Создание автотестов документооборота](#создание-автотестов-документооборота)
- [Интеграционные тесты](#интеграционные-тесты)
- [Мониторинг и валидация UI](#мониторинг-и-валидация-ui)

---

## 🌐 Автотестирование веб-клиента 1С

### Пример 1: Авторизация в веб-клиенте
```javascript
// Базовый сценарий авторизации в 1С веб-клиенте
async function test1CWebLogin(credentials) {
    console.log("🔐 Тестирую авторизацию в веб-клиенте 1С...");
    
    // Навигация к форме входа
    await mcp__playwright_automation__playwright_navigate({
        url: "http://localhost:1542/infobase",
        browserType: "chromium",
        headless: false,
        width: 1920,
        height: 1080
    });
    
    // Ждем загрузки страницы авторизации
    await mcp__playwright_automation__playwright_wait_for({
        text: "Вход в систему",
        time: 10
    });
    
    // Заполняем поля авторизации
    await mcp__playwright_automation__playwright_fill({
        selector: "#Username",
        value: credentials.username || "Администратор"
    });
    
    await mcp__playwright_automation__playwright_fill({
        selector: "#Password", 
        value: credentials.password || ""
    });
    
    // Выбираем информационную базу (если есть выбор)
    if (credentials.database) {
        await mcp__playwright_automation__playwright_select({
            selector: "#InfobaseSelect",
            value: credentials.database
        });
    }
    
    // Делаем скриншот формы входа
    await mcp__playwright_automation__playwright_screenshot({
        name: "login-form",
        savePng: true,
        storeBase64: false
    });
    
    // Нажимаем кнопку входа
    await mcp__playwright_automation__playwright_click({
        selector: "#LoginButton"
    });
    
    // Ждем загрузки интерфейса
    await mcp__playwright_automation__playwright_wait_for({
        text: "Главное меню",
        time: 30
    });
    
    // Проверяем успешную авторизацию
    const pageContent = await mcp__playwright_automation__playwright_get_visible_text();
    
    if (pageContent.includes("Главное меню") || pageContent.includes("Рабочий стол")) {
        console.log("✅ Авторизация успешна");
        
        // Делаем скриншот главного экрана
        await mcp__playwright_automation__playwright_screenshot({
            name: "main-interface",
            savePng: true
        });
        
        return {
            success: true,
            message: "Авторизация прошла успешно",
            userInterface: "loaded"
        };
    } else {
        console.log("❌ Ошибка авторизации");
        
        // Скриншот ошибки
        await mcp__playwright_automation__playwright_screenshot({
            name: "login-error",
            savePng: true
        });
        
        return {
            success: false,
            message: "Не удалось авторизоваться",
            pageContent: pageContent.substring(0, 500)
        };
    }
}

// Использование
const loginResult = await test1CWebLogin({
    username: "Менеджер",
    password: "123456",
    database: "DemoAccounting"
});
```

### Пример 2: Создание документа через веб-интерфейс
```javascript
// Создание документа "Поступление товаров" через веб-клиент
async function createPurchaseDocument(documentData) {
    console.log("📄 Создаю документ 'Поступление товаров'...");
    
    // Переходим к разделу документов
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Покупки']"
    });
    
    await mcp__playwright_automation__playwright_wait_for({
        text: "Поступление товаров",
        time: 5
    });
    
    // Нажимаем "Создать"
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Создать']"
    });
    
    // Ждем открытия формы документа
    await mcp__playwright_automation__playwright_wait_for({
        text: "Поступление товаров (создание)",
        time: 10
    });
    
    // Заполняем реквизиты шапки документа
    
    // Дата документа
    if (documentData.date) {
        await mcp__playwright_automation__playwright_fill({
            selector: "[data-name='Дата']",
            value: documentData.date
        });
    }
    
    // Контрагент
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Контрагент'] .dropdown-toggle"
    });
    
    await mcp__playwright_automation__playwright_wait_for({
        text: "Выбор контрагента",
        time: 5
    });
    
    await mcp__playwright_automation__playwright_fill({
        selector: "#SearchField",
        value: documentData.vendor || "ООО Поставщик"
    });
    
    await mcp__playwright_automation__playwright_press_key({
        key: "Enter"
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: ".list-item:first-child"
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: "#SelectButton"
    });
    
    // Заполнение табличной части товаров
    await fillDocumentItems(documentData.items || []);
    
    // Сохранение документа
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Записать']"
    });
    
    // Ждем подтверждения сохранения
    await mcp__playwright_automation__playwright_wait_for({
        text: "Документ записан",
        time: 10
    });
    
    // Получаем номер созданного документа
    const documentNumber = await mcp__playwright_automation__playwright_evaluate({
        script: `
            const numberField = document.querySelector('[data-name="Номер"]');
            return numberField ? numberField.value : null;
        `
    });
    
    // Скриншот созданного документа
    await mcp__playwright_automation__playwright_screenshot({
        name: `document-${documentNumber}`,
        savePng: true
    });
    
    console.log(`✅ Документ создан: №${documentNumber}`);
    
    return {
        success: true,
        documentNumber: documentNumber,
        message: `Документ 'Поступление товаров' №${documentNumber} создан`
    };
}

async function fillDocumentItems(items) {
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        
        // Добавляем новую строку
        await mcp__playwright_automation__playwright_click({
            selector: "[data-name='ДобавитьСтроку']"
        });
        
        // Выбираем номенклатуру
        await mcp__playwright_automation__playwright_click({
            selector: `[data-row='${i}'] [data-name='Номенклатура'] .dropdown-toggle`
        });
        
        await mcp__playwright_automation__playwright_fill({
            selector: "#SearchField",
            value: item.product
        });
        
        await mcp__playwright_automation__playwright_press_key({
            key: "Enter"
        });
        
        await mcp__playwright_automation__playwright_click({
            selector: ".list-item:first-child"
        });
        
        await mcp__playwright_automation__playwright_click({
            selector: "#SelectButton"
        });
        
        // Заполняем количество
        await mcp__playwright_automation__playwright_fill({
            selector: `[data-row='${i}'] [data-name='Количество']`,
            value: item.quantity.toString()
        });
        
        // Заполняем цену
        await mcp__playwright_automation__playwright_fill({
            selector: `[data-row='${i}'] [data-name='Цена']`,
            value: item.price.toString()
        });
        
        // Ждем пересчета суммы
        await mcp__playwright_automation__playwright_wait_for({
            time: 1
        });
    }
}

// Использование
const docResult = await createPurchaseDocument({
    date: "01.10.2024",
    vendor: "ООО Поставщик №1",
    items: [
        { product: "Товар 001", quantity: 10, price: 1500 },
        { product: "Товар 002", quantity: 5, price: 2500 }
    ]
});
```

---

## 🔗 Тестирование HTTP API

### Пример 3: Тестирование REST API 1С
```javascript
// Комплексное тестирование HTTP сервисов 1С
class API1CTester {
    constructor(baseUrl, credentials) {
        this.baseUrl = baseUrl;
        this.credentials = credentials;
        this.authToken = null;
    }
    
    async authenticate() {
        console.log("🔐 Аутентификация в API...");
        
        const authResponse = await mcp__playwright_automation__playwright_post({
            url: `${this.baseUrl}/hs/api/auth`,
            value: JSON.stringify({
                username: this.credentials.username,
                password: this.credentials.password
            }),
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        if (authResponse.includes('"token"')) {
            const tokenMatch = authResponse.match(/"token"\\s*:\\s*"([^"]+)"/);
            this.authToken = tokenMatch ? tokenMatch[1] : null;
            
            console.log("✅ Аутентификация успешна");
            return { success: true, token: this.authToken };
        } else {
            console.log("❌ Ошибка аутентификации");
            return { success: false, response: authResponse };
        }
    }
    
    async testDocumentCRUD() {
        if (!this.authToken) {
            await this.authenticate();
        }
        
        const testResults = {
            create: null,
            read: null,
            update: null,
            delete: null
        };
        
        console.log("📄 Тестирую CRUD операции с документами...");
        
        // CREATE - создание документа
        const createData = {
            type: "ПоступлениеТоваров",
            date: "2024-10-01T12:00:00",
            organization: "ОсновнаяОрганизация",
            vendor: "ООО Тестовый поставщик",
            items: [
                {
                    product: "Товар для тестирования",
                    quantity: 1,
                    price: 100.00
                }
            ]
        };
        
        const createResponse = await mcp__playwright_automation__playwright_post({
            url: `${this.baseUrl}/hs/api/v1/documents`,
            value: JSON.stringify(createData),
            token: `Bearer ${this.authToken}`
        });
        
        if (createResponse.includes('"id"')) {
            const idMatch = createResponse.match(/"id"\\s*:\\s*"([^"]+)"/);
            const documentId = idMatch ? idMatch[1] : null;
            
            testResults.create = {
                success: true,
                documentId: documentId,
                response: createResponse
            };
            
            console.log(`✅ CREATE: Документ создан с ID ${documentId}`);
            
            // READ - чтение документа
            const readResponse = await mcp__playwright_automation__playwright_get({
                url: `${this.baseUrl}/hs/api/v1/documents/${documentId}`
            });
            
            testResults.read = {
                success: readResponse.includes(documentId),
                response: readResponse
            };
            
            console.log(`${testResults.read.success ? '✅' : '❌'} READ: Документ прочитан`);
            
            // UPDATE - обновление документа
            const updateData = {
                comment: "Обновлено автотестом",
                status: "conducted"
            };
            
            const updateResponse = await mcp__playwright_automation__playwright_put({
                url: `${this.baseUrl}/hs/api/v1/documents/${documentId}`,
                value: JSON.stringify(updateData)
            });
            
            testResults.update = {
                success: updateResponse.includes('"success"') || updateResponse.includes('200'),
                response: updateResponse
            };
            
            console.log(`${testResults.update.success ? '✅' : '❌'} UPDATE: Документ обновлен`);
            
            // DELETE - удаление документа  
            const deleteResponse = await mcp__playwright_automation__playwright_delete({
                url: `${this.baseUrl}/hs/api/v1/documents/${documentId}`
            });
            
            testResults.delete = {
                success: deleteResponse.includes('"deleted"') || deleteResponse.includes('200'),
                response: deleteResponse
            };
            
            console.log(`${testResults.delete.success ? '✅' : '❌'} DELETE: Документ удален`);
            
        } else {
            testResults.create = {
                success: false,
                error: "Не удалось создать документ",
                response: createResponse
            };
            
            console.log("❌ CREATE: Ошибка создания документа");
        }
        
        return testResults;
    }
    
    async testCatalogOperations() {
        console.log("📚 Тестирую операции со справочниками...");
        
        const catalogTests = {};
        
        // Получение списка номенклатуры
        const nomenclatureResponse = await mcp__playwright_automation__playwright_get({
            url: `${this.baseUrl}/hs/api/v1/catalogs/nomenclature?limit=10`
        });
        
        catalogTests.nomenclatureList = {
            success: nomenclatureResponse.includes('"items"'),
            count: (nomenclatureResponse.match(/"id"/g) || []).length,
            response: nomenclatureResponse
        };
        
        console.log(`✅ Номенклатура: получено ${catalogTests.nomenclatureList.count} элементов`);
        
        // Получение списка контрагентов
        const vendorsResponse = await mcp__playwright_automation__playwright_get({
            url: `${this.baseUrl}/hs/api/v1/catalogs/vendors?limit=10`
        });
        
        catalogTests.vendorsList = {
            success: vendorsResponse.includes('"items"'),
            count: (vendorsResponse.match(/"id"/g) || []).length,
            response: vendorsResponse
        };
        
        console.log(`✅ Контрагенты: получено ${catalogTests.vendorsList.count} элементов`);
        
        return catalogTests;
    }
    
    async runFullAPITest() {
        console.log("🚀 Запускаю полное тестирование API...");
        
        const testSuite = {
            startTime: new Date(),
            authentication: null,
            documentOperations: null,
            catalogOperations: null,
            endTime: null,
            duration: null,
            success: false
        };
        
        try {
            // Аутентификация
            testSuite.authentication = await this.authenticate();
            
            if (testSuite.authentication.success) {
                // CRUD операции с документами
                testSuite.documentOperations = await this.testDocumentCRUD();
                
                // Операции со справочниками
                testSuite.catalogOperations = await this.testCatalogOperations();
            }
            
            testSuite.endTime = new Date();
            testSuite.duration = testSuite.endTime - testSuite.startTime;
            
            // Определяем общий результат
            testSuite.success = testSuite.authentication.success &&
                               testSuite.documentOperations?.create?.success &&
                               testSuite.catalogOperations?.nomenclatureList?.success;
            
            // Сохраняем отчет
            const report = this.generateTestReport(testSuite);
            
            const reportPath = `reports/api-test-${Date.now()}.md`;
            await mcp__filesystem__write_file({
                path: reportPath,
                content: report
            });
            
            console.log(`📄 Отчет сохранен: ${reportPath}`);
            
        } catch (error) {
            testSuite.error = error.message;
            testSuite.success = false;
            console.log(`❌ Ошибка тестирования: ${error.message}`);
        }
        
        return testSuite;
    }
    
    generateTestReport(testSuite) {
        const successIcon = testSuite.success ? '✅' : '❌';
        
        return `# Отчет тестирования API 1С ${successIcon}

## 📊 Общая информация
- **Время начала:** ${testSuite.startTime.toLocaleString()}
- **Время окончания:** ${testSuite.endTime?.toLocaleString() || 'не завершено'}
- **Длительность:** ${testSuite.duration ? Math.round(testSuite.duration / 1000) : 'N/A'} сек
- **Общий результат:** ${testSuite.success ? 'УСПЕШНО' : 'ПРОВАЛЕНО'}

## 🔐 Аутентификация
- **Статус:** ${testSuite.authentication?.success ? '✅ Успешно' : '❌ Провалено'}
- **Токен получен:** ${testSuite.authentication?.token ? 'Да' : 'Нет'}

## 📄 Операции с документами
${testSuite.documentOperations ? `
- **CREATE:** ${testSuite.documentOperations.create?.success ? '✅' : '❌'}
- **READ:** ${testSuite.documentOperations.read?.success ? '✅' : '❌'}  
- **UPDATE:** ${testSuite.documentOperations.update?.success ? '✅' : '❌'}
- **DELETE:** ${testSuite.documentOperations.delete?.success ? '✅' : '❌'}
` : 'Не выполнялись'}

## 📚 Операции со справочниками
${testSuite.catalogOperations ? `
- **Номенклатура:** ${testSuite.catalogOperations.nomenclatureList?.success ? '✅' : '❌'} (${testSuite.catalogOperations.nomenclatureList?.count || 0} элементов)
- **Контрагенты:** ${testSuite.catalogOperations.vendorsList?.success ? '✅' : '❌'} (${testSuite.catalogOperations.vendorsList?.count || 0} элементов)
` : 'Не выполнялись'}

## 🔍 Рекомендации
${testSuite.success ? 
  '- API работает стабильно\n- Все основные операции функционируют\n- Можно использовать в продуктиве' :
  '- Обнаружены проблемы в работе API\n- Требуется детальный анализ ошибок\n- Не рекомендуется использование в продуктиве'
}

---
*Отчет сгенерирован автоматически: ${new Date().toLocaleString()}*
`;
    }
}

// Использование
const apiTester = new API1CTester(
    "http://localhost:1542/infobase",
    { username: "WebAPIUser", password: "password123" }
);

const apiTestResults = await apiTester.runFullAPITest();
```

---

## 📋 Создание автотестов документооборота

### Пример 4: E2E тест полного цикла документооборота
```javascript
// Тест полного цикла: Поступление → Реализация → Отчеты
async function testFullDocumentFlow() {
    console.log("🔄 Тестирую полный цикл документооборота...");
    
    const flowResults = {
        login: null,
        purchaseDocument: null,
        stockCheck: null,
        saleDocument: null,
        reports: null,
        cleanup: null
    };
    
    try {
        // 1. Авторизация
        console.log("1️⃣ Авторизация...");
        flowResults.login = await test1CWebLogin({
            username: "Менеджер",
            password: "123456"
        });
        
        if (!flowResults.login.success) {
            throw new Error("Не удалось авторизоваться");
        }
        
        // 2. Создание документа поступления
        console.log("2️⃣ Создание поступления товаров...");
        flowResults.purchaseDocument = await createPurchaseDocument({
            date: new Date().toISOString().split('T')[0],
            vendor: "ООО Тестовый поставщик",
            items: [
                { product: "Тестовый товар E2E", quantity: 100, price: 50 }
            ]
        });
        
        if (!flowResults.purchaseDocument.success) {
            throw new Error("Не удалось создать документ поступления");
        }
        
        // 3. Проведение документа поступления
        console.log("3️⃣ Проведение документа...");
        await mcp__playwright_automation__playwright_click({
            selector: "[data-name='Провести']"
        });
        
        await mcp__playwright_automation__playwright_wait_for({
            text: "Документ проведен",
            time: 15
        });
        
        // 4. Проверка остатков на складе
        console.log("4️⃣ Проверка остатков...");
        flowResults.stockCheck = await checkProductStock("Тестовый товар E2E");
        
        // 5. Создание документа реализации
        console.log("5️⃣ Создание реализации товаров...");
        flowResults.saleDocument = await createSaleDocument({
            customer: "ООО Тестовый покупатель",
            items: [
                { product: "Тестовый товар E2E", quantity: 30, price: 75 }
            ]
        });
        
        // 6. Проверка отчетов
        console.log("6️⃣ Проверка отчетов...");
        flowResults.reports = await checkReports();
        
        // 7. Очистка тестовых данных
        console.log("7️⃣ Очистка данных...");
        flowResults.cleanup = await cleanupTestData([
            flowResults.purchaseDocument.documentNumber,
            flowResults.saleDocument?.documentNumber
        ]);
        
        console.log("✅ Полный цикл документооборота протестирован успешно");
        
    } catch (error) {
        console.log(`❌ Ошибка в цикле документооборота: ${error.message}`);
        
        // Скриншот ошибки
        await mcp__playwright_automation__playwright_screenshot({
            name: "e2e-error",
            savePng: true
        });
        
        flowResults.error = error.message;
    }
    
    // Генерируем отчет
    const report = generateE2EReport(flowResults);
    
    const reportPath = `reports/e2e-test-${Date.now()}.md`;
    await mcp__filesystem__write_file({
        path: reportPath,
        content: report
    });
    
    return {
        results: flowResults,
        reportPath: reportPath
    };
}

async function checkProductStock(productName) {
    // Переход к отчету остатков
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Отчеты']"
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='ОстаткиТоваров']"
    });
    
    await mcp__playwright_automation__playwright_wait_for({
        text: "Остатки товаров",
        time: 10
    });
    
    // Устанавливаем фильтр по номенклатуре
    await mcp__playwright_automation__playwright_fill({
        selector: "[data-name='НоменклатураФильтр']",
        value: productName
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Сформировать']"
    });
    
    await mcp__playwright_automation__playwright_wait_for({
        text: productName,
        time: 15
    });
    
    // Получаем данные об остатках
    const reportContent = await mcp__playwright_automation__playwright_get_visible_text();
    
    const stockMatch = reportContent.match(/\\b(\\d+(?:,\\d+)?)\\b.*шт/);
    const stockQuantity = stockMatch ? parseFloat(stockMatch[1].replace(',', '.')) : 0;
    
    return {
        success: stockQuantity > 0,
        quantity: stockQuantity,
        product: productName
    };
}

async function createSaleDocument(documentData) {
    // Переход к созданию реализации
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Продажи']"
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='РеализацияТоваров']"
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='Создать']"
    });
    
    // Заполнение аналогично поступлению
    // ... (детали заполнения)
    
    return {
        success: true,
        documentNumber: "РТ-000001" // получается из интерфейса
    };
}

function generateE2EReport(results) {
    return `# E2E Тест документооборота

## 📊 Результаты тестирования

| Этап | Статус | Детали |
|------|--------|---------|
| Авторизация | ${results.login?.success ? '✅' : '❌'} | ${results.login?.message || 'N/A'} |
| Поступление | ${results.purchaseDocument?.success ? '✅' : '❌'} | Документ №${results.purchaseDocument?.documentNumber || 'N/A'} |
| Проверка остатков | ${results.stockCheck?.success ? '✅' : '❌'} | Количество: ${results.stockCheck?.quantity || 0} |
| Реализация | ${results.saleDocument?.success ? '✅' : '❌'} | Документ №${results.saleDocument?.documentNumber || 'N/A'} |
| Отчеты | ${results.reports?.success ? '✅' : '❌'} | ${results.reports?.message || 'N/A'} |
| Очистка | ${results.cleanup?.success ? '✅' : '❌'} | ${results.cleanup?.message || 'N/A'} |

## 🎯 Общий результат
${Object.values(results).every(r => r?.success) ? '✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ' : '❌ ЕСТЬ ПРОБЛЕМЫ'}

---
*Отчет создан: ${new Date().toLocaleString()}*
`;
}
```

---

## 🔧 Интеграционные тесты

### Пример 5: Тестирование интеграции с внешними системами
```javascript
// Тест интеграции 1С с внешними API
async function testExternalIntegration() {
    console.log("🔗 Тестирую интеграцию с внешними системами...");
    
    // Ожидание запроса к внешнему API
    await mcp__playwright_automation__playwright_expect_response({
        id: "external-api-call",
        url: "**/api/external/**"
    });
    
    // Запускаем обмен данными в 1С
    await mcp__playwright_automation__playwright_navigate({
        url: "http://localhost:1542/infobase#/DataExchange"
    });
    
    await mcp__playwright_automation__playwright_click({
        selector: "[data-name='ЗапуститьОбмен']"
    });
    
    // Проверяем, что запрос к внешнему API был выполнен
    const apiResponse = await mcp__playwright_automation__playwright_assert_response({
        id: "external-api-call",
        value: '"status":"success"'
    });
    
    console.log("✅ Интеграция с внешним API работает");
    
    return {
        success: true,
        apiCallMade: true,
        responseValid: apiResponse.includes('success')
    };
}

// Тест производительности веб-клиента
async function performanceTest() {
    console.log("⚡ Тестирую производительность...");
    
    const startTime = Date.now();
    
    // Открытие большого списка документов
    await mcp__playwright_automation__playwright_navigate({
        url: "http://localhost:1542/infobase#/Documents"
    });
    
    await mcp__playwright_automation__playwright_wait_for({
        text: "Загрузка завершена",
        time: 30
    });
    
    const loadTime = Date.now() - startTime;
    
    // Проверка времени загрузки
    const isPerformanceGood = loadTime < 5000; // 5 секунд
    
    console.log(`${isPerformanceGood ? '✅' : '⚠️'} Время загрузки: ${loadTime}мс`);
    
    return {
        loadTime: loadTime,
        performanceGood: isPerformanceGood,
        threshold: 5000
    };
}
```

---

## 👁️ Мониторинг и валидация UI

### Пример 6: Визуальное тестирование интерфейса
```javascript
// Визуальное сравнение интерфейса
async function visualRegressionTest() {
    console.log("👁️ Выполняю визуальное тестирование...");
    
    const testPages = [
        { name: "main-menu", url: "/Main" },
        { name: "document-list", url: "/Documents" },
        { name: "reports-section", url: "/Reports" },
        { name: "settings", url: "/Settings" }
    ];
    
    const visualResults = [];
    
    for (const page of testPages) {
        console.log(`📸 Тестирую страницу: ${page.name}`);
        
        await mcp__playwright_automation__playwright_navigate({
            url: `http://localhost:1542/infobase#${page.url}`
        });
        
        await mcp__playwright_automation__playwright_wait_for({
            time: 3 // ждем полной загрузки
        });
        
        // Делаем скриншот
        await mcp__playwright_automation__playwright_screenshot({
            name: `baseline-${page.name}`,
            savePng: true,
            fullPage: true
        });
        
        // Проверяем наличие ключевых элементов
        const pageContent = await mcp__playwright_automation__playwright_get_visible_text();
        
        const elementChecks = {
            hasHeader: pageContent.includes("Главное меню") || pageContent.includes("Панель навигации"),
            hasContent: pageContent.length > 100,
            hasFooter: pageContent.includes("© 2024") || pageContent.includes("Версия")
        };
        
        visualResults.push({
            pageName: page.name,
            url: page.url,
            screenshot: `baseline-${page.name}.png`,
            elementChecks: elementChecks,
            allElementsPresent: Object.values(elementChecks).every(check => check)
        });
    }
    
    // Генерируем отчет визуального тестирования
    const visualReport = generateVisualReport(visualResults);
    
    return {
        results: visualResults,
        report: visualReport,
        allPassed: visualResults.every(r => r.allElementsPresent)
    };
}

function generateVisualReport(results) {
    let report = `# Отчет визуального тестирования\n\n`;
    report += `*Дата: ${new Date().toLocaleString()}*\n\n`;
    
    report += `## 📊 Сводка\n\n`;
    const passedCount = results.filter(r => r.allElementsPresent).length;
    report += `- **Всего страниц:** ${results.length}\n`;
    report += `- **Пройдено:** ${passedCount}\n`;
    report += `- **Провалено:** ${results.length - passedCount}\n\n`;
    
    report += `## 📋 Детали по страницам\n\n`;
    
    results.forEach(result => {
        const status = result.allElementsPresent ? '✅' : '❌';
        report += `### ${status} ${result.pageName}\n\n`;
        report += `- **URL:** ${result.url}\n`;
        report += `- **Скриншот:** ${result.screenshot}\n`;
        
        report += `- **Проверки элементов:**\n`;
        Object.entries(result.elementChecks).forEach(([check, passed]) => {
            report += `  - ${check}: ${passed ? '✅' : '❌'}\n`;
        });
        
        report += '\n';
    });
    
    return report;
}

// Мониторинг консольных ошибок
async function monitorConsoleErrors() {
    console.log("🐛 Мониторю консольные ошибки...");
    
    // Получаем логи консоли
    const consoleLogs = await mcp__playwright_automation__playwright_console_logs({
        type: "error",
        limit: 50
    });
    
    if (consoleLogs && consoleLogs.length > 0) {
        console.log(`⚠️ Найдено ${consoleLogs.length} ошибок в консоли`);
        
        // Анализируем типы ошибок
        const errorTypes = {
            javascript: 0,
            network: 0,
            security: 0,
            other: 0
        };
        
        consoleLogs.forEach(log => {
            if (log.includes('TypeError') || log.includes('ReferenceError')) {
                errorTypes.javascript++;
            } else if (log.includes('Failed to load') || log.includes('404')) {
                errorTypes.network++;
            } else if (log.includes('CORS') || log.includes('CSP')) {
                errorTypes.security++;
            } else {
                errorTypes.other++;
            }
        });
        
        return {
            hasErrors: true,
            totalErrors: consoleLogs.length,
            errorTypes: errorTypes,
            logs: consoleLogs
        };
    } else {
        console.log("✅ Ошибок в консоли не обнаружено");
        return {
            hasErrors: false,
            totalErrors: 0
        };
    }
}
```

---

## 🛠️ Настройка и конфигурация

### Конфигурация в claude_desktop_config.json:
```json
{
  "mcpServers": {
    "playwright-automation": {
      "command": "npx",
      "args": ["-y", "playwright-automation-mcp"],
      "env": {
        "PLAYWRIGHT_BROWSERS_PATH": "./browsers",
        "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "false",
        "PLAYWRIGHT_TIMEOUT": "30000",
        "PLAYWRIGHT_HEADLESS": "false"
      }
    }
  }
}
```

### Настройки браузеров:
```javascript
// Конфигурация для различных сценариев
const browserConfigs = {
    development: {
        headless: false,
        slowMo: 100,
        timeout: 30000
    },
    ci: {
        headless: true,
        slowMo: 0,
        timeout: 15000
    },
    debug: {
        headless: false,
        slowMo: 500,
        timeout: 60000,
        devtools: true
    }
};
```

---

## ⚠️ Важные замечания

1. **Стабильность**: Веб-клиент 1С может медленно загружаться
2. **Селекторы**: Используйте стабильные атрибуты `data-name`
3. **Ожидания**: Всегда добавляйте ожидания после действий
4. **Очистка**: Удаляйте тестовые данные после тестов
5. **Скриншоты**: Делайте скриншоты для отладки ошибок

---

## 📚 Дополнительные ресурсы

- [Официальная документация Playwright](https://playwright.dev)
- [Тестирование веб-клиента 1С](../Examples/WebClient-Testing/)
- [CI/CD интеграция](../Automation/CI-CD/)

---

*Последнее обновление: ${new Date().toLocaleDateString()}*
*Версия документа: 1.0.0*