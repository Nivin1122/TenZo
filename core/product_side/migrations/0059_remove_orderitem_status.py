# Generated by Django 5.0.4 on 2024-07-03 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0058_orderitem_status_delete_transaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='status',
        ),
    ]
