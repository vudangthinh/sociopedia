from django.contrib import admin

# Register your models here.
from .models import Keyword, Tweet

admin.site.register(Keyword)
admin.site.register(Tweet)