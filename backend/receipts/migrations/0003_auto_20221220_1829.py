# Generated by Django 2.2.16 on 2022-12-20 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('receipts', '0002_remove_ingredient_minimal_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='receipt',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='receipt',
            old_name='description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipts.Receipt')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipts.Receipt')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
