import os
from django.core.management import BaseCommand, call_command
from django.conf import settings
import json
from .utils import generate_index_html_content

class Command(BaseCommand):
    help = 'Generate Django apps, models, migrations, admin, and DRF views from JSON schema files.'

    def handle(self, *args, **options):
        """
        Generates all the necessary code for a given app based on its JSON Schema file.
        The command is called with an argument that specifies which app to generate:
        python manage.py generate_models_from_schema <appname>
        If no arguments are provided, it will generate all apps in the specified directory.
        """
        self.stdout.write(self.style.NOTICE('Starting the app and model generation process...'))
        schema_dir = os.path.join(settings.BASE_DIR, 'schema')
        schema_generated_apps = []  # Initialize an empty list to store app names

        for filename in os.listdir(schema_dir):
            if filename.endswith('_schema.json'):
                file_path = os.path.join(schema_dir, filename)
                with open(file_path, 'r') as file:
                    schema = json.load(file)
                    # Get the name of the app from the schema's title
                    app_name = schema.get('appName', 'default_app')
                    schema_generated_apps.append(app_name)
                
                    #creating app and its models from schema and writing it to their own file.
                    self.create_app(schema)
                    self.create_models( schema)
                
                    #create Authentication App with ApplicationUser Model and register it in admin
                    self.create_authentication_app()
                    # Generate admin code from the schema
                    admin_code = self.generate_admin_code_from_schema(schema, app_name)
                    # Create or append to the app's admin.py file with the generated admin code
                    self.create_or_append_admin_file(app_name, admin_code)
                    self.generate_serializers_from_schema(schema, app_name)
                    self.generate_views_from_schema(schema, app_name)
                    self.generate_urls_from_schema(schema, app_name)
                    #write apps' name in INSTALLED_APP in settings.py
                    self.add_apps_to_installed_apps(app_name)
        
        project_name = settings.SETTINGS_MODULE.split('.')[0]  # Get the project name

        #generate index.html file
        self.index_file_generator(project_name)

        # Call the generate_settings_content method with schema_generated_apps and project_name
        self.generate_settings_content(schema_generated_apps, project_name)

                
        self.stdout.write(self.style.SUCCESS('Completed app and model generation process.'))
    
    def create_app(self, schema):
        """
        Create a new Django application based on the provided schema.
        
        Args:
        schema (dict): The JSON schema representing the application's structure.
        Function:
        - Creates an empty directory named after the app name under the main project directory.
        """
        app_name = schema.get('appName', 'default_app')
        app_directory = os.path.join(settings.BASE_DIR, app_name)

        # Check if the app directory exists, if not, create a new app
        if not os.path.exists(app_directory):
            self.stdout.write(self.style.NOTICE(f'Creating new Django app: {app_name}'))
            call_command('startapp', app_name)
        else:
            self.stdout.write(self.style.NOTICE(f'Django app {app_name} already exists.'))

    def create_models(self, schema):
        """
        Generate Django models from the provided schema.
        Args:
        schema (dict): The JSON schema representing the application's structure.
        Function:
        - Iterate over all fields defined in the schema and create corresponding Django models.
        """
        app_name = schema.get('appName', 'default_app')
        models = schema.get('models', [])
        models_code = f"# Models for {app_name} app\n\n"

        for model in models:
            model_name = model.get('modelName', 'DefaultModel')
            fields = model.get('fields', [])

            models_code += f"class {model_name}(models.Model):\n"
            for field in fields:
                field_name = field.get('fieldName')
                field_type = field.get('fieldType')
                attributes = field.get('attributes', {})
                attr_parts = []

                for key, value in attributes.items():
                    if key != 'undefined':
                        if isinstance(value, str):
                            if field_type == 'ForeignKey' and key == 'on_delete':
                                attr_parts.append(f'{key}={value}')
                            elif key == 'max_length':
                                # Convert max_length to integer
                                attr_parts.append(f'{key}={int(value)}')
                            else:
                                attr_parts.append(f'{key}="{value}"')
                        else:
                            attr_parts.append(f'{key}={value}')

                attr_str = ', '.join(attr_parts)
                models_code += f"    {field_name} = models.{field_type}({attr_str})\n"

            models_code += '\n'

        models_file_path = os.path.join(settings.BASE_DIR, app_name, 'models.py')
        with open(models_file_path, 'a') as models_file:
            models_file.write(models_code)

        self.stdout.write(self.style.SUCCESS(f'Models for app "{app_name}" have been generated.'))

    
    def add_apps_to_installed_apps(self, app_name, schema_apps=None):
        """
        Add an app to INSTALLED_APPS setting of settings.py file.
        Args:
        app_name (str): Name of the app to be added.
        schema_apps (list, optional): List of app names generated from a schema.
        If provided, these apps will be added in between 'app_builder' and 'Authentication'.
        """
        project_name = settings.SETTINGS_MODULE.split('.')[0]
        settings_path = os.path.join(settings.BASE_DIR, project_name, 'settings.py')

        with open(settings_path, 'r+') as settings_file:
            settings_content = settings_file.read()

            if f"'{app_name}'" not in settings_content:
                # Find the index where 'app_builder' and 'Authentication' are located
                app_builder_index = settings_content.find("'app_builder'")
                authentication_index = settings_content.find("'Authentication'")

                # Determine where to insert 'app_name'
                if schema_apps:
                    # If schema_apps are provided, insert 'app_name' between 'app_builder' and 'Authentication'
                    if app_builder_index != -1 and authentication_index != -1:
                        insert_index = min(app_builder_index, authentication_index)
                    else:
                        # If 'app_builder' or 'Authentication' is not found, insert 'app_name' at the end
                        insert_index = len(settings_content)
                else:
                    # If schema_apps are not provided, insert 'app_name' at the end
                    insert_index = len(settings_content)

                # Generate the new INSTALLED_APPS line
                new_installed_apps = f"INSTALLED_APPS = [\n    'jazzmin',\n    'django.contrib.admin',\n    'django.contrib.auth',\n    'django.contrib.contenttypes',\n    'django.contrib.sessions',\n    'django.contrib.messages',\n    'django.contrib.staticfiles',\n    'app_builder',\n    'Authentication',\n"
                
                if schema_apps:
                    new_installed_apps += ',\n'.join([f"    '{app}'," for app in schema_apps]) + '\n'
                
                new_installed_apps += "]"

                # Replace the old INSTALLED_APPS line with the new one
                new_settings_content = settings_content[:insert_index] + new_installed_apps + settings_content[insert_index:]

                settings_file.seek(0)
                settings_file.write(new_settings_content)
                settings_file.truncate()

                self.stdout.write(self.style.SUCCESS(f"Added '{app_name}' to INSTALLED_APPS."))
            else:
                self.stdout.write(self.style.NOTICE(f"'{app_name}' is already listed in INSTALLED_APPS."))
    
    def generate_serializers_from_schema(self, schema, app_name):
        """
        Generates serializers code based on a given schema.
        Parameters:
        schema (dict): The dictionary containing all the information about the database schema.
        app_name (str): The name of the Django app.
        Function:
        This function generates serializers for each model in the schema and writes them to serializers.py in the app directory.
        If serializers.py doesn't exist, it creates the file.
        """
        serializers_code = ""

        # Get the models from the schema
        models = schema.get("models", [])
        serializers_code += f'from rest_framework import serializers\n'
        for model in models:
            model_name = model["modelName"]
            fields = model["fields"]

            # Generate code for the serializer class
            serializers_code += f'from .models import {model_name}\n\n'
            serializers_code += f'class {model_name}Serializer(serializers.ModelSerializer):\n'
            serializers_code += f'    class Meta:\n'
            serializers_code += f'        model = {model_name}\n'
            serializers_code += f'        fields = ['
            
            # Include fields in the serializer
            for field in fields:
                field_name = field["fieldName"]
                serializers_code += f"'{field_name}', "
            
            serializers_code += f"]\n\n"

        # Define the serializers.py file path
        serializers_file_path = os.path.join(app_name, "serializers.py")

        # Check if serializers.py exists, if not, create it
        if not os.path.exists(serializers_file_path):
            with open(serializers_file_path, 'w') as serializers_file:
                serializers_file.write(serializers_code)
        else:
            # If serializers.py already exists, append the generated serializers to it
            with open(serializers_file_path, 'a') as serializers_file:
                serializers_file.write(serializers_code)
        
        self.stdout.write(self.style.SUCCESS(f"Added '{app_name}' serializers."))

    def generate_views_from_schema(self, schema, app_name):
        """
        Generates viewsets code based on a given schema.
        Parameters:
        schema (dict): The dictionary containing all the information about the database schema.
        app_name (str): The name of the Django app.
        Function:
        This function generates viewsets for each model in the schema and writes them to views.py in the app directory.
        If views.py doesn't exist, it creates the file.
        """
        views_code = ""

        # Get the models from the schema
        models = schema.get("models", [])
        views_code += f'from rest_framework import viewsets\n'
        for model in models:
            model_name = model["modelName"]

            # Generate code for the viewset class
            views_code += f'from .models import {model_name}\n'
            views_code += f'from .serializers import {model_name}Serializer\n\n'
            views_code += f'class {model_name}ViewSet(viewsets.ModelViewSet):\n'
            views_code += f'    queryset = {model_name}.objects.all()\n'
            views_code += f'    serializer_class = {model_name}Serializer\n\n'

        # Define the views.py file path
        views_file_path = os.path.join(app_name, "views.py")

        # Check if views.py exists, if not, create it
        if not os.path.exists(views_file_path):
            with open(views_file_path, 'w') as views_file:
                views_file.write(views_code)
        else:
            # If views.py already exists, append the generated views to it
            with open(views_file_path, 'a') as views_file:
                views_file.write(views_code)
        
        self.stdout.write(self.style.SUCCESS(f"Added '{app_name}' api views."))

    def generate_urls_from_schema(self, schema, app_name):
        """
        Generates URL patterns based on a given schema and adds them to the app's urls.py file.
        Parameters:
        schema (dict): The dictionary containing all the information about the database schema.
        app_name (str): The name of the Django app.
        Function:
        This function generates URL patterns for each model's viewset in the schema and adds them to the app's urls.py file.
        If urls.py doesn't exist, it creates the file.
        """
        urls_code = ""

        # Get the models from the schema
        models = schema.get("models", [])
        # Generate URL pattern code for the model's viewset
        urls_code += f'from django.urls import path, include\n'
        urls_code += f'from rest_framework.routers import DefaultRouter\n'
        urls_code += f'router = DefaultRouter()\n'
        for model in models:
            model_name = model["modelName"]
            urls_code += f'from .views import {model_name}ViewSet\n\n'
            urls_code += f'router.register(r"{model_name.lower()}", {model_name}ViewSet)\n\n'

        # Define the urls.py file path for the app
        urls_file_path = os.path.join(app_name, "urls.py")

        # Check if urls.py exists, if not, create it
        if not os.path.exists(urls_file_path):
            with open(urls_file_path, 'w') as urls_file:
                urls_file.write(urls_code)
        else:
            # If urls.py already exists, append the generated URL patterns to it
            with open(urls_file_path, 'a') as urls_file:
                urls_file.write(urls_code)

        # Add the urlpatterns for the app
        urlpatterns_code = f'''
urlpatterns = [
    path('', include(router.urls)),  # Include generated URLs for {app_name}
]
    '''
        with open(urls_file_path, 'a') as urls_file:
            urls_file.write(urlpatterns_code)

        self.stdout.write(self.style.SUCCESS(f"Added URL patterns to '{app_name}' app's urls.py."))

    def generate_admin_code_from_schema(self, schema, app_name):
        """
        Generates admin code based on a given schema.
        Parameters:
        schema (dict): The dictionary containing all the information about the database schema.
        Function:
        This function generates the necessary code to create an admin model from a given schema. It first checks whether there is any table that has a foreign key
        """
        admin_code = ""

        # Get the models from the schema
        models = schema.get("models", [])

        for model in models:
            model_name = model["modelName"]
            fields = model["fields"]

            # Define list_display and search_fields options based on fields
            list_display = [field["fieldName"] for field in fields]
            search_fields = list_display

            # Generate code for the model's admin class using the @admin.register decorator
            admin_code += f'from {app_name}.models import {model_name}\n'
            admin_code += f'@admin.register({model_name})\n'
            admin_code += f'class {model_name}Admin(admin.ModelAdmin):\n'
            admin_code += f'    list_display = {list_display}\n'
            admin_code += f'    search_fields = {search_fields}\n\n'

        return admin_code


    def create_or_append_admin_file(self, app_name, admin_code):
        # Construct the path to the app's admin.py file
        app_directory = os.path.join(settings.BASE_DIR, app_name)
        admin_file_path = os.path.join(app_directory, 'admin.py')

        # Check if the admin.py file exists in the app directory
        if os.path.exists(admin_file_path):
            # Append the admin code to the existing admin.py file
            with open(admin_file_path, 'a') as admin_file:
                admin_file.write(admin_code)
        else:
            # Create a new admin.py file with the generated admin code
            with open(admin_file_path, 'w') as admin_file:
                admin_file.write(admin_code)
 
    # Method to create the 'Authentication' app and add content
    def create_authentication_app(self):

        app_name = 'Authentication'

        # Run the startapp command to create the app
        os.system(f'python manage.py startapp {app_name}')

        # Add content to models.py
        models_code = '''
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def image_size_validator(value):
    max_size = 10485760

    if value.size > max_size:
        raise ValidationError(f"Image must be less than 10MB")

class ApplicationUser(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pictures', blank=True, null=True, validators=[image_size_validator, FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'gif'])])
    contact = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
'''

        # Get the app directory
        app_directory = os.path.join(os.path.join(settings.BASE_DIR, app_name))

        # Create a models.py file in the app directory and add the models code
        models_file_path = os.path.join(app_directory, 'models.py')
        with open(models_file_path, 'w') as models_file:
            models_file.write(models_code)

        # Add content to admin.py
        admin_code = '''
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ApplicationUser

class ApplicationUserAdmin(UserAdmin):
    list_display = ('username', 'email','contact', 'profile_pic_image')

    def profile_pic_image(self, obj):
        if obj.profile_pic:
            return format_html(f'<img src ="{obj.pro8file_pic.url}" width="150" height="150" alt="{obj.username}"/>')
        else:
            return format_html("<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAI0AAACNCAMAAAC9gAmXAAAAY1BMVEX///8AAADi4uL39/coKCg7OzsYGBjAwMDm5ua6urrLy8vt7e2WlpY1NTXW1tZQUFCdnZ3c3NwREREiIiIdHR2lpaWLi4swMDBVVVWxsbGBgYFcXFxnZ2dvb296enpCQkJJSUkC9QxWAAAESUlEQVR4nO1aaZOiMBCVSyOMICAo6Ij//1duuVN0mkPI0c1s1eZ9nMnxDH3ldXY7BwcHBwcHBwcHBwcHPohjVd+i8lJGt7Y6+r/IJEjr7uphhF2dBr/Dpcq8OWTV9nyS8yyVH3yJbckcowUynndqNuTi3xe5vHHbzKDj/SoZz9sftiGzZDED69mCTD3ZNoyyLIvCyd+f25O5NXEugiAQftyMzanelsx97DvHIaGWl8wR75XF0zgXxDc8hNXTc+xN1YdBVSHHFCkfmeAk9zl9jrcChcYrX5pAvn1b2iVA1sPm577c47Ey9FsOzZnYyC1eq2NvysQNkcIG4XqOTqSJxSxsHlrrxzD6zkEm0Dx7+V0TBjbgUArf6Q0BRSqDW0mvVQ33kEQWo4EZpHurlpkJo5Mf9D0WLIc+Wz31l276Kd/kbPrcU6gfu9/n2BM1meDSe5TGpN6rLtRm7PdlQqYx6a5/nmqA0KpjA61O8DZio1PrfvWTqG8z4OBnjUnNP8WmYmfzT3wpKG50rBgiJrUVi97DXxqTeoGH3MMh+pUakay/DJNHP8gMnvoNKe3PkzwzyEj26VI3BbgUfdYEp1JPDVCfHcnZQKLyVFUrWZ8x6FwP3XMH/34w3H7BCvZqdpyX+pamDnmDeSmNl2oyizAAJ69UjEqlh96j3oDwoRJbkdLDJOHIw9mvXR8TqUlyaZGJFK26ZVsIXjBS+fqljUbucV2KIVjcYlT+UNdl/7lKwFr7i4/MTmCJup3/WkGLxpSs7YYU7eTtq6kxJ9WgCcEoib5R4b28Uz30df9r2CnSKaKN0HhDlG1zSH3hp4emHbcaOFLCCp33Jwuv4UyXaAMys3RmsVH/TnQKXLrNepv+dZVMyCVaj5FP+2VzaJm9+y+SWqWr+UbRckizA1TThuFnXHjjTb7eeh4iY/xch8v8nkXURcWHf3H5+SAd/iB6nmPpySI+t9M3BN8sZXEwfsRxOuczWTM/n0bjOgZjFqNf3S7UN6NDvJLHnnRgMpcV503qEg9XvIEpY1BmeXeFO8NjwJ606Bp0njs13SxGlTqtnoTz0kPVKBPUavVCOs/Cp26kiXqETSqcJfX0xBjNJHpTgZYsdKVWfJkhEUYT6dsGtigQHYr6qzU/mTdimcAIbuToO5klQPRIxl5Sl1nH9KUR6PteaUtG/jJz0VdmOMvyIoHrgUVwF5C0Irt0Lu9ONg3/M9HhgNVcrZbpSJYBAd1SDpfr2LgVxBqdvvMcwJAtYk5CdDT4cMwDMri3pS9gWdLcjqGSsH9iCSHQ+KVSAF/bvnKDhszJ9JghRRXWZHY7iICmXgWlG8VbWIiAporX0/bnYBg9xMDoby2LurkqBIR1wwX66TQFNsgbZquJfjrN20oIF2YnDbo5zYNuiDhm1TpUEzS6r+Vy4JM0ghCkGbNKifi9SkzEhkbvyGnN0MHBwcHBwcHBwcHhP8Qf+m4owMUfTr8AAAAASUVORK5CYII=' height='150' width='150'")
admin.site.register(ApplicationUser, ApplicationUserAdmin)

'''
        # Create an admin.py file in the app directory and add the admin code
        admin_file_path = os.path.join(app_directory, 'admin.py')
        with open(admin_file_path, 'w') as admin_file:
            admin_file.write(admin_code)

        self.stdout.write(self.style.SUCCESS(f'App "{app_name}" has been created with content.'))


    def generate_settings_content(self, schema_generated_apps, project_name):
        # Define the content of jazzmin_settings_content as a string
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
    'app_builder',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'dj_rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
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
        'rest_framework.authentication.SessionAuthentication',
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
    re_path(r'^', include('app_builder.urls')),
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

        # Define the path to the settings.py file
        settings_file_path = os.path.join(settings.BASE_DIR, project_name, 'settings.py')
        urls_file_path = os.path.join(settings.BASE_DIR, project_name, 'urls.py')

        # Write the generated content to the settings.py file
        with open(settings_file_path, 'w') as settings_file:
            settings_file.write(full_settings_content)
        with open(urls_file_path, 'w') as urls_file:
            urls_file.write(urls_content)
        # Print a success message
        self.stdout.write(self.style.SUCCESS("settings.py and urls.py file has been updated successfully."))
    
    def index_file_generator(self, project_name):
        # Define the path to the templates folder
        templates_folder = os.path.join(settings.BASE_DIR, 'Authentication', 'templates')
        # Check if the templates folder exists, and create it if not
        if not os.path.exists(templates_folder):
            os.makedirs(templates_folder)
        # Define the path to the index.html file inside the templates folder
        index_html_path = os.path.join(templates_folder, "index.html")
        index_html_content = generate_index_html_content()
        # Write the content to the index.html file
        with open(index_html_path, "w") as index_file:
            index_file.write(index_html_content)
        # Print a success message
        self.stdout.write(self.style.SUCCESS("index.html file has been generated and updated successfully in the templates folder."))