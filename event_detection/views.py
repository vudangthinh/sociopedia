from django.shortcuts import render, redirect
from .forms import KeywordSearchForm, KeywordAnalysisForm, SelectTimeRangeForm
from .twitter_utils import twitter_search, knowledge_extract
from django.http import JsonResponse
from .models import Keyword, Tweet
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder
from plotly.offline import plot
import plotly.graph_objs as go
import collections
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from wordcloud import WordCloud, STOPWORDS
import threading
from django.core import serializers
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from . import utils


# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def search(request):
    if request.method == 'POST':
        form = KeywordSearchForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            print('end_date', post.end_date)

            keyword_obj_list = []
            for keyword in post.keyword.strip().split(','):
                keyword_obj = Keyword.objects.create(user=request.user, keyword=keyword.strip(), search_date=timezone.now(), end_date=post.end_date)
                keyword_obj_list.append(keyword_obj)

            stream = twitter_search.stream_search(keyword_obj_list)
            if stream is None:
                pass
            # download_thread = threading.Thread(target=twitter_search.stream_search, args=(post, ))
            # download_thread.start()
            # keyword_objs = Keyword.objects.filter(keyword=post.keyword)
            # tweets = Tweet.objects.filter(keyword=keyword_objs[0])
            # tweet_texts = []
            # for tweet in tweets:
            #     tweet_texts.append(tweet.text)

            return render(request, 'keyword_search.html', {'title': 'search', 'form': form, 'keyword': post.keyword})
    else:
        form = KeywordSearchForm()
        end_date = timezone.now() + timedelta(7)
        form['end_date'].initial = end_date
        min_date = timezone.now().strftime("%Y/%m/%d")
        max_date = end_date.strftime("%Y/%m/%d")
        return render(request, 'keyword_search.html', {'title': 'search', 'form': form, 'min_date': min_date, 'max_date': max_date})

@login_required
def data_analysis(request):
    if request.method == 'POST':
        form = KeywordAnalysisForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # post.save()

            # Show tweets which include keyword
            # twitter_search.stream_search(post)
            # keyword_objs = Keyword.objects.filter(keyword=post.keyword)
            # tweets = Tweet.objects.filter(keyword=keyword_objs[0])
            # tweet_texts = []
            # for tweet in tweets:
            #     tweet_texts.append(tweet.text)

            keyword = Keyword.objects.filter(keyword=post.keyword.lower())[0]
            result = keyword.tweets.all().values('created_at')
            # result = Tweet.objects.filter(text__contains=post.keyword).order_by('created_at')

            first_tweet = result.first()
            first_time = first_tweet['created_at'].timestamp()
            last_tweet = result.last()
            last_time = last_tweet['created_at'].timestamp()
            
            denominator = 60
            time_option = form.cleaned_data['time_option']
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
            for tweet in result.iterator():
                date_time = tweet['created_at'].timestamp()
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
                                
            return render(request, 'keyword_analysis.html', {'title': 'keyword_analysis', 'form': form, 'plot_div': plot_div})
    else:
        form = KeywordAnalysisForm()
        return render(request, 'keyword_analysis.html', {'title': 'keyword_analysis', 'form': form})

def word_cloud(request):
    if request.method == 'POST':
        form = KeywordSearchForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            if post.keyword.lower() == 'covid':
                post.keyword = 'donald trump'
            else:
                post.keyword = 'covid'

            keyword = Keyword.objects.filter(keyword=post.keyword.lower())[0]
            result = keyword.tweets.all().values('text').order_by('?')[:10000]

            text = ''
            for tweet in result.iterator():
                text += tweet['text'] + ' '

            wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=1200, height=700, collocations=False).generate(text)
            wordcloud.to_file(f"event_detection/static/event_detection/{request.user.username}.png")
                                
            return render(request, 'word_cloud.html', {'title': 'word_cloud', 'form': form, 'wordcloud': f'event_detection/{request.user.username}.png'})
    else:
        form = KeywordSearchForm()
        return render(request, 'word_cloud.html', {'title': 'word_cloud', 'form': form})

def knowledge_graph(request):
    if request.method == 'POST':
        form = KeywordSearchForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            
            if post.keyword.lower() == 'covid':
                post.keyword = 'donald trump'
            else:
                post.keyword = 'covid'

            keyword = Keyword.objects.filter(keyword=post.keyword.lower())[0]
            result = keyword.tweets.all().values('text').order_by('?')[:100]
            text_list = []
            for tweet in result.iterator():
                text_list.append(tweet['text'])

            plot_div = knowledge_extract.extract_knowledge_graph(text_list)          
            return render(request, 'knowledge_graph.html', {'title': 'word_cloud', 'form': form, 'plot_div': plot_div})
    else:
        form = KeywordSearchForm()
        return render(request, 'knowledge_graph.html', {'title': 'word_cloud', 'form': form})

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

@login_required
def system_management(request):
    keywords = request.user.keywords.all()
    current_time = timezone.now()
    for keyword in keywords:
        if keyword.end_date < current_time:
            keyword.is_streaming = False
        else:
            keyword.is_streaming = True
            
        keyword.n_tweets = keyword.tweets.count()

    return render(request, 'system_management.html', {'title': 'system_management', 'keywords': keywords})

@csrf_exempt
def delete_keyword(request):
    if request.method == "GET":
        keyword_id = request.GET.get('keyword_id', None)
        Keyword.objects.filter(id=keyword_id).delete()
        
        return JsonResponse({"id": keyword_id}, status=200)

    return JsonResponse({"error": "not ajax request"}, status=400)

@login_required
def view_tweets(request, pk):
    tweet_list = Tweet.objects.filter(keyword=pk)
    plot_div = utils.plot_distribution(tweet_list)

    page = request.GET.get('page', 1)
    tweets, tweet_index, page_range = utils.paging_tweets(tweet_list, page)
    
    form = SelectTimeRangeForm()

    # page_settings = {}
    # page_settings['has_other_pages'] = tweets.has_other_pages()
    # page_settings['has_previous'] = tweets.has_previous()
    # page_settings['has_next'] = tweets.has_next()
    # page_settings['previous_page_number'] = tweets.previous_page_number()
    # page_settings['next_page_number'] = tweets.next_page_number()

    return render(request, 'view_tweets.html', {'title': 'system_management',
                                                'keyword_id': pk,
                                                'tweets': tweets.object_list, 
                                                'page_settings': tweets,
                                                'tweet_index': tweet_index, 
                                                'page_range': page_range,
                                                'plot_div': plot_div,
                                                'form': form})

@csrf_exempt
def filter_tweets_intime(request):
    if request.is_ajax and request.method == "POST":
        keyword_id = request.POST.get('id', None)
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
        page_n = request.POST.get('page_n', None)
        tweet_list = utils.get_tweet_in_time_range(keyword_id, start_date, end_date)

        page = int(page_n)
        tweets, tweet_index, page_range = utils.paging_tweets(tweet_list, page)

        page_settings = {}
        page_settings['has_other_pages'] = tweets.has_other_pages()
        page_settings['has_previous'] = tweets.has_previous()
        page_settings['number'] = tweets.number
        page_settings['has_next'] = tweets.has_next()

        tweets = serializers.serialize('json', tweets)

        return JsonResponse({"tweets": tweets, "tweet_index": tweet_index, "page_range": page_range, 'page_settings': page_settings}, status=200)

    return JsonResponse({"error": ""}, status=400)

def home(request):
    return render(request, 'home.html', {'title': 'home'})

def about(request):
    return render(request, 'about.html', {'title': 'about'})
