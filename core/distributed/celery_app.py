import os
from celery import Celery

# Configure Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "mintuu_distributed",
    broker=redis_url,
    backend=redis_url,
    include=["core.distributed.tasks"]
)

# Optional configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max per task
)

if __name__ == "__main__":
    app.start()
