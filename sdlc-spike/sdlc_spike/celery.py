import os 
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdlc_spike.settings')

app = Celery('sdlc_spike')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
