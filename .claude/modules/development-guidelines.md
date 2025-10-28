# Development Guidelines

## Information Priority

1. **PRIMARY**: Documents from "Сценарий разработки" (organizational processes)
2. **SECONDARY**: Official 1C:Enterprise documentation from "Документация разработчика"
3. **SUPPLEMENTARY**: External sources and internet research when needed

## Quality Practices

1. **BSL Validation**: Always run `python -m sonar_integration analyze` before commits
2. **Documentation**: Reference official 1C documentation when applicable
3. **File Management**: Follow `.claude/file-organization-rules.md` СТРОГО
4. **Version Control**: Git hooks automatically validate code quality
5. **Testing**: Use Task Master for systematic development approach

## Response Guidelines

**For technical 1C questions, include:**
1. **📖 REFERENCE**: Quote from official documentation when relevant
2. **🔧 EXPLANATION**: Technical explanation using 1C terminology
3. **💡 PRACTICAL ADVICE**: Actionable implementation guidance
4. **✅ VALIDATION**: BSL quality checks and best practices

## Best Practices

### For 1C Development
- Always run BSL analysis before committing code
- Use meaningful variable and function names in Russian (1C standard)
- Follow BSL Language Server recommendations (793 rules available)
- Implement proper error handling with Попытка...Исключение...КонецПопытки
- Document architectural decisions in Task Master

### For Framework Usage
- Start with working tools (BSL + Task Master + Development Automation)
- Use Git hooks for automatic quality control
- Reference framework documentation for best practices
- Leverage automation tools for efficient development

## Git Workflow (Automated)

### Standard workflow with automatic validation
```bash
git checkout -b feature/task-description
# Make changes - Git hooks will automatically run BSL analysis
git add .
git commit -m "feat: description

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Git hooks automatically:**
- Run BSL Language Server analysis on changed .bsl files
- Block commits if BLOCKER or CRITICAL issues found
- Provide detailed error reports

## При обнаружении ошибок

- Автоматически предлагай исправления
- Ссылайся на конкретные правила из `sonar_integration/rules/bsl_rules_catalog.json`
- Используй уровни критичности: BLOCKER > CRITICAL > MAJOR > MINOR > INFO

## VS Code/Cursor горячие клавиши

- `Ctrl+Shift+B` - анализ текущего файла
- `Ctrl+Alt+B` - полный анализ проекта
- `Ctrl+Shift+Alt+B` - генерация HTML отчёта