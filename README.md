# Доставка еды

Сервис доставки еды (аналог Яндекс Еды): рестораны, меню, корзина и заказы.

## Стек

- **Backend:** Python, Django, Django REST Framework, SimpleJWT, django-cors-headers, django-filter
- **Frontend:** React, Vite, Axios

## Запуск (Windows PowerShell)

### Backend

```powershell
cd backend

# Создать виртуальное окружение
python -m venv .venv

# Активировать
.\.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt

# Создать файл с секретами (скопировать пример и заполнить)
Copy-Item .env.example .env

# Применить миграции
python manage.py migrate

# Запустить сервер на порту 8003
python manage.py runserver 8003
```

### Frontend

```powershell
cd frontend

# Создать файл с настройками (скопировать пример)
Copy-Item .env.example .env

# Установить зависимости
npm install

# Запустить dev-сервер
npm run dev
```

Фронтенд будет доступен на `http://localhost:5173`, бэкенд — на `http://127.0.0.1:8003`.

## Что реализовано

- Кастомная модель пользователя (`UserProfile`) — адрес доставки, телефон, аватар
- Модели ресторанов с логотипом, временем доставки и минимальной суммой заказа
- Категории и позиции меню с фото, весом и ценой
- Корзина (`Cart` / `CartItem`) — создаётся автоматически при регистрации пользователя
- Заказы (`Order` / `OrderItem`) со статусами: Новый → Готовится → В пути → Доставлен
- Отзывы на рестораны со звёздным рейтингом (1–5)
- REST API на Django REST Framework с JWT-аутентификацией
- Подключение API к фронтенду на React
