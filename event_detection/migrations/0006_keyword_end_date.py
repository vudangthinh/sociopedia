# Generated by Django 3.0.5 on 2020-08-31 06:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event_detection', '0005_keyword_is_streaming'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]