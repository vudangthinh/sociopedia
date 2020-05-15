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
            x_data = [0,1,2,3]
            y_data = [x**2 for x in x_data]
            plot_div = plot([go.Bar(x=x_data, y=y_data, name='Tweets Distribution')],
                                output_type='div', include_plotlyjs=False,
                                show_link=False, link_text="")
            
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
