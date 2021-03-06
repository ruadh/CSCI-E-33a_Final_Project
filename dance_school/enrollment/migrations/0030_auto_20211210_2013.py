# Generated by Django 3.1.7 on 2021-12-10 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0029_auto_20211210_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='vacation',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vacations', to='enrollment.semester'),
        ),
    ]
