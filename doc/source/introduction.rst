Introduction
============

This project provides `Django <https://www.djangoproject.com/>`_ sites access to the `Split.io <http://split.io/>`_ SDK API. For more information on the Split.io SDK, please consult the documentation.

Installation and Requirements
-----------------------------

``django_splitio`` supports both Python 2 (2.7 or later) and Python 3 (3.3 or later) and Django 1.8 (or later). Stable versions can be installed from `PyPI <https://pypi.python.org>`_ using pip: ::

  pip install django-splitio

and development versions are installed directly from the `Github <https://github.com/splitio/django-splitio>`_ repository: ::

  pip install -e git+git@github.com:splitio/django-splitio.git@development#egg=django_splitio

This project require an access to a `Redis <http://redis.io/>`_ 2.6 (or later) instance. To populate Redis with the Split.io data, the app could be configured with `Celery <http://www.celeryproject.org/>`_ setup `integrated into your Django site <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>_`.
Or on the other hand, there is available a python script named ``splitio.bin.synchronizer`` in order to run as a service instead of a ``celery worker``. For production environment we recomend run it via ``supervisord``

Quickstart
----------

Before you begin, make sure that you have an **API key** for the Split.io services. Consult the Split.io documentation on how to get an API key for any of your environments.

First add ``django_splitio`` to the ``INSTALLED_APPS`` Django setting: ::

    INSTALLED_APPS = (
        ...
        'django_splitio',
        ...
    )

Next, create a ``SPLITIO`` dictionary on the Django settings. Only the ``API_KEY`` is mandatory. ::

    SPLITIO = {
        'API_KEY': 'my_splitio_api_key',
    }

With this configuration, the Split.io client will save all its information on a Redis instance running on ``localhost`` on port 6879. If you need to change the Redis configuration, you can use the ``REDIS_HOST``, ``REDIS_PORT`` and ``REDIS_DB`` configuration parameters: ::

    SPLITIO = {
        'API_KEY': 'my_splitio_api_key',
        'REDIS_HOST': 'my.redis.host',
        'REDIS_PORT': 6879,
        'REDIS_DB': 0,
    }

In the next section you can read about all the possible configuration parameters.

The next step is to schedule the Split.io related tasks.

To configure the ``splitio.bin.synchronizer`` service just type: ::

    $ /home/user/venv/bin/python -m splitio.bin.synchronizer --help

    Usage:
      synchronizer [options] <config_file>
      synchronizer -h | --help
      synchronizer --version

    Options:
      --splits-refresh-rate=SECONDS         The SECONDS rate to fetch Splits definitions [default: 30]
      --segments-refresh-rate=SECONDS       The SECONDS rate to fetch the Segments keys [default: 30]
      --impression-refresh-rate=SECONDS     The SECONDS rate to send key impressions [default: 60]
      --metrics-refresh-rate=SECONDS        The SECONDS rate to send SDK metrics [default: 60]
      -h --help                             Show this screen.
      --version                             Show version.

    Configuration file:
        The configuration file is a JSON file with the following fields:

        {
          "apiKey": "YOUR_API_KEY",
          "redisHost": "REDIS_DNS_OR_IP",
          "redisPort": 6379,
          "redisDb": 0
        }


    Examples:
        python -m splitio.bin.synchronizer splitio-config.json
        python -m splitio.bin.synchronizer --splits-refresh-rate=10 splitio-config.json

For **production environment** we recomend run it via ``supervisord``

If you followed the instructions for Celery integration with Django, you'll most likely have a celery.py module that contains your Celery app. One way to schedule to schedule the tasks is to add entries to the ``CELERYBEAT_SCHEDULE`` settting, as shown in the following example: ::

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

The convenience methods ``get_features_update_schedule``, ``get_segments_update_schedule``, ``get_impressions_update_schedule`` and ``get_metrics_update_schedule`` are provided to set the task's schedule according to the Split.io client configuration.

Once everythig has been set-up and the celery tasks are and up running, you can request the treatment for user using the client provided by the ``get_factory`` function: ::

  >>> from django_splitio import get_factory
  >>> factory = get_factory()
  >>> client = factory.client()
  >>> client.get_treatment('some_user', 'some_feature')
  'SOME_TREATMENT'

Client configuration
--------------------

The following configuration parameters are available for the ``SPLITIO`` settings dictionary:

