# Generated by Django 5.0.4 on 2024-04-24 07:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='is_listed',
            new_name='is_deleted',
        ),
    ]
