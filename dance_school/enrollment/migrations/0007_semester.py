# Generated by Django 3.1.7 on 2021-11-27 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0006_auto_20211126_1945'),
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('registration_open', models.DateTimeField()),
                ('registration_close', models.DateTimeField()),
            ],
        ),
    ]
