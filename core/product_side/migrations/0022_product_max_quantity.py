# Generated by Django 5.0.4 on 2024-05-16 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0021_alter_product_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_quantity',
            field=models.PositiveIntegerField(default=5),
        ),
    ]
