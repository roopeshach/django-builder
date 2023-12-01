import os
import zipfile
import sys
import subprocess
from django.conf import settings


def zip_project_folder(project_name):

    # Find the folder with the specified project_name in the base directory
    project_folder = os.path.join(settings.BASE_DIR, project_name)
    if not os.path.exists(project_folder):
        print(f"Folder '{project_name}' not found in the base directory.")
        return

    # Create the projects folder if it doesn't exist
    projects_folder = os.path.join(settings.BASE_DIR, 'projects')
    os.makedirs(projects_folder, exist_ok=True)

    # Define the file path for the zip file
    zip_file_path = os.path.join(projects_folder, f'{project_name}.zip')

    # Create a zip file that contains the project folder
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_folder):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_folder)
                zipf.write(file_path, os.path.join(project_name, rel_path))

    return zip_file_path

def generate_index_html_content():
    # Create the content for the index.html file with Bootstrap cards
    index_html_content = """
    <!DOCTYPE html>
    <html>
    <!-- Font Awesome -->
<link
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
  rel="stylesheet"
/>
<!-- Google Fonts -->
<link
  href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
  rel="stylesheet"
/>
<!-- MDB -->
<link
  href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.0.0/mdb.min.css"
  rel="stylesheet"
/>
      <!--Main Navigation-->
  <header>
    <style>
      #intro {
        background-image: url("https://www.yotta.com/wp-content/uploads/2020/10/High-Performance-Computing-to-drive-AI-ML-workloads.jpg");
        height: 110vh;
      }

      /* Height for devices larger than 576px */
      @media (min-width: 992px) {
        #intro {
          margin-top: -58.59px;
        }
      }

      .navbar .nav-link {
        color: #fff !important;
      }
    </style>

    
    <!-- Background image -->
    <div id="intro" class="bg-image shadow-2-strong">
      <div class="mask" style="background-color: rgba(0, 0, 0, 0.8);">
        <div class="container d-flex align-items-center justify-content-center text-center h-100">
          <div class="text-white">
            <h1 class="mb-3">Django App Builder</h1>
            <h5 class="mb-4">Design Your Apps in seconds.</h5>
            <a class="btn btn-outline-primary btn-lg m-2" href="/docs" role="button"
              rel="nofollow" target="_blank">Swagger Docs</a>
            <a class="btn btn-outline-success btn-lg m-2" href="/admin" target="_blank"
              role="button">Admin Panel</a>
          </div>
        </div>
      </div>
    </div>
    <!-- Background image -->
  </header>
  <!--Main Navigation-->
   <!--Footer-->
  <footer class="bg-light text-lg-start">
  

   
    <!-- Copyright -->
    <div class="text-center p-3" style="background-color: rgba(0, 0, 0, 0.2);">
      © 2020 Copyright:
      <a class="text-dark" href="https://reev-it.com/">Reev InfoTech</a>
    </div>
    <!-- Copyright -->
  </footer>
<!-- MDB -->
<script
  type="text/javascript"
  src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.0.0/mdb.umd.min.js"
></script>
  
    """
    return index_html_content

