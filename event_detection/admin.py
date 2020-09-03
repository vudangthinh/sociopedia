from django.contrib import admin

# Register your models here.
from .models import TwitterToken, Keyword, Tweet

admin.site.register(TwitterToken)
admin.site.register(Keyword)
admin.site.register(Tweet)