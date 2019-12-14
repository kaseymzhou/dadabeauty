from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/send_topics$',views.send_topics)
]