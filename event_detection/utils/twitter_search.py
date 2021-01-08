# https://stackoverflow.com/questions/48034725/tweepy-connection-broken-incompleteread-best-way-to-handle-exception-or-can
import sys
import time
import tweepy
import json
from event_detection.models import Tweet, Keyword, TwitterToken, Knowledge
from queue import Queue
from threading import Thread
from tweepy.models import Status
import dateutil.parser
import time
from django.utils import timezone
from event_detection.utils import knowledge_graph_extract, text_utils
from django.utils.timezone import make_aware

class StreamListener(tweepy.StreamListener):
    def __init__(self, keyword_obj_list, used_token, q=Queue()):
        super(StreamListener, self).__init__()
        num_worker_threads = 8
        self.q = q

        for i in range(num_worker_threads):
            t = Thread(target=self.save_tweets)
            t.daemon = True
            t.start()
        
        self.used_token = used_token
        self.keyword_obj_list = keyword_obj_list
        self.end_date = self.keyword_obj_list[0].end_date
        self.start_time = int(time.time())

    def on_data(self, raw_data):
        self.q.put(raw_data)

        if timezone.now() < self.end_date:
            return True
        else:
            self.used_token.used_count -= 1
            self.used_token.save()
            return False

    def save_tweets(self):
        while True:
            raw_data = self.q.get()

            data = json.loads(raw_data)

            if 'in_reply_to_status_id' in data:
                status = Status.parse(self.api, data)

                is_retweet = False
                retweeted_id = 0
                if hasattr(status, 'retweeted_status'):
                    is_retweet = True
                    retweeted_id = status.retweeted_status.id

                    if hasattr(status.retweeted_status, 'extended_tweet'):
                        text = status.retweeted_status.extended_tweet['full_text']
                    else:
                        text = status.retweeted_status.text

                else:
                    if hasattr(status, 'extended_tweet'):
                        text = status.extended_tweet['full_text']
                    else:
                        text = status.text


                is_quote = hasattr(status, "quoted_status")
                quoted_text = ""
                quoted_id = 0
                if is_quote:
                    quoted_id = status.quoted_status.id

                    if hasattr(status.quoted_status, "extended_tweet"):
                        quoted_text = status.quoted_status.extended_tweet["full_text"]
                    else:
                        quoted_text = status.quoted_status.text

                for keyword_obj in self.keyword_obj_list:
                    keyword = keyword_obj.keyword

                    if keyword.lower() in text.lower() or keyword.lower() in quoted_text.lower():
                        tweet_obj = Tweet.objects.create(keyword=keyword_obj,
                                            tweet_id=status.id,
                                            created_at=make_aware(status.created_at), 
                                            user_id=status.user.id, 
                                            retweeted_id=retweeted_id, 
                                            quoted_id=quoted_id, 
                                            text=text, 
                                            quoted_text=quoted_text)

                        triple_list = knowledge_graph_extract.extract_entity(text_utils.pre_process(text))
                        for triple in triple_list:
                            Knowledge.objects.create(tweet=tweet_obj,
                                                    k_subject=triple[0],
                                                    k_predicate=triple[1],
                                                    k_object=triple[2], 
                                                    subject_type=triple[3],
                                                    object_type=triple[4])


            self.q.task_done()

    # def on_limit(self, track):
    #     print("Rate Limit Exceeded, Sleep for 5 Mins")
    #     time.sleep(5 * 60)
    #     return True

    def on_error(self, status_code):
        print('Encountered streaming error (', status_code, ')')
        return False
        # if status_code == 420 or status_code == 401:
        #     return False
        # else:
        #     return True

def stream_search(keyword_obj_list):
    keywords = set()
    for keyword_obj in keyword_obj_list:
        keywords.add(keyword_obj.keyword)

    tokens = TwitterToken.objects.all() # filter only token of admin and current user???
    used_token = None
    for token in tokens:
        if token.used_count < 2:
            used_token = token
            token.used_count += 1
            token.save()
            break
    
    if used_token is None:
        return None
    
    used_token.consumer_key = '9TvVKS8HRroMN4wQtBdzNA'
    used_token.consumer_secret = 'BrmSzXi4sGzDiRdj7kbPHMRLQNMkbpHeDqtLhWPhU'
    used_token.access_token = '1287392767-m7gcpy3wkpNpvMpywC9wwBTzIivWVXvLabhZMlA'
    used_token.access_token_secret = 'RHNCzFoLOpUHZhLQu7mDkJGsgtA3xtpKm35596ZfuRY'

    auth = tweepy.OAuthHandler(used_token.consumer_key, used_token.consumer_secret)
    auth.set_access_token(used_token.access_token, used_token.access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # stream_time_limit = 1 * 60 # 7 * 24 * 60 * 60
    streamListener = StreamListener(keyword_obj_list, used_token)
    stream = tweepy.Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')

    print("Crawling keywords: ", keywords)
    stream.filter(track=keywords, is_async=True)
    return stream

    