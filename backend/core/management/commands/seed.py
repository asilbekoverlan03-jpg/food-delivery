"""
python manage.py seed
Наполняет БД тестовыми данными: рестораны, меню, отзывы, суперпользователь.
Валюта: кыргызский сом (KGS).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Restaurant, MenuCategory, MenuItem, RestaurantReview

User = get_user_model()

RESTAURANTS = [
    {
        "name": "Burger King",
        "address": "ул. Ленина, 1",
        "description": "Вкусные бургеры и картошка фри",
        "delivery_time": 25,
        "min_order_price": 350,
        "is_open": True,
        "categories": [
            {
                "name": "Бургеры",
                "items": [
                    {"name": "Воппер",       "price": 320, "weight": 300, "description": "Классический бургер"},
                    {"name": "Чикен Роял",   "price": 280, "weight": 250, "description": "С курицей"},
                    {"name": "Бэкон Кинг",   "price": 390, "weight": 350, "description": "С двойным беконом"},
                    {"name": "Вегги Бургер", "price": 220, "weight": 200, "description": "Без мяса"},
                ],
            },
            {
                "name": "Напитки и десерты",
                "items": [
                    {"name": "Кола 0.5",      "price": 90,  "weight": 500, "description": ""},
                    {"name": "Молочный шейк", "price": 150, "weight": 300, "description": "Клубничный"},
                ],
            },
        ],
    },
    {
        "name": "Суши Мастер",
        "address": "пр. Победы, 15",
        "description": "Японская кухня — роллы и суши",
        "delivery_time": 40,
        "min_order_price": 500,
        "is_open": True,
        "categories": [
            {
                "name": "Роллы",
                "items": [
                    {"name": "Филадельфия",  "price": 450, "weight": 240, "description": "Лосось, сыр"},
                    {"name": "Калифорния",   "price": 380, "weight": 220, "description": "Краб, авокадо"},
                    {"name": "Дракон",       "price": 520, "weight": 260, "description": "Угорь, авокадо"},
                    {"name": "Спайси тунец", "price": 410, "weight": 230, "description": "Тунец, острый соус"},
                ],
            },
            {
                "name": "Супы",
                "items": [
                    {"name": "Мисо суп", "price": 160, "weight": 250, "description": "Классический"},
                    {"name": "Рамен",    "price": 340, "weight": 400, "description": "С курицей"},
                    {"name": "Том Ям",   "price": 390, "weight": 350, "description": "Острый", "is_available": False},
                ],
            },
        ],
    },
    {
        "name": "Пицца Хаус",
        "address": "ул. Гагарина, 8",
        "description": "Пицца на дровяной печи",
        "delivery_time": 35,
        "min_order_price": 450,
        "is_open": True,
        "categories": [
            {
                "name": "Пицца",
                "items": [
                    {"name": "Маргарита",    "price": 420, "weight": 500, "description": "Томат, моцарелла"},
                    {"name": "Пепперони",    "price": 490, "weight": 550, "description": "С острой колбасой"},
                    {"name": "Четыре сыра",  "price": 560, "weight": 530, "description": "Ассорти сыров"},
                    {"name": "Гавайская",    "price": 470, "weight": 520, "description": "Ветчина, ананас"},
                    {"name": "Барбекю",      "price": 510, "weight": 560, "description": "Курица, BBQ соус"},
                ],
            },
            {
                "name": "Закуски",
                "items": [
                    {"name": "Чесночный хлеб",        "price": 130, "weight": 150, "description": ""},
                    {"name": "Картофельные дольки",    "price": 170, "weight": 200, "description": ""},
                ],
            },
        ],
    },
    {
        "name": "Закрытый ресторан",
        "address": "ул. Тихая, 99",
        "description": "Мы временно закрыты",
        "delivery_time": 60,
        "min_order_price": 300,
        "is_open": False,
        "categories": [
            {
                "name": "Меню",
                "items": [
                    {"name": "Суп дня", "price": 200, "weight": 300, "description": ""},
                ],
            },
        ],
    },
]

REVIEWS = [
    ("Burger King",  "user1", 5, "Отличные бургеры, быстрая доставка!"),
    ("Burger King",  "user2", 4, "Всё хорошо, но немного дорого."),
    ("Суши Мастер",  "user1", 5, "Лучшая Филадельфия в городе!"),
    ("Суши Мастер",  "user3", 3, "Доставка задержалась на 20 минут."),
    ("Пицца Хаус",   "user2", 5, "Пепперони — просто огонь!"),
    ("Пицца Хаус",   "user3", 4, "Вкусно, но порция маловата."),
]


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными (цены в сомах)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Суперпользователь
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write("  superuser admin / admin123")

        # Тестовые пользователи для отзывов
        for uname in ("user1", "user2", "user3"):
            if not User.objects.filter(username=uname).exists():
                User.objects.create_user(uname, f"{uname}@example.com", "pass1234")
                self.stdout.write(f"  user {uname} / pass1234")

        # Рестораны, категории, блюда
        for rdata in RESTAURANTS:
            categories = rdata.pop("categories")
            rest, created = Restaurant.objects.get_or_create(
                name=rdata["name"], defaults=rdata
            )
            if created:
                self.stdout.write(f"  restaurant: {rest.name}")
            for cdata in categories:
                items = cdata.pop("items")
                cat, _ = MenuCategory.objects.get_or_create(
                    name=cdata["name"], restaurant=rest
                )
                for idata in items:
                    MenuItem.objects.get_or_create(
                        name=idata["name"], category=cat,
                        defaults={
                            "price":        idata["price"],
                            "weight":       idata.get("weight", 0),
                            "description":  idata.get("description", ""),
                            "is_available": idata.get("is_available", True),
                        },
                    )
            rdata["categories"] = categories

        # Отзывы
        for rest_name, uname, stars, comment in REVIEWS:
            try:
                rest = Restaurant.objects.get(name=rest_name)
                user = User.objects.get(username=uname)
                RestaurantReview.objects.get_or_create(
                    restaurant=rest, user=user,
                    defaults={"stars": stars, "comment": comment},
                )
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS("\nБаза данных заполнена!"))
        self.stdout.write("  Логин: admin / admin123")
        self.stdout.write("  Тестовые юзеры: user1, user2, user3 / pass1234")
        self.stdout.write("  Цены в сомах (KGS)")
