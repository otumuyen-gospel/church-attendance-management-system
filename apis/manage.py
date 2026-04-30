import os
import sys

# Use non-interactive Matplotlib backend so GUI code does not require a display.
os.environ.setdefault("MPLBACKEND", "Agg")

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apis.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
