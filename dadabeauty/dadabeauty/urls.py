"""dadabeauty URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # http://127.0.0.1:8000/test
    url(r'^test$',views.test),
    # http://127.0.0.1:8000/v1/user
    url(r'^v1/user',include('user.urls')),
    # http://127.0.0.1:8000/v1/product
    url(r'^v1/product',include('product.urls')),
    # http://127.0.0.1:8000/v1/community
    url(r'^v1/community',include('community.urls')),
    # http://127.0.0.1:8000/v1/dtoken
    url(r'v1/dtoken',include('dtoken.urls')),

]
