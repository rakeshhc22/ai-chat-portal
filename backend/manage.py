#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This file should be placed in the backend directory and is usually auto-generated
by Django when you run 'django-admin startproject config'.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/ref/django-admin/
"""

import os
import sys


def main():
    """
    Run administrative tasks for Django project.
    
    This function:
    1. Sets the default Django settings module
    2. Executes Django management commands
    3. Handles command-line arguments
    """
    # Set the Django settings module to use from config package
    # This tells Django which settings.py file to load
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        # Import Django management utilities
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Execute the Django command passed through command-line arguments
    # Examples:
    # - python manage.py runserver
    # - python manage.py migrate
    # - python manage.py makemigrations
    # - python manage.py createsuperuser
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Run the main function when this script is executed
    main()
