# Generated by Django 3.1.7 on 2021-12-12 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0034_auto_20211212_1556'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offering',
            old_name='backup_date',
            new_name='backup_class',
        ),
    ]