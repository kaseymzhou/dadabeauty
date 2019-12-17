from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/sendtopics$',views.send_topics),
    # http://127.0.0.1:8000/v1/community/index  访问所有博客
    # http://127.0.0.1:8000/v1/community/index?tag=xxx  访问tag标签博客
    url(r'^index$',views.index),
    url(r'^myindex$',views.my_index),
    url(r'^detail$',views.detail_blog),
    url(r'^forward$',views.forward_blog),
    url(r'^like$',views.like_blog),
    url(r'^unlike$',views.unlike),
]