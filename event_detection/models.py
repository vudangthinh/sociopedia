import re
from django.db import models
from django.utils import timezone
from datetime import date
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class TwitterToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=User.objects.get(pk=1).id, related_name='tokens')
    consumer_key = models.CharField(max_length=100)
    consumer_secret = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    access_token_secret = models.CharField(max_length=100)
    used_count = models.IntegerField(default=0)

    def __str__(self):
        return self.consumer_key


class Keyword(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=User.objects.get(pk=1).id, related_name='keywords')
    keyword = models.CharField(max_length=200)
    search_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_streaming = models.BooleanField(default=False)

    def __str__(self):
        return self.keyword


class Tweet(models.Model):
    keyword = models.ForeignKey('event_detection.Keyword', on_delete=models.CASCADE, related_name='tweets')
    tweet_id = models.BigIntegerField()
    created_at = models.DateTimeField()
    user_id = models.BigIntegerField()
    # user = models.CharField(max_length=50)
    is_retweet = models.BooleanField(default=False)
    is_quote = models.BooleanField(default=False)
    text = models.TextField()
    quoted_text = models.TextField()

    def __str__(self):
        return self.text
