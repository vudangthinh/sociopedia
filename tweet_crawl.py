import os
import sys
import tweepy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--key', default='', help='Search keyword')

args = parser.parse_args()
keyword = args.key
keyword = ['donald trump', 'iphone', 'macbook', 'covid-19', 'corona virus', 'kim jong-un']

class StreamListener(tweepy.StreamListener):
    def __init__(self, keyword, writer):
        super(StreamListener, self).__init__()
        self.keyword = keyword
        self.writer = writer

    def on_status(self, status):
        is_retweet = False
        if hasattr(status, 'retweeted_status'):
            is_retweet = True

        if hasattr(status, 'extended_tweet'):
            text = status.extended_tweet['full_text']
        else:
            text = status.text

        is_quote = hasattr(status, "quoted_status")
        quoted_text = ""
        if is_quote:
            # check if quoted tweet's text has been truncated before recording it
            if hasattr(status.quoted_status, "extended_tweet"):
                quoted_text = status.quoted_status.extended_tweet["full_text"]
            else:
                quoted_text = status.quoted_status.text

        # remove characters that might cause problems with csv encoding
        remove_characters = [",", "\n"]
        for c in remove_characters:
            text = text.replace(c, " ")
            quoted_text = quoted_text.replace(c, " ")
        
        # Tweet.objects.create(status.track, status.created_at, status.user.screen_name, is_retweet, is_quote, text, quoted_text).save()
        self.writer.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (status.id_str,status.created_at,status.user.id_str,status.user.screen_name,is_retweet,is_quote,text,quoted_text))

    def on_error(self, status_code):
        print('Encountered streaming error (', status_code, ')')
        sys.exit()


consumer_key = '9TvVKS8HRroMN4wQtBdzNA'
consumer_secret = 'BrmSzXi4sGzDiRdj7kbPHMRLQNMkbpHeDqtLhWPhU'
access_token = '1287392767-m7gcpy3wkpNpvMpywC9wwBTzIivWVXvLabhZMlA'
access_token_secret = 'RHNCzFoLOpUHZhLQu7mDkJGsgtA3xtpKm35596ZfuRY'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if __name__ == "__main__":
    writer = open(os.path.join("/data_hdd/socioscope/data", 'tweets.csv'), "w", encoding='utf-8')
    writer.write("tweet_id,date,user_id,user,is_retweet,is_quote,text,quoted_text\n")

    streamListener = StreamListener(keyword, writer)
    stream = tweepy.Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')

    while True:
        try:
            stream.filter(track=keyword, languages=['en'], stall_warnings=True) #is_async=True
        except Exception as e:
            print(e)
            continue

    writer.close()