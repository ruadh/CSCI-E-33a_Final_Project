# Generated by Django 3.1.7 on 2021-12-12 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0033_offering_hourly_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offering',
            name='backup_date',
            field=models.DateTimeField(),
        ),
    ]