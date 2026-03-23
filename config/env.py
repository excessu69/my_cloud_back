import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name, default=None):
    """
    Получает значение переменной окружения.

    Args:
        name (str): Имя переменной.
        default: Значение по умолчанию.

    Returns:
        Значение переменной или default.
    """
    return os.getenv(name, default)


def get_env_bool(name, default=False):
    """
    Получает булево значение переменной окружения.

    Args:
        name (str): Имя переменной.
        default (bool): Значение по умолчанию.

    Returns:
        bool: True если значение в ('true', '1', 'yes', 'on'), иначе default.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_list(name, default=''):
    """
    Получает список значений из переменной окружения.

    Args:
        name (str): Имя переменной.
        default (str): Значение по умолчанию.

    Returns:
        list: Список разделенных запятыми значений.
    """
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]