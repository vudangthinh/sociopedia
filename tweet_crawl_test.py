import os
import sys
import tweepy
import argparse
import json
import time
from queue import Queue
from threading import Thread
from tweepy.models import Status

parser = argparse.ArgumentParser()
parser.add_argument('--key', default='', help='Search keyword')

args = parser.parse_args()
keyword = args.key
keyword = ['trump', 'covid', 'blacklivematter', 'racist', 'tradewar']


class StreamListener(tweepy.StreamListener):
    def __init__(self, keyword, writer, q=Queue()):
        super(StreamListener, self).__init__()
        num_worker_threads = 8
        self.q = q

        for i in range(num_worker_threads):
            t = Thread(target=self.save_tweets)
            t.daemon = True
            t.start()

        self.keyword = keyword
        self.writer = writer

    def on_data(self, raw_data):
        self.q.put(raw_data)

    def save_tweets(self):
        while True:
            raw_data = self.q.get()
            print('#####################################')
            print(raw_data)

            data = json.loads(raw_data)

            if 'in_reply_to_status_id' in data:
                status = Status.parse(self.api, data)

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
                self.writer.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (status.id_str, status.created_at,
                                                                status.user.id_str, status.user.screen_name, is_retweet, is_quote, text, quoted_text))

            self.q.task_done()

    # def on_status(self, status):
    #     is_retweet = False
    #     if hasattr(status, 'retweeted_status'):
    #         is_retweet = True

    #     if hasattr(status, 'extended_tweet'):
    #         text = status.extended_tweet['full_text']
    #     else:
    #         text = status.text

    #     is_quote = hasattr(status, "quoted_status")
    #     quoted_text = ""
    #     if is_quote:
    #         # check if quoted tweet's text has been truncated before recording it
    #         if hasattr(status.quoted_status, "extended_tweet"):
    #             quoted_text = status.quoted_status.extended_tweet["full_text"]
    #         else:
    #             quoted_text = status.quoted_status.text

    #     # remove characters that might cause problems with csv encoding
    #     remove_characters = [",", "\n"]
    #     for c in remove_characters:
    #         text = text.replace(c, " ")
    #         quoted_text = quoted_text.replace(c, " ")

    #     # Tweet.objects.create(status.track, status.created_at, status.user.screen_name, is_retweet, is_quote, text, quoted_text).save()
    #     self.writer.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (status.id_str, status.created_at,
    #                                                      status.user.id_str, status.user.screen_name, is_retweet, is_quote, text, quoted_text))

    def on_limit(self, track):
        print("Rate Limit Exceeded, Sleep for 5 Mins")
        time.sleep(5 * 60)
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

if __name__ == "__main__":
    writer = open(os.path.join("/data_hdd/socioscope/data",
                               'tweets.csv.test.2'), "w", encoding='utf-8')
    writer.write(
        "tweet_id,date,user_id,user,is_retweet,is_quote,text,quoted_text\n")

    isexcept = True
    while isexcept:
        try:
            streamListener = StreamListener(keyword, writer)
            stream = tweepy.Stream(
                auth=api.auth, listener=streamListener, tweet_mode='extended')
            isexcept = False
        except Exception as e:
            print('First exception:', e)
            isexcept = True

    while True:
        try:
            stream.filter(track=keyword, languages=[
                          'en'], stall_warnings=True)  # is_async=True
        except Exception as e:
            print('Second exception:', e)

    writer.close()
    print('Crawling done!!!')
