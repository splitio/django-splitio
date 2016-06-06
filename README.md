# Split.io Django Client

This project provides [Django](http://www.djangoproject.com/)` programs access to the [Split.io](http://split.io/)` SDK API. For more information on the Split.io SDK, please consult the documentation.

##  Installation and Requirements

`django-splitio` supports both Python 2 (2.7 or later) and Python 3 (3.3 or later) and Django 1.8 (or later). Stable versions can be installed from `PyPI <https://pypi.python.org>`_ using pip:
```
  pip install django-splitio
```
and development versions are installed directly from the `Github <https://github.com/splitio/django-splitio>`_ repository:
```
  pip install -e git+git@github.com:splitio/django-splitio.git@development#egg=django-splitio
```
This project requires a working `Celery <http://www.celeryproject.org/>`_ setup `integrated into your Django site <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>_` and access to a `Redis <http://redis.io/>`_ 2.6 (or later) instance.

## Quickstart

Before you begin, make sure that you have an **API key** for the Split.io services. Consult the Split.io documentation on how to get an API key for any of your environments.

First add `django_splitio` to the ``INSTALLED_APPS`` Django setting:
```
    INSTALLED_APPS = (
        ...
        'django_splitio',
        ...
    )
```
Next, create a `SPLITIO` dictionary on the Django settings. Only the `API_KEY` is mandatory.
```
    SPLITIO = {
        'API_KEY': 'my_splitio_api_key',
    }
```
With this configuration, the Split.io client will save all its information on a Redis instance running on ``localhost`` on port 6879. If you need to change the Redis configuration, you can use the ``REDIS_HOST``, ``REDIS_PORT`` and ``REDIS_DB`` configuration parameters:
```
    SPLITIO = {
        'API_KEY': 'my_splitio_api_key',
        'REDIS_HOST': 'my.redis.host',
        'REDIS_PORT': 6879,
        'REDIS_DB': 0,
    }
```
In the next section you can read about all the possible configuration parameters.

The next step is to schedule the Split.io related tasks. If you followed the instructions for Celery integration with Django, you'll most likely have a celery.py module that contains your Celery app. One way to schedule to schedule the tasks is to add entries to the ``CELERYBEAT_SCHEDULE`` settting, as shown in the following example:
```
    # celery.py
    from __future__ import absolute_import

    import os

    from celery import Celery

    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_splitio_testapp.settings')

    from django.conf import settings  # noqa

    from django_splitio.tasks import (get_features_update_schedule,  # noqa
                                      get_segments_update_schedule,
                                      get_impressions_update_schedule, get_metrics_update_schedule)

    app = Celery('django_splitio_testapp')

    # Using a string here means the worker will not have to
    # pickle the object when using Windows.
    app.config_from_object('django.conf:settings')
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
    app.conf.update(CELERYBEAT_SCHEDULE={
        'update_features_task': {
            'task': 'django_splitio.tasks.update_features_task',
            'schedule': get_features_update_schedule()
        },
        'update_segments_task': {
            'task': 'django_splitio.tasks.update_segments_task',
            'schedule': get_segments_update_schedule()
        },
        'update_impressions_task': {
            'task': 'django_splitio.tasks.update_impressions_task',
            'schedule': get_impressions_update_schedule()
        },
        'update_metrics_task': {
            'task': 'django_splitio.tasks.update_metrics_task',
            'schedule': get_metrics_update_schedule()
        }
    })
```
The convenience methods `get_features_update_schedule`, `get_segments_update_schedule`, `get_impressions_update_schedule` and `get_metrics_update_schedule` are provided to set the task's schedule according to the Split.io client configuration.

Once everythig has been set-up and the celery tasks are and up running, you can request the treatment for user using the client provided by the `get_client` function:
```
  >>> from django_splitio import get_client
  >>> client = get_client()
  >>> client.get_treatment('some_user', 'some_feature')
  'SOME_TREATMENT'
```
## Additional information

You can get more information on how to use this package in the included documentation.