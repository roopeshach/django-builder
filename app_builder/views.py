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

@csrf_exempt
def save_model_schema(request):
    if request.method == 'POST':
        try:
            # Load the list of app schemas from the request body
            all_app_schemas = json.loads(request.body)

            # Iterate through each app's schema
            for app_schema in all_app_schemas:
                app_name = app_schema.get('appName', 'default_app')
                app_slug = slugify(app_name)
                
                # Ensure the 'schema' directory exists at the project level, next to manage.py
                schema_directory = os.path.join(settings.BASE_DIR, 'schema')
                os.makedirs(schema_directory, exist_ok=True)

                # Construct the file path using the app slug
                file_path = os.path.join(schema_directory, f'{app_slug}_schema.json')
                
                # Write the schema to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(app_schema, file, indent=4)

            # Respond with success
            return JsonResponse({
                'status': 'success',
                'message': 'All app schemas saved successfully.'
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


REQUIRED = 'required'

SPECIAL_FIELD_ARGS = {
    'ForeignKey': {
        'to': REQUIRED,
        'on_delete': 'models.CASCADE',  # This is typically the required argument
    },
    'CharField': {
        'max_length': REQUIRED,  # Indicate that max_length is required for CharFields
    },
    # Add other fields that need special handling here.
}

def get_field_options(field_class):
    field_name = field_class.__name__
    if field_name in SPECIAL_FIELD_ARGS:
        return SPECIAL_FIELD_ARGS[field_name]

    # Attempt to instantiate the field to get default arguments
    # This may not be comprehensive for all field types and does not account for inherited defaults
    try:
        field_instance = field_class()
        name, path, args, kwargs = field_instance.deconstruct()
        return kwargs
    except TypeError:
        # Handle cases where instantiation fails
        return {arg: REQUIRED for arg in inspect.getfullargspec(field_class.__init__).args if arg != 'self'}

def get_all_model_fields():
    model_field_classes = {}
    for field_name in dir(models):
        field_class = getattr(models, field_name)
        if isinstance(field_class, type) and issubclass(field_class, models.Field):
            field_options = get_field_options(field_class)
            model_field_classes[field_name] = field_options
    return model_field_classes


def convert_bools_for_js(value):
    if isinstance(value, bool):
        return str(value).lower()
    return value

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