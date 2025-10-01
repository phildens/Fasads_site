# shop_part/management/commands/fix_image_extensions.py
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.fields.files import ImageFieldFile
import os

from shop_part.models import (
    Category, Product, Gallery, BigGalery, SmallGallery,
)  # поля: card_image/image и т.п.

TARGET_MAP = {
    Category:      ["card_image"],
    Product:       ["card_image"],
    Gallery:       ["image"],
    BigGalery:     ["card_image"],
    SmallGallery:  ["image"],
}

# --- НОВОЕ: поддерживаем несколько исходных расширений ---
SOURCE_EXTS = {".png", ".jpg", ".jpeg"}  # при желании добавь ".jfif", ".bmp" и т.д.

def to_webp_name(name: str) -> str | None:
    """
    Если имя заканчивается на одно из SOURCE_EXTS (любой регистр),
    возвращаем путь с .webp, иначе None.
    """
    if not name:
        return None
    root, ext = os.path.splitext(name)
    if ext.lower() in SOURCE_EXTS:
        return root + ".webp"
    return None

class Command(BaseCommand):
    help = "Заменяет в БД ссылки *.png/*.jpg/*.jpeg на *.webp, если соответствующие .webp существуют в storage."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать изменения, без сохранения в БД.",
        )
        parser.add_argument(
            "--only",
            type=str,
            default="",
            help="Список моделей через запятую (Category,Product,Gallery,BigGalery,SmallGallery)",
        )

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        only = {x.strip() for x in (opts["only"] or "").split(",") if x.strip()}

        models = []
        for model, fields in TARGET_MAP.items():
            if only and model.__name__ not in only:
                continue
            models.append((model, fields))

        self.stdout.write(self.style.NOTICE(
            f"Запуск{' (dry-run)' if dry else ''}. Моделей: {', '.join(m.__name__ for m, _ in models)}"
        ))

        updates = 0
        checked = 0

        @transaction.atomic
        def run():
            nonlocal updates, checked
            for model, fields in models:
                for obj in model.objects.all():
                    for field_name in fields:
                        f: ImageFieldFile = getattr(obj, field_name, None)
                        if not f or not f.name:
                            continue

                        # --- ИЗМЕНЕНО: единая функция решает, надо ли конвертировать ---
                        new_name = to_webp_name(f.name)
                        if not new_name:
                            continue  # не png/jpg/jpeg — пропускаем

                        checked += 1

                        # проверяем, что .webp реально существует
                        if default_storage.exists(new_name):
                            self.stdout.write(f"[{model.__name__}#{obj.pk}.{field_name}] {f.name} -> {new_name}")
                            if not dry:
                                setattr(obj, field_name, new_name)
                                obj.save(update_fields=[field_name])
                            updates += 1
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"[{model.__name__}#{obj.pk}.{field_name}] пропуск: нет файла {new_name} в storage"
                            ))

            if dry:
                self.stdout.write(self.style.NOTICE("DRY-RUN: изменения не сохранены (транзакция откатится)."))
                raise transaction.TransactionManagementError("Dry run rollback")

        try:
            run()
        except transaction.TransactionManagementError:
            pass

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Проверено полей: {checked}. Обновлено: {updates}{' (симуляция)' if dry else ''}."
        ))
