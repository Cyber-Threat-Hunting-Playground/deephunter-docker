import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'helloworld'

DEBUG = True

# Update settings
UPDATE_ON = "release" # Possible values: commit|release
TEMP_FOLDER = "/data/tmp"
VENV_PATH = "/data/venv"

# Should the login form be displayed?
# It can be disabled if you are using an external authentication provider (PingID, EntraID)
SHOW_LOGIN_FORM = True

ALLOWED_HOSTS = ['deephunter.domain.com', 'localhost', '127.0.0.1', '*']

# PingID / MS Entra ID (leave placeholder values when using local auth)
AUTHLIB_OAUTH_CLIENTS = {
    'pingid': {
        'client_id': '',
        'client_secret': '',
        'server_metadata_url': '',
        'client_kwargs': {'scope': 'openid groups profile email'},
    },
    'entra_id': {
        'client_id': '',
        'client_secret': '',
        'server_metadata_url': '',
        'client_kwargs': {'scope': 'openid profile email'},
    },
}

# Which auth provider are you using (pingid|entra_id).
# Set to an empty string for local authentication
AUTH_PROVIDER = ''

AUTH_TOKEN_MAPPING = {
    'username': 'unique_name',
    'first_name': 'given_name',
    'last_name': 'family_name',
    'email': 'upn',
    'groups': 'roles',
}

USER_GROUPS_MEMBERSHIP = {
    'viewer': '',
    'manager': '',
    'threathunter': '',
}

# USER and GROUP. Used by deployment script to apply correct permissions
USER_GROUP = "user:group"
SERVER_USER = "www-data"

# GitHub URL used by the deploy.sh script to clone the repo
GITHUB_URL = "https://github.com/Cyber-Threat-Hunting-Playground/deephunter.git"
GITHUB_LATEST_RELEASE_URL = 'https://api.github.com/repos/Cyber-Threat-Hunting-Playground/deephunter/releases/latest'
GITHUB_COMMIT_URL = 'https://raw.githubusercontent.com/Cyber-Threat-Hunting-Playground/deephunter/refs/heads/main/static/commit_id.txt'

# Max retention (in days). By default 90 days (3 months)
DB_DATA_RETENTION = int(os.environ.get('DB_DATA_RETENTION', 90))

# Max number of distinct hostnames to consider an analytic as rare
RARE_OCCURRENCES_THRESHOLD = 10

# Threshold for max number of hosts saved to DB for a given analytic (campaigns).
# By default 1000
CAMPAIGN_MAX_HOSTS_THRESHOLD = 1000

# Actions applied to analytics if CAMPAIGN_MAX_HOSTS_THRESHOLD is reached several times
ON_MAXHOSTS_REACHED = {
    "THRESHOLD": 3,
    "DISABLE_RUN_DAILY": True,
    "DELETE_STATS": True
}

# Analytics per page in the list view
ANALYTICS_PER_PAGE = 50

# Workflow settings
DAYS_BEFORE_REVIEW = 30  # Number of days before an analytic is considered for review
DISABLE_ANALYTIC_ON_REVIEW = False  # Disable analytics with status 'REVIEW'

# Automatically regenerate stats when analytic query field is changed
AUTO_STATS_REGENERATION = True

# For repo import when FK/M2M fields don't exist in your DB, should the missing relation be created
# target_os and mitre_techniques won't be automatically created. If not in your database, analytic will be created without empty values
# Vulnerabilities base score will default to 0
REPO_IMPORT_CREATE_FIELD_IF_NOT_EXIST = {
    "category": "false",
    "threats": "false",
    "actors": "false",
    "vulnerabilities": "false",
}
# Default values when analytics are imported from a repo
REPO_IMPORT_DEFAULT_STATUS = "DRAFT"
REPO_IMPORT_DEFAULT_RUN_DAILY = True

# List of users and groups to send notifications to for each notification level
NOTIFICATIONS_RECIPIENTS = {
    'debug':   {'users': ['admin'], 'groups': []},
    'info':    {'users': ['admin'], 'groups': ['manager', 'viewer']},
    'success': {'users': [''], 'groups': ['manager']},
    'warning': {'users': [''], 'groups': ['']},
    'error':   {'users': [''], 'groups': ['']},
}
# Notifications auto deleted after x days for each notification level
AUTO_DELETE_NOTIFICATIONS_AFTER = {
    'debug':   1,
    'info':    7,
    'success': 7,
    'warning': 30,
    'error':   30,
}

