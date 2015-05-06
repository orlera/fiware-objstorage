from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'object_storage.views.index', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^storage/', include('object_storage.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/', 'object_storage.views.index'),
)
