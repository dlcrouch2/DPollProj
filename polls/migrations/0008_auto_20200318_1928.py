# Generated by Django 3.0.4 on 2020-03-19 00:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_auto_20200318_1517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='date',
        ),
        migrations.AddField(
            model_name='vote',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date entered'),
            preserve_default=False,
        ),
    ]
