# Generated by Django 2.2.16 on 2022-12-19 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='minimal_amount',
        ),
    ]
