import sys
sys.path.append('/data/django/socioscope/event_detection')
import os
import pandas as pd
from models import Tweet
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware

def import_tweets(input_file):
    df = pd.read_csv(input_file)

    for i, row in df.iterrows():
        date = parse_datetime(row['date'])
        if not is_aware(date):
            date = make_aware(date) 

        tweet = Tweet(tweet_id=row['tweet_id'],
                created_at=date,
                user_id=row['user_id'],
                user=row['user'],
                is_retweet=bool(row['is_retweet']),
                is_quote=bool(row['is_quote']),
                text=row['text'],
                quoted_text=row['quoted_text'])

        tweet.save()

if __name__ == "__main__":
    import_tweets('/data_hdd/socioscope/data/tweets.csv.v1')
