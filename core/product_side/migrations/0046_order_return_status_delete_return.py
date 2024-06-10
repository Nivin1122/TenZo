# Generated by Django 5.0.4 on 2024-06-10 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_side', '0045_remove_wallettransaction_wallet_return_delete_wallet_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='return_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled'), ('Returned', 'Returned')], default='Pending', max_length=50),
        ),
        migrations.DeleteModel(
            name='Return',
        ),
    ]
