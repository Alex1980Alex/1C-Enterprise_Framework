"""
API Key Authentication
Модуль аутентификации через API ключи
"""

import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

# Security scheme
security = HTTPBearer(auto_error=False)

# API ключи из переменных окружения
# Формат: API_KEYS=key1,key2,key3 или одиночный ключ API_KEY=your_key
def get_api_keys() -> set:
    """Получение списка валидных API ключей"""

    # Множественные ключи через запятую
    keys_env = os.getenv("API_KEYS", "")
    if keys_env:
        return set(key.strip() for key in keys_env.split(",") if key.strip())

    # Одиночный ключ
    single_key = os.getenv("API_KEY", "")
    if single_key:
        return {single_key}

    # Режим разработки - без аутентификации
    # Если переменные не установлены, API работает без защиты
    return set()


def is_auth_enabled() -> bool:
    """Проверка, включена ли аутентификация"""
    return len(get_api_keys()) > 0


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> str:
    """
    Проверка API ключа

    Возвращает API ключ при успешной проверке
    Бросает HTTPException при ошибке
    """

    # Если аутентификация отключена, разрешаем доступ
    if not is_auth_enabled():
        return "auth_disabled"

    # Проверка наличия credentials
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide Authorization header with Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Проверка валидности ключа
    api_key = credentials.credentials
    valid_keys = get_api_keys()

    if api_key not in valid_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    return api_key


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """
    Опциональная аутентификация

    Позволяет доступ без ключа, но возвращает ключ если он предоставлен
    Полезно для публичных endpoints с расширенными возможностями для авторизованных
    """
    if not credentials:
        return None

    # Если ключ предоставлен, проверяем его валидность
    if is_auth_enabled():
        api_key = credentials.credentials
        valid_keys = get_api_keys()

        if api_key in valid_keys:
            return api_key

    return None


def generate_api_key() -> str:
    """
    Генерация нового API ключа

    Использует secrets.token_urlsafe для генерации безопасного ключа
    """
    return secrets.token_urlsafe(32)


# Dependency для защищенных endpoints
async def require_api_key(api_key: str = Depends(verify_api_key)) -> str:
    """Dependency для endpoints, требующих аутентификации"""
    return api_key


# Dependency для публичных endpoints с опциональной аутентификацией
async def get_optional_api_key(api_key: Optional[str] = Depends(optional_auth)) -> Optional[str]:
    """Dependency для публичных endpoints с опциональной расширенной функциональностью"""
    return api_key


# Утилиты для логирования
def log_auth_attempt(api_key: str, success: bool, endpoint: str):
    """Логирование попытки аутентификации"""
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILED"
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"

    print(f"[{timestamp}] AUTH {status}: {masked_key} -> {endpoint}")
