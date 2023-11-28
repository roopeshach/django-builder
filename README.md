# DJANGO- BUILDER


## Table of Contents

- [Features](#features)
- [Process](#process)

## Features

Listed below are the key features of this project:

- **Save Model Schema:** This feature allows users to save the schema of Django models used in their project. The schema is saved in JSON format, and a separate schema file is created for each app in the project.

- **Support for Multiple Apps:** The system supports multiple Django apps, and it saves the schema for each app separately. Apps are identified by their names, and the schema files are named accordingly.

- **Schema Directory:** The schema files are saved in a directory named "schema" at the project level, next to the "manage.py" file. The directory is automatically created if it doesn't exist.

- **JSON Format:** The schema is saved in a well-structured JSON format, making it easy to read and manage.

- **Error Handling:** The system includes error handling to deal with cases of invalid JSON format or other exceptions. It provides appropriate error messages for better user experience.

- **CSRF Exempt:** The "save_model_schema" endpoint is CSRF exempt, making it easier to use in various contexts.

- **Model Field Information:** The project includes functionality to retrieve information about Django model fields, including special handling for ForeignKey and CharField.

- **JavaScript Compatibility:** Booleans in the schema are converted to JavaScript-compatible boolean values, ensuring smooth integration with JavaScript-based frontends.

- **Model Schema Form:** The project provides a view that renders a form for generating the model schema. Users can easily select fields and options for their models.

- **Model Selection:** The form includes a list of all available Django models, allowing users to choose which models they want to include in the schema.

## Process

The process of using this project involves the following steps:

1. Make a POST request to the "/save_model_schema" endpoint with a JSON payload containing the schemas of your Django apps' models.

2. The project will create separate JSON files for each app's schema in a "schema" directory located at the project level.

3. The schema files can be used for documentation, data migration, or any other purposes related to your Django project.

4. Error handling is in place to handle cases of invalid JSON format or other exceptions.

5. The project also provides a view for generating the model schema interactively. Users can select fields and options for their models.

6. Users can select which Django models they want to include in the schema using the provided form.

7. Booleans in the schema are converted to JavaScript-compatible boolean values for seamless integration with JavaScript-based frontends.

This README.md file provides an overview of the features and the process of using this project.
