# Generated by Django 3.1.7 on 2021-11-27 17:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0014_semester_hide'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offering',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='semester',
            name='hide',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=8)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('total', models.DecimalField(decimal_places=2, max_digits=8)),
                ('completed', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planned_absences', models.CharField(blank=True, max_length=1024, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('offering', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='enrollment.offering')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='enrollment.order')),
            ],
        ),
    ]
