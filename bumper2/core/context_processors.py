from django.conf import settings


def static_file_version_processor(request):
    return {
        'static_version': getattr(settings, 'STATIC_FILES_VERSION', '100'),
        'web_static_version': getattr(settings, 'WEB_STATIC_FILES_VERSION', '100'),
    }
