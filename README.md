# 📦 MyCloud — облачное хранилище (Backend)

Backend часть дипломного проекта.  
Реализует REST API для хранения файлов пользователей.

## 🚀 Возможности

- Регистрация и авторизация пользователей
- Получение текущего пользователя
- Выход из системы
- Загрузка файлов
- Список файлов пользователя
- Удаление файлов
- Обновление комментария файла
- Скачивание файла
- Генерация публичной ссылки
- Скачивание файла по публичной ссылке
- Администрирование пользователей

---

## 🛠 Стек

- Python 3.13
- Django 6
- Django REST Framework
- PostgreSQL
- DBeaver (для просмотра БД)

---

## ⚙️ Установка

### 1. Клонировать репозиторий

```
git clone <repo_url>
cd Backend
```

### 2. Создать виртуальное окружение

```
python -m venv venv
venv\Scripts\activate
```

### 3. Установить зависимости

```
pip install -r requirements.txt
```

---

## 🔐 Настройка окружения

Создать файл `.env` на основе `.env.example` :

```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=mycloud
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🗄️ База данных

Создать БД в PostgreSQL:

```
CREATE DATABASE mycloud;
```

---

## 🔧 Миграции

```
python manage.py migrate
```

---

## 👤 Создание администратора

```
python manage.py createsuperuser
```

---

## ▶️ Запуск сервера

```
python manage.py runserver
```

---

## 📡 API

### 🔐 Аутентификация

- POST `/api/auth/register/` — регистрация
- POST `/api/auth/login/` — вход
- POST `/api/auth/logout/` — выход
- GET `/api/auth/me/` — текущий пользователь

---

### 👤 Users (admin)

- GET `/api/auth/users/` — список пользователей
- DELETE `/api/auth/users/{id}/` — удалить пользователя
- PATCH `/api/auth/users/{id}/` — изменить пользователя

---

### 📁 Файлы

- GET `/api/files/` — список файлов
- POST `/api/files/upload/` — загрузка файла
- DELETE `/api/files/<id>/delete/`— удалить файл
- PATCH `/api/files/<id>/` — обновить файл
- GET `/api/files/<id>/download/` — скачать файл

---

### 🌍 Публичный доступ

- POST `/api/files/<id>/public-link/`— получить ссылку
- GET `/api/files/public/<token>/`— скачать файл

---

## 📝 Логирование

Все действия логируются:

- регистрация
- вход/выход
- загрузка/удаление файлов
- скачивание
- генерация публичных ссылок

---

## 📌 Особенности

- аутентификация через сессии
- проверка прав доступа
- уникальные имена файлов
- поддержка публичных ссылок
- хранение файлов на сервере

---

## 📁 Структура проекта

```
backend/
├── config/
├── apps/
│   ├── users/
│   ├── storage/
│   └── core/
├── media/
├── static/
└── logs/
```

---

## ⚠️ Важно

- `.env` не добавляется в Git
- используется PostgreSQL
- проект предназначен для учебных целей

---
