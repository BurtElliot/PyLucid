# coding: utf-8

"""
    PyLucid base settings
    ~~~~~~~~~~~~~~~~~~~~~
"""

import os

gettext = lambda s: s


ALLOWED_HOSTS = []


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Chicago'

USE_I18N = True
USE_L10N = True
USE_TZ = True



SITE_ID = 1

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.csrf',
    'django.core.context_processors.tz',
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings'
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cms',
    'djangocms_admin_style',
    'djangocms_text_ckeditor',
    'menus',
    'sekizai',
    'mptt',
    # 'djangocms_style',
    # 'djangocms_column',
    'djangocms_file',
    # 'djangocms_flash',
    # 'djangocms_googlemap',
    # 'djangocms_inherit',
    'djangocms_link',
    'djangocms_picture',
    # 'djangocms_teaser',
    'djangocms_video',
    'cmsplugin_htmlsitemap', # https://github.com/raphaa/cmsplugin-htmlsitemap
    'cmsplugin_pygments', # https://github.com/chrisglass/cmsplugin-pygments

    'reversion', # https://github.com/etianen/django-reversion
    'reversion_compare', # https://github.com/jedie/django-reversion-compare
    'compressor', # https://github.com/django-compressor/django-compressor
    'django_extensions', # https://github.com/django-extensions/django-extensions

    # djangocms-blog
    'filer',
    'easy_thumbnails',
    'cmsplugin_filer_image',
    'parler',
    'taggit',
    'taggit_autosuggest',
    'django_select2',
    'meta',
    'meta_mixin',
    'admin_enhancer',
    'djangocms_blog',

    # own apps:
    'django_info_panel',
    'pylucid',
)

LANGUAGES = (
    ## Customize this
    ('en', gettext('en')),
    ('de', gettext('de')),
)

CMS_LANGUAGES = {
    ## Customize this
    'default': {
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    },
    1: [
        {
            'redirect_on_fallback': True,
            'public': True,
            'hide_untranslated': False,
            'code': 'en',
            'name': gettext('en'),
        },
        {
            'redirect_on_fallback': True,
            'public': True,
            'hide_untranslated': False,
            'code': 'de',
            'name': gettext('de'),
        },
    ],
}

CMS_TEMPLATES = (
    ('fullwidth.html', 'Full-width template'),
    ('sidebar_left.html', 'Sidebar left template'),
    ('homepage.html', 'Homepage template'),
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}



MIGRATION_MODULES = {
    'cms': 'cms.migrations_django',
    'menus': 'menus.migrations_django',
    'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations_django',
    # 'djangocms_column': 'djangocms_column.migrations_django',
    # 'djangocms_flash': 'djangocms_flash.migrations_django',
    # 'djangocms_googlemap': 'djangocms_googlemap.migrations_django',
    # 'djangocms_inherit': 'djangocms_inherit.migrations_django',
    # 'djangocms_style': 'djangocms_style.migrations_django',
    'djangocms_file': 'djangocms_file.migrations_django',
    'djangocms_link': 'djangocms_link.migrations_django',
    'djangocms_picture': 'djangocms_picture.migrations_django',
    # 'djangocms_teaser': 'djangocms_teaser.migrations_django',
    'djangocms_video': 'djangocms_video.migrations_django',

    # for djangocms-blog:
    'filer': 'filer.migrations_django',
    'cmsplugin_filer_image': 'cmsplugin_filer_image.migrations_django',
}


# django-reversion-compare settings:
ADD_REVERSION_ADMIN=True # Add the reversion modes to admin interface


# django-debug-toolbar settings:
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',

    'django_info_panel.panels.database.DatabaseInfo',
    'django_info_panel.panels.urlpatterns.UrlPatternsInfo',
]


# https://github.com/nephila/djangocms-blog#quick-hint
SOUTH_MIGRATION_MODULES = {
    'easy_thumbnails': 'easy_thumbnails.south_migrations',
    'taggit': 'taggit.south_migrations',
}


# http://django-filer.readthedocs.org/en/latest/installation.html#configuration
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)


# https://github.com/nephila/django-meta#configuration
META_SITE_PROTOCOL = None # This should be set to either 'http' or 'https'. Default is None
META_USE_SITES = True # use Django's sites contrib app


# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_DEFAULT_LANGUAGE_CODE = 'en'
PARLER_LANGUAGES = {
    None: (
        {'code': 'en',},
        {'code': 'de',},
    ),
    # 1: ( # SITE_ID == 1
    #     {'code': 'en',},
    #     {'code': 'de',},
    # ),
    # 2: ( # SITE_ID == 2
    #     {'code': 'en',},
    #     {'code': 'de',},
    # ),
    'default': {
        'fallback': PARLER_DEFAULT_LANGUAGE_CODE,
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}