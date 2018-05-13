from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /
    url(r'^$', views.view_list, name='view_list'),
    # ex: /product/
    url(r'^product$', views.product_list, name='product_list'),
    # ex: /product/357/
    url(r'^product/(?P<product_id>[0-9]+)/$', views.product_detail, name='product_detail'),
    # ex: /view/user - get views for the logged user
    url(r'^view/user/(?P<username>\w+)/$', views.user_view_list, name='user_view_list'),
    url(r'^view/user/$', views.user_view_list, name='user_view_list'),
    # ex: /recommendation - get recommendations for the logged user
    url(r'^recommendation/$', views.user_recommendation_list, name='user_recommendation_list'),
]