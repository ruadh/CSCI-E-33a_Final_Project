# Generated by Django 3.1.7 on 2021-11-27 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0010_auto_20211127_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='qualifications',
            field=models.CharField(default='a', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='level',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
