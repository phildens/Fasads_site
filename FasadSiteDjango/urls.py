"""
URL configuration for FasadSiteDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from shop_part import views
from shop_part.views import ProductListView, FAQView

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Главная страница
    path('', views.index, name='home'),

    # Страница категорий (рендерит category.html)
    path('categories', views.category, name='cats'),

    # Страница «О нас»
    path('about', views.about, name='about'),

    # Страница одного продукта (рендерит category.html, если надо)
    path('product', views.products, name='product_detail'),

    # DRF API: список продуктов в JSON
    path('products/', ProductListView.as_view(), name='products_api'),

    # Страница галереи объектов
    path('galery/', views.galery, name='galery'),
    path("contact-request/create/", views.contact_request_create, name="contact_request_create"),
    path("faq/", FAQView.as_view(), name="faq"),
]

# Статика (CSS, JS, шрифты) — отдаётся через STATIC_URL
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Медиа (загруженные изображения) — работает только при DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
