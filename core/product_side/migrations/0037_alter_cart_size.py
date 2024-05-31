# Generated by Django 5.0.4 on 2024-05-30 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0036_alter_cart_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='size',
            field=models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large')], default='M', max_length=2),
        ),
    ]
