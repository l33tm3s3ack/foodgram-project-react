# Generated by Django 3.2.16 on 2023-01-02 15:19

from django.db import migrations, models
import receipts.validators


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0005_auto_20221227_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[receipts.validators.validate_hex], verbose_name='color code of the tag'),
        ),
    ]
