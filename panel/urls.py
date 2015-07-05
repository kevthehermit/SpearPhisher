from django.conf.urls import patterns, url

from panel import views

urlpatterns = patterns('',
    # Index
    url(r'^$', views.index, name='index'),
    
    # Login Page
    url(r'^login/', views.login_page, name='login'),

    # Single Email Spoof
    url(r'^single/', views.single_email, name='single'),
    url(r'^send/single', views.send_single, name='send_single'),
    
    # Logout Page
    url(r'^logout/', views.logout_page, name='logout'),
    
    # Campaign Pages
    url(r'^campaign/(?P<campaign_id>\d+)/$', views.campaign, name='campaign'),
    url(r'^control/', views.campaign_control, name='campaign_control'),
    
    # ex: Template pages
    url(r'^template/$', views.template, name='template'),
    url(r'^template/(?P<template_id>\d+)$', views.template, name='template'),

    # Recipient Data
    url(r'^recipient/(?P<recipient_id>.+)/$', views.recipient_data, name='recipient_data'),
    
    # Post Data Pages
    url(r'^add/(?P<add_type>.+)/$', views.add_post_data, name='add_post_data'),

    # Stats Return Json Object
    url(r'^stats/(?P<campaign_id>\d+)/$', views.statistics, name='statistcs'),
    
    # Export Rules
    url(r'^export/(?P<export_type>.+)/(?P<campaign_id>\d+)$', views.export_tracking, name='export_tracking'), 
    
)