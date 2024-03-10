from django.db import models
from django.shortcuts import render
import inspect

# Define a placeholder for required arguments.
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.http import JsonResponse
from django.utils.text import slugify
from django.conf import settings

def index(request):
    return render(request, 'app_builder/index.html')

@csrf_exempt
def save_model_schema(request):
    if request.method == 'POST':
        try:
            # Load the project schema from the request body
            project_schema = json.loads(request.body)

            # Extract the project name
            project_name = project_schema.get('projectName', 'default_project')
            project_slug = slugify(project_name)

            # Ensure the 'schema' directory exists at the project level, next to manage.py
            schema_directory = os.path.join(settings.BASE_DIR, 'schema')
            os.makedirs(schema_directory, exist_ok=True)

            # Construct the file path using the project slug
            file_path = os.path.join(schema_directory, f'{project_slug}_schema.json')

            # Write the project schema to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(project_schema, file, indent=4)

            # Respond with success
            return JsonResponse({
                'status': 'success',
                'message': 'Project schema saved successfully.'
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)

def get_all_models():
    all_models = apps.get_models()
    return [model._meta.object_name for model in all_models]

def convert_bools_for_js(value):
    if isinstance(value, bool):
        return str(value).lower()
    return value

# Constants for required and not required options
REQUIRED = 'required'
NOT_REQUIRED = 'not_required'

SPECIAL_FIELD_ARGS = {
    'ForeignKey': {
        'to': REQUIRED,
        'on_delete': 'models.CASCADE',  
        'related_name' : REQUIRED , 
    },
    'OneToOneField': {
        'to': REQUIRED,
        'on_delete': 'models.CASCADE',
    },
    'ManyToManyField': {
        'to': REQUIRED,
    },
    'CharField': {
        'max_length': REQUIRED, 
    },
    'DecimalField':{
        'decimal_places': NOT_REQUIRED,
        'max_digits': REQUIRED,
        
    }
}

def get_field_options(field_class):
    field_name = field_class.__name__
    if field_name in SPECIAL_FIELD_ARGS:
        return SPECIAL_FIELD_ARGS[field_name]

    # Attempt to instantiate the field to get default arguments
    try:
        field_instance = field_class()
        name, path, args, kwargs = field_instance.deconstruct()
        return kwargs
    except TypeError:
        # Handle cases where instantiation fails
        return {arg: REQUIRED if arg in SPECIAL_FIELD_ARGS.get(field_name, {}) else NOT_REQUIRED for arg in inspect.getfullargspec(field_class.__init__).args if arg != 'self'}

def get_all_model_fields():
    model_field_classes = {}
    for field_name in dir(models):
        field_class = getattr(models, field_name)
        if isinstance(field_class, type) and issubclass(field_class, models.Field):
            field_options = get_field_options(field_class)
            model_field_classes[field_name] = field_options
    return model_field_classes

def model_schema_view(request):
    model_fields = get_all_model_fields()
    
    # Convert Python booleans to JavaScript booleans
    for field, options in model_fields.items():
        for key, value in options.items():
            options[key] = convert_bools_for_js(value)
    all_models = get_all_models()

    return render(request, 'app_builder/model_schema_form.html', {
        'model_fields': model_fields,
        'all_models': all_models
    })
