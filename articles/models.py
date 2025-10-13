from django.db import models
from django.utils import timezone
# Create your models here.
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "pub", "Опубликована"

    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=220, unique=True)
    subtitle = models.CharField("Краткое описание", max_length=400, blank=True)
    cover = models.ImageField("Обложка/превью", upload_to="articles/covers/", blank=True, null=True)
    content = RichTextUploadingField("Текст статьи", config_name="article")
    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateField("Дата публикации", default=timezone.now)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("articles:detail", args=[self.slug])
