# Generated by Django 3.1.7 on 2021-11-27 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0019_auto_20211127_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
