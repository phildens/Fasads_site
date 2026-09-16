from django.db import migrations, models


def set_existing_banner_positions(apps, schema_editor):
    BannerSlide = apps.get_model('shop_part', 'BannerSlide')
    database_alias = schema_editor.connection.alias
    slides = BannerSlide.objects.using(database_alias).order_by('id')
    for position, slide in enumerate(slides, start=1):
        slide.position = position * 10
        slide.save(using=database_alias, update_fields=['position'])


class Migration(migrations.Migration):

    dependencies = [
        ('shop_part', '0033_product_feed_and_prices'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannerslide',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Показывать на сайте'),
        ),
        migrations.AddField(
            model_name='bannerslide',
            name='position',
            field=models.PositiveIntegerField(
                db_index=True,
                default=0,
                help_text='Чем меньше число, тем раньше баннер показывается.',
                verbose_name='Позиция',
            ),
        ),
        migrations.RunPython(set_existing_banner_positions, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name='bannerslide',
            options={
                'ordering': ('position', 'id'),
                'verbose_name': 'Баннер',
                'verbose_name_plural': 'Баннеры',
            },
        ),
    ]
