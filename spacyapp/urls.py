from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

router = routers.DefaultRouter()
urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='NLP-API')),
    url(r'^admin/', admin.site.urls),
    url(r'^query/', include('enrich.urls', namespace='enrich')),
    url(r'^', include('webpage.urls', namespace='webpage')),
]
