# Generated by Django 5.0.4 on 2024-06-13 09:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_side', '0007_shipping_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping_address',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
