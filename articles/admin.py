from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at")
    list_filter = ("status", "published_at")
    search_fields = ("title", "subtitle", "content")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "subtitle", "cover", "status", "published_at")}),
        ("Содержимое", {"fields": ("content",)}),
    )
