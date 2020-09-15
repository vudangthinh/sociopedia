import collections
from datetime import datetime, timedelta

from plotly.offline import plot
import plotly.graph_objs as go

from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Keyword, Tweet
from wordcloud import WordCloud, STOPWORDS

import collections
import string
import re
import nltk
from nltk.util import ngrams
nltk.download('punkt')

def plot_distribution(tweet_list, time_option="Option 1"):
    first_tweet = tweet_list.first()
    first_time = first_tweet.created_at.timestamp()
    last_tweet = tweet_list.last()
    last_time = last_tweet.created_at.timestamp()
    
    denominator = 60
    if time_option == 'Option 1': # minute
        denominator = 60
    elif time_option == 'Option 2': # hour
        denominator = 60 * 60
    elif time_option == 'Option 3': # day
        denominator = 60 * 60 * 24
    elif time_option == 'Option 4': # week
        denominator = 60 * 60 * 24 * 7
    elif time_option == 'Option 5': # month
        denominator = 60 * 60 * 24 * 30
        
    time_range = int((last_time - first_time) / denominator)
    if time_range < 1: 
        time_range = 1
    x_data = [i for i in range(time_range)]

    counter = collections.Counter()
    for tweet in tweet_list.iterator():
        date_time = tweet.created_at.timestamp()
        counter.update([int((date_time - first_time) / denominator)])
    
    y_data = []
    x_data_date = []
    for x in x_data:
        date = datetime.fromtimestamp(x * denominator + first_time)
        x_data_date.append(date)
        if x in counter:
            y_data.append(counter[x])
        else:
            y_data.append(0)

    fig = go.Figure()
    bar = go.Bar(x=x_data_date, y=y_data)
    fig.add_trace(bar)
    fig.update_layout(
        xaxis=dict(
            title='Time',
            type='date'
        ),
        yaxis=dict(
            title='Number of tweets'
        ),
        title='Tweets Distribution'
    )
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    plot_div = plot(fig,
                    output_type='div', 
                    include_plotlyjs=False,
                    show_link=False, 
                    link_text="")

    return plot_div


def paging_tweets(tweet_list, page):
    tweet_per_page = 50
    tweet_index = [i + 1 for i in range((int(page) - 1) * tweet_per_page, int(page) * tweet_per_page)]
    paginator = Paginator(tweet_list, tweet_per_page)
    try:
        tweets = paginator.page(page)
    except PageNotAnInteger:
        tweets = paginator.page(1)
    except EmptyPage:
        tweets = paginator.page(paginator.num_pages)

    page_start = tweets.number - 2
    page_end = tweets.number + 3
    if page_start <= 0: page_start = 1
    if page_end > tweets.paginator.page_range[-1] + 1: page_end = tweets.paginator.page_range[-1] + 1

    page_range = list(range(page_start, page_end))
    if page_start > 2:
        page_range = [1, -1] + page_range
    elif page_start > 1:
        page_range = [1] + page_range
    if page_end < tweets.paginator.page_range[-1]:
        page_range = page_range + [-1, tweets.paginator.page_range[-1]]
    elif page_end < tweets.paginator.page_range[-1] + 1:
        page_range = page_range + [tweets.paginator.page_range[-1]]

    for tweet in tweets:
        tweet.user_id = str(tweet.user_id)
        tweet.tweet_id = str(tweet.tweet_id)
        tweet.created_at_str = tweet.created_at.strftime("%Y/%m/%d, %H:%M:%S")

    return tweets, tweet_index, page_range

def get_tweet_in_time_range(pk, start_date, end_date):
    if start_date is None or start_date == "":
        start_date = datetime.strptime("1970-01-01 00:00", "%Y-%m-%d %H:%M")
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")

    if end_date is None or end_date == "":
        end_date = timezone.now()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")

    tweet_list = Tweet.objects.filter(keyword=pk, created_at__range=[start_date, end_date])
    return tweet_list

def analyse_wordcloud(tweet_list, request):
    text = " ".join([tweet.text for tweet in tweet_list])

    wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=1200, height=700, collocations=False).generate(text)
    wordcloud.to_file(f"event_detection/static/event_detection/{request.user.username}.png")

    return f'event_detection/{request.user.username}.png'

def ngrams_visualization(counter, ngrams):
    count_list = counter.most_common()[:20]
    # count_list.reverse()

    fig = go.Figure()
    bar = go.Bar(x=[' '.join(value[0]) for value in count_list], y=[value[1] for value in count_list])
    fig.add_trace(bar)
    fig.update_layout(
        xaxis=dict(
            title=f'{ngrams}-grams',
        ),
        yaxis=dict(
            title='Count'
        ),
        title=f'{ngrams}-grams Distribution'
    )

    plot_div = plot(fig,
                    output_type='div', 
                    include_plotlyjs=False,
                    show_link=False, 
                    link_text="")

    return plot_div

def analyse_ngrams(tweet_list):
    tokens = nltk.word_tokenize('. '.join([tweet.text for tweet in tweet_list]).translate(str.maketrans('', '', string.punctuation)))
    one_gram = ngrams(tokens, 1)
    one_gram_counter = collections.Counter(one_gram)
    one_gram_plot_div = ngrams_visualization(one_gram_counter, 1)

    two_gram = ngrams(tokens, 2)
    two_gram_counter = collections.Counter(two_gram)
    two_gram_plot_div = ngrams_visualization(two_gram_counter, 2)

    thr_gram = ngrams(tokens, 3)
    thr_gram_counter = collections.Counter(thr_gram)
    thr_gram_plot_div = ngrams_visualization(thr_gram_counter, 3)

    return one_gram_plot_div, two_gram_plot_div, thr_gram_plot_div