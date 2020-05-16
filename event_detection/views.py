from django.shortcuts import render, redirect
from .forms import KeywordForm
from .twitter_utils import twitter_search
from django.http import JsonResponse
from .models import Keyword, Tweet
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder
from plotly.offline import plot
import plotly.graph_objs as go
import collections
from datetime import datetime

# Create your views here.

def search(request):
    # return render(request, 'base.html')
    if request.method == 'POST':
        form = KeywordForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            # Show tweets which include keyword
            # twitter_search.stream_search(post)
            # keyword_objs = Keyword.objects.filter(keyword=post.keyword)
            # tweets = Tweet.objects.filter(keyword=keyword_objs[0])
            # tweet_texts = []
            # for tweet in tweets:
            #     tweet_texts.append(tweet.text)

            result = Tweet.objects.filter(text__contains=post.keyword).order_by('created_at')
            first_tweet = result.first()
            first_time = first_tweet.created_at.timestamp()
            last_tweet = result.last()
            last_time = last_tweet.created_at.timestamp()
            
            denominator = 60
            time_range = int((last_time - first_time) / denominator)
            x_data = [i for i in range(time_range)]

            counter = collections.Counter()
            for tweet in result.iterator():
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
            plot_div = plot(fig,
                            output_type='div', 
                            include_plotlyjs=False,
                            show_link=False, 
                            link_text="")
                                
            return render(request, 'keyword_search.html', {'title': 'search', 'form': form, 'plot_div': plot_div})
    else:
        form = KeywordForm()
        return render(request, 'keyword_search.html', {'title': 'search', 'form': form})

@csrf_exempt
def update_search_result(request):
    '''
    Update search result in real-time using ajax (not work correctly)
    '''
    keyword = request.POST.get('keyword', None)
    keyword_objs = Keyword.objects.filter(keyword=keyword)
    tweets = Tweet.objects.filter(keyword=keyword_objs[0])
    tweet_texts = []
    for tweet in tweets:
        tweet_texts.append(tweet.text)
    data = {'tweets': tweet_texts}
    
    return JsonResponse(data)

def system_management(request):
    return render(request, 'base.html', {'title': 'system_management'})

def about(request):
    return render(request, 'about.html', {'title': 'about'})