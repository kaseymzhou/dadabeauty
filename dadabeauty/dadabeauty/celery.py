from celery import Celery
from django.conf import settings
import os

# 为celery设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dadabeauty.settings')

# 创建应用 初始化celery
app = Celery('dadabeauty')
app.conf.update(
    BROKER_URL = 'redis://@127.0.0.1:6379/1'
)
app.autodiscover_tasks(settings.INSTALLED_APPS)