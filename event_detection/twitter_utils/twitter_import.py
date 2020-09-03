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


# tweet_list = [] 
# with open('/data_hdd/socioscope/data/tweets.csv', 'r') as file:  
#     for i, line in enumerate(file):  
#         if i > 0 and 'donald trump' in line.lower():  
#             try: 
#                 if i % 100 == 0: 
#                     Tweet.objects.bulk_create(tweet_list) 
#                     tweet_list = [] 
#                 row = line.split(',')  
#                 if len(row) != 8: 
#                     continue 
#                 date = parse_datetime(row[1])  
#                 if not is_aware(date):  
#                     date = make_aware(date)   
                
#                 tweet = Tweet(keyword=trump_key,  
#                     tweet_id=row[0],  
#                     created_at=date,  
#                     user_id=row[2],  
#                     user=row[3],  
#                     is_retweet=bool(row[4]),  
#                     is_quote=bool(row[5]),  
#                     text=row[6],  
#                     quoted_text=row[7]) 
                    
#                 tweet_list.append(tweet)  
#             except Exception as e: 
#                 print(f'line: {i} - ', e) 
