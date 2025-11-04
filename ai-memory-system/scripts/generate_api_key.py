"""
API Key Generator
Генератор API ключей для BSL Code Search API
"""

import secrets
import sys
import argparse


def generate_api_key(length: int = 32) -> str:
    """
    Генерация криптографически безопасного API ключа

    Args:
        length: Длина ключа в байтах (по умолчанию 32 байта = 256 бит)

    Returns:
        URL-safe base64 encoded ключ
    """
    return secrets.token_urlsafe(length)


def main():
    parser = argparse.ArgumentParser(
        description="Генератор API ключей для BSL Code Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Сгенерировать один ключ
  python generate_api_key.py

  # Сгенерировать 3 ключа
  python generate_api_key.py --count 3

  # Сгенерировать ключ с кастомной длиной
  python generate_api_key.py --length 48

  # Сохранить ключи в .env файл
  python generate_api_key.py --count 3 --save

Настройка API:

  1. Скопировать .env.example в .env
  2. Сгенерировать ключи этим скриптом
  3. Добавить ключи в .env:
     API_KEYS=key1,key2,key3
  4. Перезапустить API сервер
        """
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Количество ключей для генерации (по умолчанию: 1)"
    )

    parser.add_argument(
        "--length",
        "-l",
        type=int,
        default=32,
        help="Длина ключа в байтах (по умолчанию: 32)"
    )

    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="Сохранить ключи в .env файл (добавить к существующему)"
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["simple", "env", "json"],
        default="simple",
        help="Формат вывода (по умолчанию: simple)"
    )

    args = parser.parse_args()

    # Валидация
    if args.count < 1:
        print("Ошибка: количество ключей должно быть >= 1", file=sys.stderr)
        sys.exit(1)

    if args.length < 16:
        print("Ошибка: длина ключа должна быть >= 16 байт", file=sys.stderr)
        sys.exit(1)

    # Генерация ключей
    keys = [generate_api_key(args.length) for _ in range(args.count)]

    # Вывод
    if args.format == "simple":
        print(f"\n{'='*80}")
        print(f"Сгенерировано {args.count} API ключ(ей)")
        print(f"{'='*80}\n")

        for i, key in enumerate(keys, 1):
            print(f"[{i}] {key}")

        print(f"\n{'='*80}")
        print("Добавьте ключи в .env файл:")
        print(f"{'='*80}\n")

        if args.count == 1:
            print(f"API_KEY={keys[0]}")
        else:
            print(f"API_KEYS={','.join(keys)}")

        print()

    elif args.format == "env":
        # Формат для .env файла
        if args.count == 1:
            print(f"API_KEY={keys[0]}")
        else:
            print(f"API_KEYS={','.join(keys)}")

    elif args.format == "json":
        # JSON формат
        import json
        print(json.dumps({"api_keys": keys}, indent=2))

    # Сохранение в .env
    if args.save:
        try:
            import os
            from pathlib import Path

            # Путь к .env файлу
            env_path = Path(__file__).parent.parent / ".env"

            # Создать .env из .env.example если не существует
            if not env_path.exists():
                example_path = Path(__file__).parent.parent / ".env.example"
                if example_path.exists():
                    import shutil
                    shutil.copy(example_path, env_path)
                    print(f"\n✅ Создан .env файл из .env.example")

            # Добавить ключи в .env
            with open(env_path, "a", encoding="utf-8") as f:
                f.write("\n\n# Generated API Keys\n")
                if args.count == 1:
                    f.write(f"API_KEY={keys[0]}\n")
                else:
                    f.write(f"API_KEYS={','.join(keys)}\n")

            print(f"\n✅ Ключи сохранены в {env_path}")
            print(f"⚠️  Не забудьте перезапустить API сервер!")

        except Exception as e:
            print(f"\n❌ Ошибка сохранения в .env: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
