from django.core import serializers
from myapp.models import MakeAPost

data = serializers.serialze("json", MakeAPost.objects.all())



