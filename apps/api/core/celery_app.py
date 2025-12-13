"""
Celery Configuration and Tasks
Background job processing for emails, PDFs, and other async operations
"""

from celery import Celery
from celery.schedules import crontab
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'inara_hris',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['core.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'send-timesheet-reminders': {
        'task': 'core.tasks.send_timesheet_reminders',
        'schedule': crontab(hour=9, minute=0, day_of_week='friday'),  # Every Friday at 9 AM
    },
    'check-contract-expirations': {
        'task': 'core.tasks.check_contract_expirations',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    'update-leave-balances': {
        'task': 'core.tasks.update_leave_balances',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),  # Monthly on 1st
    },
}

if __name__ == '__main__':
    celery_app.start()