# Choose AI connector. Leave empty string to disable AI features
AI_CONNECTOR = ""

# Proxy settings
PROXY = {
    'http': '',
    'https': ''
}

# Keep ModelBackend around for per-user permissions and local superuser (admin)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django plugins
    'django_extensions',
    'django.contrib.humanize',
    'dbbackup',
    'django_markup',
    'simple_history',
    'rest_framework',
    'drf_spectacular',
    
    # DeepHunter apps
    'qm',
    'extensions',
    'reports',
    'connectors',
    'repos',
    'notifications',
    'dashboard',
    'config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'deephunter.history_middleware.SafeHistoryRequestMiddleware',
    'django_auto_logout.middleware.auto_logout',
]

ROOT_URLCONF = 'deephunter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]

WSGI_APPLICATION = 'deephunter.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
# For Docker: Use 'mariadb' as HOST (container name)
# For local: Use '127.0.0.1' or 'localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'deephunter',
        'USER': 'deephunter',
        'PASSWORD': 'Awes0meP4ssW0rd',
        'HOST': 'mariadb',  # Docker container name
        'PORT': '3306'
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = '{}/static'.format(BASE_DIR)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/admin/login/'

### dbbackup settings (encrypted backups)
DBBACKUP_STORAGE_OPTIONS = {'location': '/data/backups/'}
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_GPG_RECIPIENT = 'email@domain.com'

# Logout automatically after 1 hour
AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=60),
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}

# For Docker: Use 'redis' as hostname (container name)
# For local: Use 'localhost'
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'deephunter.api_auth.ApiKeyAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'deephunter.api_auth.ApiKeyPermission',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'DeepHunter API',
    'DESCRIPTION': 'REST API for managing all DeepHunter resources: analytics, campaigns, connectors, repositories, notifications, and configuration.',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Analytics', 'description': 'Threat hunting analytics management'},
        {'name': 'Analytics Meta', 'description': 'Analytics metadata and error tracking'},
        {'name': 'Categories', 'description': 'Analytic categories'},
        {'name': 'MITRE Tactics', 'description': 'MITRE ATT&CK tactics'},
        {'name': 'MITRE Techniques', 'description': 'MITRE ATT&CK techniques'},
        {'name': 'Threats', 'description': 'Threat names and software'},
        {'name': 'Threat Actors', 'description': 'Threat actor groups'},
        {'name': 'Countries', 'description': 'Country reference data'},
        {'name': 'Target OS', 'description': 'Target operating systems'},
        {'name': 'Vulnerabilities', 'description': 'CVE vulnerabilities'},
        {'name': 'Tags', 'description': 'Analytic tags'},
        {'name': 'Campaigns', 'description': 'Threat hunting campaigns'},
        {'name': 'Campaign Completions', 'description': 'Campaign completion tracking per connector'},
        {'name': 'Snapshots', 'description': 'Campaign execution snapshots'},
        {'name': 'Endpoints', 'description': 'Detected endpoints'},
        {'name': 'Reviews', 'description': 'Analytic review workflow'},
        {'name': 'Saved Searches', 'description': 'Saved search queries'},
        {'name': 'Tasks', 'description': 'Background task status'},
        {'name': 'Connectors', 'description': 'Data source connectors'},
        {'name': 'Connector Config', 'description': 'Connector configuration keys'},
        {'name': 'Repos', 'description': 'Analytic repositories'},
        {'name': 'Repo Analytics', 'description': 'Analytics discovered in repositories'},
        {'name': 'Notifications', 'description': 'System notifications'},
        {'name': 'User Notifications', 'description': 'Per-user notification status'},
        {'name': 'Modules', 'description': 'DeepHunter modules'},
        {'name': 'Module Permissions', 'description': 'Module permission definitions'},
        {'name': 'API Keys', 'description': 'API key management'},
        {'name': 'Users', 'description': 'User management'},
    ],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'description': 'Paste your DeepHunter API key (Config > API Keys)',
            },
            'ApiKeyHeader': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key',
                'description': 'Paste your DeepHunter API key (Config > API Keys)',
            },
        },
    },
    'SECURITY': [
        {'BearerAuth': []},
        {'ApiKeyHeader': []},
    ],
}
