# Generated by Django 3.0.5 on 2020-05-08 04:36

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=200)),
                ('search_date', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField()),
                ('user', models.CharField(max_length=50)),
                ('is_retweet', models.BooleanField(default=False)),
                ('is_quote', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('quoted_text', models.TextField()),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tweet', to='event_detection.Keyword')),
            ],
        ),
    ]
