# Generated by Django 3.1.7 on 2021-12-10 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0031_auto_20211210_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offering',
            name='price_override',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
    ]