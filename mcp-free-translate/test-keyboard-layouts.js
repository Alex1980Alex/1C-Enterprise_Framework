#!/usr/bin/env node
/**
 * Тестовый скрипт для проверки функций раскладки клавиатуры
 */

import { fixLayout, convertLayout, detectLayout } from './keyboard-layouts.js';

console.log('=== Тест функций раскладки клавиатуры ===\n');

// Тестовые случаи
const testCases = [
  { text: 'lf', expected: 'да', description: 'Простое слово' },
  { text: 'ghbdtn', expected: 'привет', description: 'Приветствие' },
  { text: 'rjvgm.nth', expected: 'компьютер', description: 'Компьютер' },
  { text: 'python', expected: 'зйерщт', description: 'Python (en->ru)' },
  { text: 'да', expected: 'lf', description: 'Обратное преобразование' },
  { text: 'Hello World', expected: 'Руддщ Цщкдв', description: 'С пробелами' },
];

console.log('1. Тест функции detectLayout():\n');
testCases.forEach(({ text }) => {
  const detected = detectLayout(text);
  console.log(`  "${text}" -> layout: ${detected}`);
});

console.log('\n2. Тест функции fixLayout() (auto):\n');
testCases.forEach(({ text, expected, description }) => {
  const result = fixLayout(text, 'auto');
  const status = result.corrected === expected ? '✅' : '❌';
  console.log(`  ${status} ${description}`);
  console.log(`     Original:  "${text}"`);
  console.log(`     Corrected: "${result.corrected}"`);
  console.log(`     Expected:  "${expected}"`);
  console.log(`     From: ${result.from} -> To: ${result.to} (confidence: ${result.confidence})\n`);
});

console.log('3. Тест функции convertLayout():\n');
console.log('  EN -> RU:');
console.log(`    "hello" -> "${convertLayout('hello', 'en', 'ru')}"`);
console.log(`    "world" -> "${convertLayout('world', 'en', 'ru')}"`);

console.log('\n  RU -> EN:');
console.log(`    "привет" -> "${convertLayout('привет', 'ru', 'en')}"`);
console.log(`    "мир" -> "${convertLayout('мир', 'ru', 'en')}"`);

console.log('\n4. Тест с вашим примером "lf":\n');
const testLf = fixLayout('lf', 'auto');
console.log('  Input:  "lf"');
console.log(`  Output: "${testLf.corrected}"`);
console.log(`  Details: ${JSON.stringify(testLf, null, 2)}`);

console.log('\n=== Все тесты завершены ===');
