# Generated by Django 3.1.7 on 2021-11-27 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0015_auto_20211127_1737'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='subtotal',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
        migrations.AlterField(
            model_name='order',
            name='completed',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
