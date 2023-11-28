#!/bin/bash

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    # Install pip (use the appropriate method for any system)
fi

# Check if Jazzmin is installed
if ! pip freeze | grep -q 'django-jazzmin'; then
    echo "Jazzmin is not installed. Installing Jazzmin..."
    pip install django-jazzmin
fi

# Step 1: Run the Django management command to generate models from schema
echo "Generating models from schema..."
python manage.py generate_models_from_schema

# Step 2: Find and call wsgi.py to restart the Django server
echo "Restarting Django server..."
wsgi_file=$(find . -name "wsgi.py")
if [ -z "$wsgi_file" ]; then
    echo "wsgi.py file not found."
else
    echo "Calling $wsgi_file to restart the server..."
    touch "$wsgi_file"
fi

# Step 3: Give Django some time to start up
sleep 2

# Step 4: Run migrations
echo "Running migrations..."
python manage.py makemigrations Authentication
python manage.py makemigrations
python manage.py migrate

# Step 5: Create a superuser
echo "Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@email.com', 'pass')" | python manage.py shell

echo "Process completed."
