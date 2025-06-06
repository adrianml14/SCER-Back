#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)

    # Iniciar scheduler solo cuando uses runserver
    if 'runserver' in sys.argv:
        try:
            from rally import scheduler
            scheduler.start()
        except Exception as e:
            print(f"❌ Error al iniciar el scheduler: {e}")

if __name__ == '__main__':
    main()
