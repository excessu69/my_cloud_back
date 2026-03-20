import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name, default=None):
    return os.getenv(name, default)


def get_env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_list(name, default=''):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]