def settings_content(project_name, schema_generated_apps):

    jazzmin_settings_content = f'''
JAZZMIN_SETTINGS = {{
    "site_title": "{project_name} Admin",  # Set the site title to the project name
    "site_header": "{project_name} Admin",  # Set the site header to the project name
    "site_brand": "{project_name} Admin",  # Set the site brand to the project name
    "site_logo": "images/logo-text.png",
    "login_logo": "images/logo-text2.png",
    "login_logo_dark": "images/logo-text2.png",
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": f'Welcome to {project_name}',  # Set the welcome sign
    "copyright": "{project_name}",  # Set the copyright to the project name
    "topmenu_links": [
        {{
            "name": "Home",
            "url": "admin:index",
            "icon": "fas fa-home"
        }}
    ],
    "show_sidebar": True,
    "navigation_expanded": False,
    "hide_apps": [],
    "hide_models": [],
    "custom_links": {{
        "auth": [],
    }},
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
}}
'''
# Define the content of jazzmin_tweaks_content as a string
    jazzmin_tweaks_content = f'''
JAZZMIN_TWEAKS = {{
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-indigo",
    "navbar": "navbar-indigo navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "sketchy",
    "dark_mode_theme": None,
    "button_classes": {{
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }},
    "site_title": "{project_name} Admin",
    "site_header": "{project_name} Admin",
    "site_logo": "images/logo-text.png",
    "topmenu_links": [
        {{
            "name": "Home",
            "url": "admin:index",
            "icon": "fas fa-home"
        }}
    ]
}}
'''
    # Generate the INSTALLED_APPS list dynamically
    installed_apps_content = ',\n    '.join(["'" + app + "'" for app in schema_generated_apps])
    # Generate the urlpatterns content for schema-generated apps
    app_urlpatterns = '\n'.join([f're_path(r\'^{app}/\', include(\'{app}.urls\')),' for app in schema_generated_apps])

	# Combine all the content into one variable
    full_settings_content = f'''
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-i7w8dm6ml*(ii@e&#f-fw23i0$!9izhthjm=y#dgi!!lu2(p+g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [  
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'drf_yasg',
    'corsheaders',
] +  [{installed_apps_content}] + ['Authentication']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }},
}}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {{
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }},
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_L10N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_AUTH = {{
    'SESSION_LOGIN': False,
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'auth',
    'JWT_AUTH_HTTPONLY': False,
    'AUTH_TOKEN_VALIDITY': timedelta(minutes=1)
}}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
CSRF_COOKIE_SECURE = False


REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
    ),

    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}}

STATIC_URL = '/static/'
import os
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
AUTH_USER_MODEL = "Authentication.ApplicationUser"
# Jazzmin settings
{jazzmin_settings_content}

# Jazzmin tweaks
{jazzmin_tweaks_content}
'''
    urls_content = f'''
from django.urls import include, re_path, path
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve

schema_view = get_schema_view(
    openapi.Info(
        title='{project_name} API Docs',
        default_version='v2',
    )
)

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name="index.html"), name='index'),
    re_path(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    re_path(r'^dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    re_path(r'^account/', include('allauth.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Include schema-generated app URLs
urlpatterns += [
    {app_urlpatterns}
]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {{
            'document_root': settings.MEDIA_ROOT,
        }}),
    ]

admin.site.site_header = "{project_name} - Platform Admin"
admin.site.site_title = "{project_name} - Platform Admin Portal"
admin.site.index_title = "Welcome to {project_name} - Platform Portal"
'''
    return full_settings_content, urls_content

def update_venv_and_modules():
    # Determine the OS (Windows or Linux)
    is_windows = sys.platform.startswith('win')

    # Set up the virtual environment path
    project_dir = os.path.join(os.getcwd())
    venv_dir = os.path.join(project_dir, '.venv')

    # Create the virtual environment
    if is_windows:
        subprocess.run(['python', '-m', 'venv', venv_dir], check=True)
    else:
        subprocess.run(['python3', '-m', 'venv', venv_dir], check=True)

    # Activate the virtual environment and install Django
    activate_script = 'activate.bat' if is_windows else 'activate'
    activate_path = os.path.join(venv_dir, 'Scripts' if is_windows else 'bin', activate_script)
    command = activate_path if is_windows else "source " + activate_path

    return command
    


def get_requirements():
    return """
asgiref
certifi
cffi
charset-normalizer
coreapi
coreschema
cryptography
defusedxml
dj-rest-auth
django
django-allauth
django-cors-headers
django-jazzmin
djangorestframework
djangorestframework-simplejwt
drf-yasg
idna
inflection
itypes
Jinja2
MarkupSafe
oauthlib
packaging
Pillow
pycparser
PyJWT
python3-openid
pytz
PyYAML
requests
requests-oauthlib
sqlparse
uritemplate
urllib3
"""