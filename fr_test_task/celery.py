from celery import Celery
import os

from fr_test_task import settings

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fr_test_task.settings')

# Create the Celery app
app = Celery('fr_test_task',
             broker=settings.CELERY_BROKER_URL,
             backend=settings.CELERY_RESULT_BACKEND)

# Load the celery config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)