from django.shortcuts import render, redirect
from .forms import KeywordSearchForm, KeywordAnalysisForm, SelectTimeRangeForm
from .utils import twitter_search, knowledge_extract
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
from .utils import utils


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

            return render(request, 'keyword_search.html', {'title': 'search', 'form': form, 'keyword_obj_list': keyword_obj_list})
    else:
        form = KeywordSearchForm()
        end_date = timezone.now() + timedelta(7)
        form['end_date'].initial = end_date
        min_date = timezone.now().strftime("%Y/%m/%d")
        max_date = end_date.strftime("%Y/%m/%d")
        return render(request, 'keyword_search.html', {'title': 'search', 'form': form, 'min_date': min_date, 'max_date': max_date})

@login_required
def data_analysis(request, pk, start_date, end_date):
    print(pk, start_date, end_date)
    # tweet_list = utils.get_tweet_in_time_range(pk, start_date, end_date)

    return render(request, 'keyword_analysis.html', {"keyword_id": pk, "start_date": start_date, "end_date": end_date})

@csrf_exempt
def analyse(request):
    if request.is_ajax and request.method == "POST":
        keyword_id = request.POST.get('id', None)
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
        analyse_type = request.POST.get('analyse_type')
       
        tweet_list = utils.get_tweet_in_time_range(keyword_id, start_date, end_date)

        if analyse_type == 'wordcloud':
            img_path = utils.analyse_wordcloud(tweet_list, request)
            return JsonResponse({'wordcloud': img_path}, status=200)

        elif analyse_type == 'n-grams':
            one_gram_plot_div, two_gram_plot_div, thr_gram_plot_div = utils.analyse_ngrams(tweet_list)
            return JsonResponse({
                'one-grams': one_gram_plot_div, 
                'two-grams': two_gram_plot_div, 
                'thr-grams': thr_gram_plot_div, 
                },
                status=200)

        elif analyse_type == 'knowledgegraph':
            knowledge_graph_dict = utils.extract_knowledge_graph(tweet_list)
            return JsonResponse({'knowledgegraph': knowledge_graph_dict}, status=200)
        
    return JsonResponse({"error": ""}, status=400)

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

    page_settings = {}
    page_settings['has_other_pages'] = tweets.has_other_pages()
    page_settings['has_previous'] = tweets.has_previous()
    page_settings['number'] = tweets.number
    page_settings['has_next'] = tweets.has_next()
    if tweets.has_previous():
        page_settings['previous_page_number'] = tweets.previous_page_number()
    if tweets.has_next():
        page_settings['next_page_number'] = tweets.next_page_number()

    return render(request, 'view_tweets.html', {'title': 'system_management',
                                                'keyword_id': pk,
                                                'tweets': tweets.object_list, 
                                                'page_settings': page_settings,
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
        if tweets.has_previous():
            page_settings['previous_page_number'] = tweets.previous_page_number()
        if tweets.has_next():
            page_settings['next_page_number'] = tweets.next_page_number()

        # for tweet in tweets:
        #     tweet.user_id = str(tweet.user_id)
        #     tweet.tweet_id = str(tweet.tweet_id)
            
        tweets = serializers.serialize('json', tweets)
        
        return JsonResponse({"tweets": tweets, "tweet_index": tweet_index, "page_range": page_range, 'page_settings': page_settings}, status=200)

    return JsonResponse({"error": ""}, status=400)

def home(request):
    return render(request, 'home.html', {'title': 'home'})

def about(request):
    return render(request, 'about.html', {'title': 'about'})
