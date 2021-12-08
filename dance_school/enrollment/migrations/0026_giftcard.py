# Generated by Django 3.1.7 on 2021-12-07 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0025_auto_20211205_1912'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiftCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16)),
                ('expiration_month', models.CharField(max_length=2)),
                ('expiration_year', models.CharField(max_length=4)),
                ('pin', models.CharField(max_length=4)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]