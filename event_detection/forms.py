from django import forms
from .models import Keyword
from django.utils import timezone


class KeywordSearchForm(forms.ModelForm):
    class Meta:
        model = Keyword
        fields = ('keyword', 'end_date')

class SelectTimeRangeForm(forms.Form):
    start_date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
    end_date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])

class KeywordAnalysisForm(forms.ModelForm):

    CHOICES = [('Option 1', 'Minute'), ('Option 2', 'Hour'), ('Option 3', 'Day'), ('Option 4', 'Week'), ('Option 5', 'Month')]
    time_option = forms.ChoiceField(label='Show by time frequency', choices=CHOICES)
    
    class Meta:
        model = Keyword
        fields = ('keyword',)