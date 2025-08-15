from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_part', '0016_alter_biggalery_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='Фамилия')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='Телефон')),
                ('description', models.TextField(blank=True, verbose_name='Краткое описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Заявка на обратный звонок',
                'verbose_name_plural': 'Заявки на обратный звонок',
                'ordering': ['-created_at'],
            },
        ),
        migrations.DeleteModel(
            name='Galery',
        ),
    ]
