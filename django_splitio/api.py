from __future__ import absolute_import, division, print_function, unicode_literals

from splitio.api import SdkApi

from .settings import splitio_settings


def _build_sdk_api():
    """Build SDK API client
    :return: SdkApi client
    :rtype: SdkApi
    """
    return SdkApi(splitio_settings.API_KEY,
                  sdk_api_base_url=splitio_settings.SDK_API_BASE_URL,
                  events_api_base_url=splitio_settings.EVENTS_API_BASE_URL,
                  split_sdk_machine_name=splitio_settings.SPLIT_SDK_MACHINE_NAME,
                  split_sdk_machine_ip=splitio_settings.SPLIT_SDK_MACHINE_IP,
                  connect_timeout=splitio_settings.CONFIG['connectionTimeout'],
                  read_timeout=splitio_settings.CONFIG['readTimeout'])
sdk_api = _build_sdk_api()
