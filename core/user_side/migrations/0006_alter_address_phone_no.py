# Generated by Django 5.0.4 on 2024-05-15 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_side', '0005_address_name_address_phone_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='phone_no',
            field=models.IntegerField(null=True),
        ),
    ]
