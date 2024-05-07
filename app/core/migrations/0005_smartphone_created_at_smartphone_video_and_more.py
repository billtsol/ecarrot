# Generated by Django 5.0.4 on 2024-05-07 22:13

import core.models
import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_smartphoneimage_smartphone_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='smartphone',
            name='created_at',
            field=models.DateTimeField(db_default=django.db.models.functions.datetime.Now()),
        ),
        migrations.AddField(
            model_name='smartphone',
            name='video',
            field=models.FileField(blank=True, upload_to=core.models.smartphone_video_file_path),
        ),
        migrations.AddField(
            model_name='smartphoneimage',
            name='created_at',
            field=models.DateTimeField(db_default=django.db.models.functions.datetime.Now()),
        ),
        migrations.AddField(
            model_name='tag',
            name='created_at',
            field=models.DateTimeField(db_default=django.db.models.functions.datetime.Now()),
        ),
        migrations.AddField(
            model_name='user',
            name='user_name',
            field=models.CharField(blank=True, default='', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='smartphone',
            name='images',
            field=models.ManyToManyField(blank=True, to='core.smartphoneimage'),
        ),
    ]
