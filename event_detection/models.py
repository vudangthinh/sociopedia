from django.db import models
from django.utils import timezone
from datetime import date

# Create your models here.
class Keyword(models.Model):
    keyword = models.CharField(max_length=200)
    search_date = models.DateField(default=date.today)

    def __str__(self):
        return self.keyword
        

class Tweet(models.Model):
    keyword = models.ForeignKey('event_detection.Keyword', on_delete=models.CASCADE, related_name='tweets')
    created_at = models.DateField()
    user = models.CharField(max_length=50)
    is_retweet = models.BooleanField(default=False)
    is_quote = models.BooleanField(default=False)
    text = models.TextField()
    quoted_text = models.TextField()

    def __str__(self):
        return self.text
