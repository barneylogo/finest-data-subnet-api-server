module.exports = {
    apps: [
      {
        name: 'django-server',
        script: 'python',
        args: 'manage.py runserver 0.0.0.0:8000',
      },
      {
        name: 'celery-worker',
        script: 'celery',
        args: '-A config worker --loglevel=info',
        interpreter: 'none',
      },
      {
        name: 'celery-beat',
        script: 'celery',
        args: '-A config beat --loglevel=info',
        interpreter: 'none',
      }
    ]
  };
