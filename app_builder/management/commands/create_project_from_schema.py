from django.core.management import call_command, BaseCommand
import json
import os
from django.conf import settings
import subprocess

class Command(BaseCommand):
    help = 'Generate Django apps, models, migrations, admin, and DRF views from JSON schema files.'

    def handle(self, *args, **options):
        """
        Generates the necessary code for a new app based on a given JSON Schema file.
        The command takes one argument: the path to the JSON Schema file.
        It will generate all of the following in the same directory as the schema file:
        - A Django model (with fields corresponding to each property in the schema)
        - A migration file that adds this model to the database
        - An admin class with list/detail view templates
        - A Django Rest Framework API Viewset with serializer classes for both list and detail views
        - A URL configuration entry pointing at the API Viewset
        """
        # Define the path to the schema directory next to manage.py
        schema_directory = os.path.join(settings.BASE_DIR, 'schema')

        # Check if the schema directory exists
        if not os.path.exists(schema_directory):
            self.stdout.write(self.style.ERROR('Schema directory does not exist'))
            return

        # Find schema files ending with "_schema.json" in the directory
        schema_files = [f for f in os.listdir(schema_directory) if f.endswith('_schema.json')]

        if not schema_files:
            self.stdout.write(self.style.ERROR('No schema files found in the directory'))
            return

        try:
            for schema_file_name in schema_files:
                schema_file_path = os.path.join(schema_directory, schema_file_name)

                # Load the schema from the JSON file
                with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
                    schema = json.load(schema_file)

                # Extract project name, apps, and other schema data
                project_name = schema.get('projectName')
                apps = schema.get('apps', [])
                self.stdout.write(self.style.SUCCESS(f'Project Name (from {schema_file_name}): {project_name}\n'))

                # Create the Django project
                if not self.create_django_project(project_name):
                    continue

                self.create_authentication_app(project_name, schema)

                # Create the Django apps within the project
                app_names = [app.get('appName') for app in apps]
                if not self.create_apps(project_name, app_names, schema):
                    continue

                self.generate_settings_content(app_names, project_name)
                
                self.index_file_generator(project_name)

                self.stdout.write(self.style.ERROR(f'''
Project (from {schema_file_name}): {project_name} is built successfully.\n 
Enter following command:\n\t
    cd {project_name}
    python manage.py makemigrations
    python manage.py migrate
    echo "from django.contrib.auth import get_user_model;User = get_user_model(); User.objects.create_superuser('admin', 'admin@email.com', 'pass')" | python manage.py shell
    python manage.py runserver
            '''))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON format in one or more schema files'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

    def create_apps(self, project_name, app_names, schema):
        """
        Create Django apps within the project based on the provided app names and schema.

        Args:
        project_name (str): The name of the Django project.
        app_names (list): A list of app names to create.
        schema (dict): The JSON schema representing the application's structure.

        Returns:
        bool: True if all apps were created successfully, False otherwise.
        """
        try:
            project_directory = os.path.join(settings.BASE_DIR, project_name)

            for app_name in app_names:
                if not self.create_app(project_name, app_name):
                    continue

                # Fetch the app schema based on app_name from the schema dictionary
                app_schema = next((app for app in schema.get("apps", []) if app.get("appName") == app_name), None)

                # After creating the app, create models for the app based on the schema
                if app_schema:
                    self.create_models_for_app(project_name, app_name, app_schema)
                    self.generate_serializers_for_app(project_name, app_name, app_schema)
                    self.generate_and_save_admin_code_for_app(project_name, app_name, app_schema)
                    self.generate_and_save_viewsets_code_for_app(project_name, app_name, app_schema)
                    self.generate_and_save_urls_code_for_app(project_name, app_name, app_schema)
                    

            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while creating apps: {str(e)}"))
            return False

    def create_app(self, project_name, app_name):
        """
        Create a Django app within the project.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app to create.

        Returns:
        bool: True if the app was created successfully, False otherwise.
        """
        try:
            project_directory = os.path.join(settings.BASE_DIR, project_name)

            # Create the app within the project directory
            subprocess.run(['python', 'manage.py', 'startapp', app_name], check=True, cwd=project_directory)

            self.stdout.write(self.style.SUCCESS(f'App Created: {app_name}'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while creating app {app_name}: {str(e)}"))
            return False

    def create_django_project(self, project_name):
        """
        Create a Django project.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app to create.

        Returns:
        bool: True if the project was created successfully, False otherwise.
        """
        try:
            # Create the Django project one level above the current project directory
            subprocess.run(['django-admin', 'startproject', project_name, '--extension=py,yml'], check=True)

            self.stdout.write(self.style.SUCCESS(f'Project Created: {project_name}'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while creating project {project_name}: {str(e)}"))
            return False

    def create_models_for_app(self, project_name, app_name, app_schema):
        """
        Create Django models for an app based on the provided schema.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app to create models for.
        app_schema (dict): The schema for the app.

        Returns:
        bool: True if models were created successfully, False otherwise.
        """
        try:
            # Create a directory for the models
            models_dir = os.path.join(settings.BASE_DIR, project_name, app_name)
            os.makedirs(models_dir, exist_ok=True)

            # Create models.py file and write the models code
            models_py_path = os.path.join(models_dir, 'models.py')

            models_code = f"# Models for {app_name} app\n\n"
            models_code += f"from django.db import models \n\n\n"
            # Iterate through models in the app's schema
            for model_schema in app_schema.get('models', []):
                model_name = model_schema.get('modelName', 'DefaultModel')
                fields = model_schema.get('fields', [])
                
                models_code += f"class {model_name}(models.Model):\n"
                for field in fields:
                    field_name = field.get('fieldName')
                    field_type = field.get('fieldType')
                    attributes = field.get('attributes', {})

                    attr_str = ', '.join([f'{key}={value}' for key, value in attributes.items() if key != 'undefined'])
                    models_code += f"    {field_name} = models.{field_type}({attr_str})\n"
                    models_code += "\n"  # Add newline after each model definition

                models_code += '\n'

            with open(models_py_path, 'w') as models_file:
                models_file.write(models_code)

            self.stdout.write(self.style.SUCCESS(f'Models for app "{app_name}" have been generated.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while creating models for app {app_name}: {str(e)}"))
            return False

    def generate_serializers_for_app(self, project_name, app_name, app_schema):
        """
        Generate serializers for an app based on the provided schema and create the serializers.py file if it doesn't exist.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app to generate serializers for.
        app_schema (dict): The schema for the app.

        Returns:
        bool: True if serializers were generated successfully, False otherwise.
        """
        try:
            # Create a directory for the serializers
            serializers_dir = os.path.join(settings.BASE_DIR, project_name, app_name)
            os.makedirs(serializers_dir, exist_ok=True)

            # Create serializers.py file and write the serializers code
            serializers_py_path = os.path.join(serializers_dir, 'serializers.py')

            serializers_code = f"# Serializers for {app_name} app\n\n"
            serializers_code += f"from rest_framework import serializers\n\n"
            
            # Iterate through models in the app's schema
            for model_schema in app_schema.get('models', []):
                model_name = model_schema.get('modelName', 'DefaultModel')
                serializer_code = f"from .models import {model_name}\n"
                # Create a serializer for the model
                serializer_code += f"class {model_name}Serializer(serializers.ModelSerializer):\n"
                serializer_code += f"    class Meta:\n"
                serializer_code += f"        model = {model_name}\n"
                serializer_code += f"        fields = '__all__'\n"
                
                serializers_code += serializer_code
                serializers_code += "\n"  # Add newline after each serializer definition

            with open(serializers_py_path, 'w') as serializers_file:
                serializers_file.write(serializers_code)

            self.stdout.write(self.style.SUCCESS(f'Serializers for app "{app_name}" have been generated.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while generating serializers for app {app_name}: {str(e)}"))
            return False
        
    def generate_and_save_admin_code_for_app(self, project_name, app_name, app_schema):
        """
        Generate and save admin registration code for models in an app with custom list_display and search_fields.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app.
        app_schema (dict): The schema for the app.

        Returns:
        bool: True if admin code was generated and saved successfully, False otherwise.
        """
        try:
            # Create a directory for the admin
            admin_dir = os.path.join(settings.BASE_DIR, project_name, app_name)
            os.makedirs(admin_dir, exist_ok=True)

            # Create admin.py file and write the admin code
            admin_py_path = os.path.join(admin_dir, 'admin.py')

            admin_code = f"# Admin for {app_name} app\n\n"
            admin_code += f"from django.contrib import admin\n"

            # Iterate through models in the app's schema
            for model_schema in app_schema.get('models', []):
                model_name = model_schema.get('modelName', 'DefaultModel')
                fields = model_schema.get('fields', [])

                # Define list_display and search_fields options based on fields
                list_display = [field['fieldName'] for field in fields]
                search_fields = list_display

                # Generate code for the model's admin class using the @admin.register decorator
                admin_code += f'from {app_name}.models import {model_name}\n\n'
                admin_code += f'@admin.register({model_name})\n'
                admin_code += f'class {model_name}Admin(admin.ModelAdmin):\n'
                admin_code += f'    list_display = {list_display}\n'
                admin_code += f'    search_fields = {search_fields}\n\n\n'

            with open(admin_py_path, 'w') as admin_file:
                admin_file.write(admin_code)

            self.stdout.write(self.style.SUCCESS(f'Admin for app "{app_name}" has been generated and saved.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while generating and saving admin for app {app_name}: {str(e)}"))
            return False

    def generate_and_save_viewsets_code_for_app(self, project_name, app_name, app_schema):
        """
        Generate and save DRF viewsets code for models in an app.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app.
        app_schema (dict): The schema for the app.

        Returns:
        bool: True if viewsets code was generated and saved successfully, False otherwise.
        """
        try:
            # Create a directory for the views
            views_dir = os.path.join(settings.BASE_DIR, project_name, app_name)
            os.makedirs(views_dir, exist_ok=True)

            # Create views.py file and write the viewsets code
            views_py_path = os.path.join(views_dir, 'views.py')

            views_code = f"# Views for {app_name} app\n\n"
            views_code += f"from rest_framework import viewsets\n"
            
            # Iterate through models in the app's schema
            for model_schema in app_schema.get('models', []):
                model_name = model_schema.get('modelName', 'DefaultModel')

                # Generate code for the viewset class
                views_code += f"from .models import {model_name}\n"
                views_code += f"from .serializers import {model_name}Serializer\n\n"
                views_code += f"class {model_name}ViewSet(viewsets.ModelViewSet):\n"
                views_code += f"    queryset = {model_name}.objects.all()\n"
                views_code += f"    serializer_class = {model_name}Serializer\n"

            with open(views_py_path, 'w') as views_file:
                views_file.write(views_code)

            self.stdout.write(self.style.SUCCESS(f'Viewsets for app "{app_name}" have been generated and saved.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while generating and saving viewsets for app {app_name}: {str(e)}"))
            return False

    def generate_and_save_urls_code_for_app(self, project_name, app_name, app_schema):
        """
        Generate and save URL patterns code for an app.

        Args:
        project_name (str): The name of the Django project.
        app_name (str): The name of the app.
        app_schema (dict): The schema for the app.

        Returns:
        bool: True if URL patterns code was generated and saved successfully, False otherwise.
        """
        try:
            # Create a directory for the app's URLs
            urls_dir = os.path.join(settings.BASE_DIR, project_name, app_name)
            os.makedirs(urls_dir, exist_ok=True)

            # Create urls.py file and write the URL patterns code
            urls_py_path = os.path.join(urls_dir, 'urls.py')

            urls_code = f"# URL patterns for {app_name} app\n\n"
            urls_code += f"from django.urls import path, include\n"
            urls_code += f'from rest_framework.routers import DefaultRouter\n'
            urls_code += f"router = DefaultRouter()\n\n"
            urls_code += f"from rest_framework.routers import DefaultRouter\n\n"
            # Iterate through models in the app's schema
            for model_schema in app_schema.get('models', []):
                model_name = model_schema.get('modelName', 'DefaultModel')

                # Generate code for the model's URL patterns
                urls_code += f"from .views import {model_name}ViewSet\n"
                urls_code += f"router.register(r'{model_name.lower()}s', {model_name}ViewSet)\n\n"

            urls_code += f"urlpatterns = [\n"
            urls_code += f"    path('', include(router.urls)),\n"
            urls_code += f"]\n"

            with open(urls_py_path, 'w') as urls_file:
                urls_file.write(urls_code)

            self.stdout.write(self.style.SUCCESS(f'URL patterns for app "{app_name}" have been generated and saved.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while generating and saving URL patterns for app {app_name}: {str(e)}"))
            return False

    def create_authentication_app(self, project_name, schema):
        """
        Create the 'Authentication' app with the specified models and admin code inside the project folder.

        Args:
        project_name (str): The name of the Django project.
        schema (dict): The schema for the project.

        Returns:
        bool: True if the app was created successfully, False otherwise.
        """
        try:
            app_name = 'Authentication'

            # Check if the project directory exists
            project_directory = os.path.join(settings.BASE_DIR, project_name)
            if not os.path.exists(project_directory):
                self.stdout.write(self.style.ERROR(f'Project directory "{project_directory}" does not exist.'))
                return False

            # Check if the app directory already exists
            app_directory = os.path.join(project_directory, app_name)
            if os.path.exists(app_directory):
                self.stdout.write(self.style.ERROR(f'App directory "{app_directory}" already exists.'))
                return False
            
            #change directory to project folder
            os.chdir(project_directory)
            # Run the startapp command to create the app
            os.system(f'python manage.py startapp {app_name}')

            # Get the app directory
            app_directory = os.path.join(project_directory, app_name)

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
    list_display = ('username', 'email', 'contact', 'profile_pic_image')

    def profile_pic_image(self, obj):
        if obj.profile_pic:
            return format_html(f'<img src ="{obj.profile_pic.url}" width="150" height="150" alt="{obj.username}"/>')
        else:
            return format_html("<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAI0AAACNCAMAAAC9gAmXAAAAY1BMVEX///8AAADi4uL39/coKCg7OzsYGBjAwMDm5ua6urrLy8vt7e2WlpY1NTXW1tZQUFCdnZ3c3NwREREiIiIdHR2lpaWLi4swMDBVVVWxsbGBgYFcXFxnZ2dvb296enpCQkJJSUkC9QxWAAAESUlEQVR4nO1aaZOiMBCVSyOMICAo6Ij//1duuVN0mkPI0c1s1eZ9nMnxDH3ldXY7BwcHBwcHBwcHBwcHPohjVd+i8lJGt7Y6+r/IJEjr7uphhF2dBr/Dpcq8OWTV9nyS8yyVH3yJbckcowUynndqNuTi3xe5vHHbzKDj/SoZz9sftiGzZDED69mCTD3ZNoyyLIvCyd+f25O5NXEugiAQftyMzanelsx97DvHIaGWl8wR75XF0zgXxDc8hNXTc+xN1YdBVSHHFCkfmeAk9zl9jrcChcYrX5pAvn1b2iVA1sPm577c47Ey9FsOzZnYyC1eq2NvysQNkcIG4XqOTqSJxSxsHlrrxzD6zkEm0Dx7+V0TBjbgUArf6Q0BRSqDW0mvVQ33kEQWo4EZpHurlpkJo5Mf9D0WLIc+Wz31l276Kd/kbPrcU6gfu9/n2BM1meDSe5TGpN6rLtRm7PdlQqYx6a5/nmqA0KpjA61O8DZio1PrfvWTqG8z4OBnjUnNP8WmYmfzT3wpKG50rBgiJrUVi97DXxqTeoGH3MMh+pUakay/DJNHP8gMnvoNKe3PkzwzyEj26VI3BbgUfdYEp1JPDVCfHcnZQKLyVFUrWZ8x6FwP3XMH/34w3H7BCvZqdpyX+pamDnmDeSmNl2oyizAAJ69UjEqlh96j3oDwoRJbkdLDJOHIw9mvXR8TqUlyaZGJFK26ZVsIXjBS+fqljUbucV2KIVjcYlT+UNdl/7lKwFr7i4/MTmCJup3/WkGLxpSs7YYU7eTtq6kxJ9WgCcEoib5R4b28Uz30df9r2CnSKaKN0HhDlG1zSH3hp4emHbcaOFLCCp33Jwuv4UyXaAMys3RmsVH/TnQKXLrNepv+dZVMyCVaj5FP+2VzaJm9+y+SWqWr+UbRckizA1TThuFnXHjjTb7eeh4iY/xch8v8nkXURcWHf3H5+SAd/iB6nmPpySI+t9M3BN8sZXEwfsRxOuczWTM/n0bjOgZjFqNf3S7UN6NDvJLHnnRgMpcV503qEg9XvIEpY1BmeXeFO8NjwJ606Bp0njs13SxGlTqtnoTz0kPVKBPUavVCOs/Cp26kiXqETSqcJfX0xBjNJHpTgZYsdKVWfJkhEUYT6dsGtigQHYr6qzU/mTdimcAIbuToO5klQPRIxl5Sl1nH9KUR6PteaUtG/jJz0VdmOMvyIoHrgUVwF5C0Irt0Lu9ONg3/M9HhgNVcrZbpSJYBAd1SDpfr2LgVxBqdvvMcwJAtYk5CdDT4cMwDMri3pS9gWdLcjqGSsH9iCSHQ+KVSAF/bvnKDhszJ9JghRRXWZHY7iICmXgWlG8VbWIiAporX0/bnYBg9xMDoby2LurkqBIR1wwX66TQFNsgbZquJfjrN20oIF2YnDbo5zYNuiDhm1TpUEzS6r+Vy4JM0ghCkGbNKifi9SkzEhkbvyGnN0MHBwcHBwcHBwcHhP8Qf+m4owMUfTr8AAAAASUVORK5CYII=' height='150' width='150' alt=''/>")

admin.site.register(ApplicationUser, ApplicationUserAdmin)
    '''

            # Create an admin.py file in the app directory and add the admin code
            admin_file_path = os.path.join(app_directory, 'admin.py')
            with open(admin_file_path, 'w') as admin_file:
                admin_file.write(admin_code)

            self.stdout.write(self.style.SUCCESS(f'App "{app_name}" has been created with content inside the project folder "{project_name}".'))

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while creating the 'Authentication' app: {str(e)}"))
            return False

    def index_file_generator(self, project_name):
            # Define the path to the templates folder
            from .utils import generate_index_html_content
            templates_folder = os.path.join(settings.BASE_DIR,project_name, 'Authentication', 'templates')
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

    def generate_settings_content(self, schema_generated_apps, project_name):
        from .utils import settings_content
        full_settings_content, urls_content = settings_content(project_name, schema_generated_apps)
        # Define the path to the settings.py file
        settings_file_path = os.path.join(settings.BASE_DIR, project_name, project_name , 'settings.py')
        urls_file_path = os.path.join(settings.BASE_DIR, project_name, project_name , 'urls.py')

        # Write the generated content to the settings.py file
        with open(settings_file_path, 'w') as settings_file:
            settings_file.write(full_settings_content)
        with open(urls_file_path, 'w') as urls_file:
            urls_file.write(urls_content)
        # Print a success message
        self.stdout.write(self.style.SUCCESS("settings.py and urls.py file has been updated successfully."))
    
