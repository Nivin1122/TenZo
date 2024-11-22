# Generated by Django 5.0.4 on 2024-07-02 11:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0056_remove_orderitem_status_alter_orderitem_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='product_side.wallet')),
            ],
        ),
    ]