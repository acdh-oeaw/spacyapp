from django.urls import path
from . import views, api_views

app_name = 'enrich'

urlpatterns = [
    path('enrich-simple-json/', api_views.enrich_simple_jsonrequest, name='enrich-simple-json'),
    path('nerparser-api/', api_views.nerparser, name='nerparser-api'),
    path('textparser/', views.TextParser.as_view(), name='textparser'),
    path('lemmatize/', views.Lemmatize.as_view(), name='lemmatize'),
    path('lemma/', api_views.lemma, name='lemma'),
    path('textparser-api/', api_views.textparser, name='textparser-api'),
    path('jsonparser-api/', api_views.JsonParser.as_view(), name='jsonparser-api'),
    path('nlppipeline-api/', api_views.NLPPipelineNew.as_view(), name='nlppipeline-api'),
    path('nlppipeline/', views.NLPPipeView.as_view(), name='nlppipeline'),
    path('test-agreement/', api_views.TestAgreement.as_view(), name='test-agreement'),
    path('download/<slug:proc_id>/', views.DownloadView.as_view(), name='download')
]
