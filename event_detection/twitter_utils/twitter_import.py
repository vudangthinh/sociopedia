import os
import pandas as pd
from ..models import Tweet

def import_tweets(input_file):
    df = pd.read_csv(input_file)

    for i, row in df.iterrows():
        tweet = Tweet(tweet_id=row['tweet_id'],
                created_at=row['date'],
                user_id=row['user_id'],
                user=row['user'],
                is_retweet=row['is_retweet'],
                is_quote=row['is_quote'],
                text=row['text'],
                quoted_text=row['quoted_text'])

        tweet.save()

if __name__ == "__main__":
    import_tweets('/data_hdd/socioscope/data/tweets.csv')
