# Generated by Django 3.1.7 on 2021-11-26 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0003_user_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
