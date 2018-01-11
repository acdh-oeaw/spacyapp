from django.urls import include, path
from . import views, api_views

app_name = 'enrich'

urlpatterns = [
    path('textparser/', views.TextParser.as_view(), name='textparser'),
    path('lemmatize/', views.Lemmatize.as_view(), name='lemmatize'),
    path('lemma/', api_views.lemma, name='lemma'),
    path('textparser-api/', api_views.textparser, name='textparser-api'),
]
