from django.conf.urls import patterns, url
import views
import forms

urlpatterns = patterns('',
    url(r'^$', views.index, name = 'index'),
    url(r'^uploaded', views.uploaded, name = 'uploaded'),
    url(r'^upload_form', views.upload_form, name = 'upload_form'),
    url(r'^uploaded_form', views.uploaded_form, name = 'uploaded_form'),
)