# Generated by Django 5.0.4 on 2024-04-24 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0002_rename_is_listed_category_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
