import collections
from datetime import datetime, timedelta

from plotly.offline import plot
import plotly.graph_objs as go

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