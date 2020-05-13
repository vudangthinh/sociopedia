import sys
import tweepy
from .models import Tweet

class StreamListener(tweepy.StreamListener):
    def __init__(self, keyword, tweet_limit):
        super(StreamListener, self).__init__()

        self.keyword = keyword
        self.tweet_limit = tweet_limit
        self.tweet_counter = 0

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
            text.replace(c, " ")
            quoted_text.replace(c, " ")
        
        # Tweet.objects.create(status.track, status.created_at, status.user.screen_name, is_retweet, is_quote, text, quoted_text).save()
        with open("/data/django/socioscope/out.csv", "a", encoding='utf-8') as f:
            f.write("%s,%s,%s,%s,%s,%s\n" % (status.created_at, status.user.screen_name, is_retweet, is_quote, text, quoted_text))

        Tweet.objects.create(keyword=self.keyword,
                            created_at=status.created_at, 
                            user=status.user.screen_name, 
                            is_retweet=is_retweet, 
                            is_quote=is_quote, 
                            text=text, 
                            quoted_text=quoted_text)

        self.tweet_counter += 1
        if self.tweet_counter > self.tweet_limit:
            return False
        else:
            return True

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

def stream_search(keyword):
    with open("/data/django/socioscope/out.csv", "w", encoding='utf-8') as f:
        f.write("date,user,is_retweet,is_quote,text,quoted_text\n")

    tweet_limit = 50
    streamListener = StreamListener(keyword, tweet_limit)
    stream = tweepy.Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')
    stream.filter(track=[keyword.keyword], languages=['en']) #is_async=True
    