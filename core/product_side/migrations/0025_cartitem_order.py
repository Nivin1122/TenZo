# Generated by Django 5.0.4 on 2024-05-20 05:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0024_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='product_side.order'),
        ),
    ]