from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UserProfile, Restaurant, MenuCategory, MenuItem,
    Cart, CartItem, Order, OrderItem, RestaurantReview,
)


# ─── Инлайны ──────────────────────────────────────────────────────────────────
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0


class MenuCategoryInline(admin.TabularInline):
    model = MenuCategory
    extra = 0


# ─── Пользователь ─────────────────────────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'delivery_address', 'is_staff')
    search_fields = ('username', 'email', 'phone_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. информация', {'fields': ('delivery_address', 'phone_number', 'avatar')}),
    )


# ─── Ресторан ─────────────────────────────────────────────────────────────────
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'delivery_time', 'min_order_price', 'is_open', 'get_avg_rating')
    list_filter = ('is_open',)
    search_fields = ('name', 'address', 'description')
    inlines = [MenuCategoryInline]


# ─── Категория меню ───────────────────────────────────────────────────────────
@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')
    list_filter = ('restaurant',)
    search_fields = ('name',)
    inlines = [MenuItemInline]


# ─── Позиция меню ─────────────────────────────────────────────────────────────
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'weight', 'is_available', 'category')
    list_filter = ('is_available', 'category__restaurant')
    search_fields = ('name', 'description')


# ─── Корзина ──────────────────────────────────────────────────────────────────
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_price')
    search_fields = ('user__username',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'item', 'quantity')


# ─── Заказ ────────────────────────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'delivery_address', 'created_date', 'get_total_price')
    list_filter = ('status',)
    search_fields = ('user__username', 'delivery_address')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', 'price')


# ─── Отзыв ────────────────────────────────────────────────────────────────────
@admin.register(RestaurantReview)
class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'stars', 'created_date')
    list_filter = ('stars', 'restaurant')
    search_fields = ('user__username', 'comment')
