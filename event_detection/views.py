from django.shortcuts import render, redirect
from .forms import KeywordForm
from . import twitter_search
from django.http import JsonResponse
from .models import Keyword, Tweet
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder


# Create your views here.

def search(request):
    if request.method == 'POST':
        form = KeywordForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            twitter_search.stream_search(post)

            keyword_objs = Keyword.objects.filter(keyword=post.keyword)
            tweets = Tweet.objects.filter(keyword=keyword_objs[0])
            tweet_texts = []
            for tweet in tweets:
                tweet_texts.append(tweet.text)

            return render(request, 'keyword_search.html', {'form': form, 'tweets': tweet_texts})
    else:
        form = KeywordForm()
        return render(request, 'keyword_search.html', {'form': form})

@csrf_exempt
def update_search_result(request):
    keyword = request.POST.get('keyword', None)
    keyword_objs = Keyword.objects.filter(keyword=keyword)
    tweets = Tweet.objects.filter(keyword=keyword_objs[0])
    tweet_texts = []
    for tweet in tweets:
        tweet_texts.append(tweet.text)
    data = {'tweets': tweet_texts}
    
    return JsonResponse(data)