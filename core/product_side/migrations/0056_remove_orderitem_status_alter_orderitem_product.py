# Generated by Django 5.0.4 on 2024-07-02 08:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0055_remove_category_offer_orderitem_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='status',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_side.product'),
        ),
    ]
