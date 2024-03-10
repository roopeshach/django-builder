from django.core.management.base import BaseCommand, CommandError
import subprocess
import os
import json
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates a new Flutter project based on the project name in the JSON schema'

    def handle(self, *args, **kwargs):
        try:
            # Define the path to the schema directory (assumed to be next to manage.py)
            base_dir = settings.BASE_DIR
            schema_dir = os.path.join(base_dir, 'schema')

            # Check if the schema directory exists
            if not os.path.exists(schema_dir):
                raise CommandError('Schema directory does not exist')

            # Assuming there's only one schema file, or you can specify which one to read
            schema_files = [f for f in os.listdir(schema_dir) if f.endswith('.json')]
            if not schema_files:
                raise CommandError('No schema files found in the schema directory')

            # Read the first schema file
            with open(os.path.join(schema_dir, schema_files[0]), 'r') as schema_file:
                schema = json.load(schema_file)
                project_name = str(schema.get('projectName')).lower()


                if not project_name:
                    raise CommandError('Project name not found in the schema')

            # Define the path where the Flutter project will be created
            project_path = os.path.join(base_dir, project_name)

            # Check if the directory already exists
            if os.path.exists(project_path):
                raise CommandError(f'Project "{project_name}" already exists')

            # Run the Flutter create command
            subprocess.run(['flutter', 'create', project_name], check=True, cwd=base_dir)

            # Generate Flutter models based on the JSON schema
            self.generate_flutter_models(schema, project_path)

            self.stdout.write(self.style.SUCCESS(f'Successfully created Flutter project "{project_name}" based on the schema'))
        except json.JSONDecodeError:
            raise CommandError('Invalid JSON format in the schema file')
        except subprocess.CalledProcessError as e:
            raise CommandError(f'An error occurred while creating the Flutter project: {e}')
        except Exception as e:
            raise CommandError(f'An error occurred: {str(e)}')

    
    def generate_flutter_models(self, schema, flutter_project_path):
        models_dir = os.path.join(flutter_project_path, 'lib', 'models')
        os.makedirs(models_dir, exist_ok=True)

        for app in schema.get('apps', []):
            for model in app.get('models', []):
                model_name = model.get('modelName')
                fields = model.get('fields', [])
                self.create_dart_model_file(model_name, fields, models_dir)

    def create_dart_model_file(self, model_name, fields, models_dir):
        model_content = f'class {model_name} {{\n'
        # Fields
        for field in fields:
            dart_type = self.get_dart_type(field['fieldType'], field.get('attributes', {}))
            model_content += f'  final {dart_type} {field["fieldName"]};\n'

        # Constructor
        model_content += f'\n  {model_name}({{\n'
        for field in fields:
            model_content += f'    required this.{field["fieldName"]},\n'
        model_content += '  });\n'

        # toJson Method
        model_content += '\n  Map<String, dynamic> toJson() => {\n'
        for field in fields:
            model_content += f'        "{field["fieldName"]}": {field["fieldName"]},\n'
        model_content += '  };\n'

        # fromJson Method
        model_content += f'\n  factory {model_name}.fromJson(Map<String, dynamic> json) => {model_name}(\n'
        for field in fields:
            dart_type = self.get_dart_type(field['fieldType'], field.get('attributes', {}))
            model_content += f'        {field["fieldName"]}: json["{field["fieldName"]}"] as {dart_type},\n'
        model_content += '  );\n'

        model_content += '}\n'

        file_path = os.path.join(models_dir, f'{model_name.lower()}.dart')
        with open(file_path, 'w') as file:
            file.write(model_content)

    def get_dart_type(self, django_field_type, field_attributes):
        # Basic field type mapping
        mapping = {
            'CharField': 'String',
            'TextField': 'String',
            'FloatField': 'double',
            'IntegerField': 'int',
            'BooleanField': 'bool',
            'DateTimeField': 'DateTime',
            # Add other basic field mappings as needed
        }

        if django_field_type in mapping:
            return mapping[django_field_type]

        # Handling relational fields
        if django_field_type in ['ForeignKey', 'OneToOneField']:
            # Assuming the related model class name is the Dart type
            return field_attributes.get('to', 'dynamic').split('.')[-1]

        if django_field_type == 'ManyToManyField':
            # For ManyToMany, use List of related model class
            related_model = field_attributes.get('to', 'dynamic').split('.')[-1]
            return f'List<{related_model}>'

        return 'dynamic'