+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| Key                    | Type | Description                                            | Default                                        |
+========================+======+========================================================+================================================+
| API_KEY                | str  | The Split.io SDK API key. This entry is mandatory. If  | None                                           |
|                        |      | "localhost" is supplied as API key, a localhost only   |                                                |
|                        |      | client is created when get_client is called            |                                                |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| SDK_API_BASE_URL       | str  | The URL base for the SDK API. This entry can be used   | 'https://sdk.split.io/api'                     |
|                        |      | to hit a different environment different than the      |                                                |
|                        |      | production one.                                        |                                                |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| EVENTS_API_BASE_URL    | str  | The URL base for the Events API. This entry can be     | 'https://events.split.io/api'                  |
|                        |      | used to hit a different environment different than     |                                                |
|                        |      | the production one.                                    |                                                |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| REDIS_HOST             | str  | The host that contains the redis instance.             | 'localhost'                                    |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| REDIS_PORT             | int  | The port of the redis instance                         | 6879                                           |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| REDIS_DB               | int  | THe db index on the redis instance                     | 0                                              |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| REDIS_FACTORY          | str  | A string with the location of a function that returns  | 'django_splitio.cache.default_redis_factory'   |
|                        |      | redis clients instances. The default implementation    |                                                |
|                        |      | uses the REDIS_HOST, REDIS_PORT and REDIS_DB to call   |                                                |
|                        |      | the StrictRedis constructor.                           |                                                |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| DISABLED_PERIOD        | int  | How long to wait to re-enable an automatic update      | 300                                            |
|                        |      | process after a problem was detected (in seconds).     |                                                |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+
| CONFIG                 | dict | A dictionary with configuration values that control    | See below.                                     |
|                        |      | the behaviour of the Split.io SDK client.              |                                                |
+------------------------+------+--------------------------------------------------------+------------------------------------------------+

The ``CONFIG`` SPLITIO setting mimics the behaviour of the ``config`` parameter for the regular Split.io python client. The following table shows the possible entries and their descriptions: ::

+------------------------+------+--------------------------------------------------------+---------+
| Key                    | Type | Description                                            | Default |
+========================+======+========================================================+=========+
| connectionTimeout      | int  | The timeout for HTTP connections in milliseconds.      | 1500    |
+------------------------+------+--------------------------------------------------------+---------+
| readTimeout            | int  | The read timeout for HTTP connections in milliseconds. | 1500    |
+------------------------+------+--------------------------------------------------------+---------+
| featuresRefreshRate    | int  | The features (splits) update refresh period in         | 30      |
|                        |      | seconds.                                               |         |
+------------------------+------+--------------------------------------------------------+---------+
| segmentsRefreshRate    | int  | The segments update refresh period in seconds.         | 60      |
+------------------------+------+--------------------------------------------------------+---------+
| metricsRefreshRate     | int  | The metrics report period in seconds                   | 60      |
+------------------------+------+--------------------------------------------------------+---------+
| impressionsRefreshRate | int  | The impressions report period in seconds               | 60      |
+------------------------+------+--------------------------------------------------------+---------+

The localhost environment
-------------------------

During development the ``LocalhostEnvironmentClient`` client class can be used to avoid hitting the
Split.io API SDK. This class takes its configuration from a ``.split`` file in the user's *HOME*
directory. The ``.split`` file has the following format: ::

  file: (comment | split_line)+
  comment : '#' string*\n
  split_line : feature_name ' ' treatment\n
  feature_name : string
  treatment : string

This is an example of a ``.split`` file: ::

  # This is a comment
  feature_0 treatment_0
  feature_1 treatment_1

In order to use this client, you need to set the ``API_KEY`` to 'localhost': ::

    SPLITIO = {
        'API_KEY': 'localhost'
    }

Afterwards, the ``get_factory().client()`` function works as expected.

  >>> from django_splitio import get_factory
  >>> factory = get_factory()
  >>> client = factory.client()
  >>> client.get_treatment('some_user', 'feature_0')
  'treatment_0'
  >>> client.get_treatment('some_other_user', 'feature_0')
  'treatment_0'
  >>> client.get_treatment('yet_another_user', 'feature_1')
  'treatment_1'
  >>> client.get_treatment('some_user', 'non_existent_feature')
  'CONTROL'
