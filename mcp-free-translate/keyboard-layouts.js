/**
 * Keyboard Layout Mappings
 * Маппинг клавиатурных раскладок для исправления текста, набранного в неправильной раскладке
 */

// EN -> RU маппинг (QWERTY -> ЙЦУКЕН)
export const EN_TO_RU = {
  // Lower case
  'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
  '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
  'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
  ',': 'б', '.': 'ю', '/': '.',

  // Upper case
  'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
  '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
  'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т', 'M': 'Ь',
  '<': 'Б', '>': 'Ю', '?': ',',

  // Special characters
  '`': 'ё', '~': 'Ё', '@': '"', '#': '№', '$': ';', '^': ':', '&': '?'
};

// RU -> EN маппинг (ЙЦУКЕН -> QWERTY)
export const RU_TO_EN = {
  // Lower case
  'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p',
  'х': '[', 'ъ': ']', 'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k',
  'д': 'l', 'ж': ';', 'э': "'", 'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n', 'ь': 'm',
  'б': ',', 'ю': '.', '.': '/',

  // Upper case
  'Й': 'Q', 'Ц': 'W', 'У': 'E', 'К': 'R', 'Е': 'T', 'Н': 'Y', 'Г': 'U', 'Ш': 'I', 'Щ': 'O', 'З': 'P',
  'Х': '{', 'Ъ': '}', 'Ф': 'A', 'Ы': 'S', 'В': 'D', 'А': 'F', 'П': 'G', 'Р': 'H', 'О': 'J', 'Л': 'K',
  'Д': 'L', 'Ж': ':', 'Э': '"', 'Я': 'Z', 'Ч': 'X', 'С': 'C', 'М': 'V', 'И': 'B', 'Т': 'N', 'Ь': 'M',
  'Б': '<', 'Ю': '>', ',': '?',

  // Special characters
  'ё': '`', 'Ё': '~', '"': '@', '№': '#', ';': '$', ':': '^', '?': '&'
};

/**
 * Определяет раскладку текста
 * @param {string} text - текст для анализа
 * @returns {string} 'en' | 'ru' | 'mixed' | 'unknown'
 */
export function detectLayout(text) {
  let enCount = 0;
  let ruCount = 0;

  for (const char of text) {
    if (EN_TO_RU[char] || EN_TO_RU[char.toLowerCase()]) {
      enCount++;
    }
    if (RU_TO_EN[char] || RU_TO_EN[char.toLowerCase()]) {
      ruCount++;
    }
  }

  const total = enCount + ruCount;
  if (total === 0) return 'unknown';

  const enRatio = enCount / total;
  const ruRatio = ruCount / total;

  if (enRatio > 0.7) return 'en';
  if (ruRatio > 0.7) return 'ru';
  if (enRatio > 0.1 && ruRatio > 0.1) return 'mixed';

  return 'unknown';
}

/**
 * Конвертирует текст из одной раскладки в другую
 * @param {string} text - исходный текст
 * @param {string} fromLayout - исходная раскладка ('en' | 'ru')
 * @param {string} toLayout - целевая раскладка ('en' | 'ru')
 * @returns {string} - сконвертированный текст
 */
export function convertLayout(text, fromLayout, toLayout) {
  if (fromLayout === toLayout) {
    return text;
  }

  const mapping = (fromLayout === 'en' && toLayout === 'ru')
    ? EN_TO_RU
    : RU_TO_EN;

  return text.split('').map(char => mapping[char] || char).join('');
}

/**
 * Автоматически исправляет раскладку текста
 * @param {string} text - текст с возможной неправильной раскладкой
 * @param {string} targetLayout - желаемая раскладка ('en' | 'ru' | 'auto')
 * @returns {Object} - { corrected: string, from: string, to: string, confidence: number }
 */
export function fixLayout(text, targetLayout = 'auto') {
  const detectedLayout = detectLayout(text);

  // Если раскладка смешанная или неизвестна - возвращаем как есть
  if (detectedLayout === 'mixed' || detectedLayout === 'unknown') {
    return {
      corrected: text,
      from: detectedLayout,
      to: detectedLayout,
      confidence: 0.0,
      message: 'Cannot determine layout or text contains mixed layouts'
    };
  }

  // Определяем целевую раскладку
  let toLayout = targetLayout;
  if (targetLayout === 'auto') {
    // Если текст на английском, скорее всего хотели русский, и наоборот
    toLayout = detectedLayout === 'en' ? 'ru' : 'en';
  }

  // Если раскладка уже правильная
  if (detectedLayout === toLayout) {
    return {
      corrected: text,
      from: detectedLayout,
      to: toLayout,
      confidence: 1.0,
      message: 'Text is already in target layout'
    };
  }

  // Конвертируем
  const corrected = convertLayout(text, detectedLayout, toLayout);

  return {
    corrected,
    from: detectedLayout,
    to: toLayout,
    confidence: 0.95
  };
}
