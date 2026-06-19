#!/usr/bin/env python
"""
Test runner that works without PostgreSQL dependency.

This script configures Django with SQLite before running tests,
so it can run on any machine without requiring database setup.
"""
import os
import sys
import ast


def extract_settings_values():
    """Extract relevant values from settings.py without loading Django."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(script_dir, '..', 'app', 'app', 'settings.py')

    with open(settings_path, 'r') as f:
        content = f.read()

    tree = ast.parse(content)

    values = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id in ['STATIC_URL', 'MEDIA_URL', 'STATIC_ROOT', 'MEDIA_ROOT',
                                     'DEBUG', 'SECRET_KEY', 'INSTALLED_APPS']:
                        try:
                            values[target.id] = ast.literal_eval(node.value)
                        except (ValueError, SyntaxError):
                            if target.id == 'SECRET_KEY':
                                values[target.id] = 'test-secret-key-for-tests'
                            elif target.id == 'DEBUG':
                                values[target.id] = True

    return values


def configure_django(settings_values):
    """Configure Django with SQLite for testing."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'

    import django
    from django.conf import settings as django_settings

    if not django_settings.configured:
        django_settings.configure(
            DEBUG=True,
            SECRET_KEY=settings_values.get('SECRET_KEY', 'test-secret-key'),
            INSTALLED_APPS=[
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'core',
            ],
            STATIC_URL=settings_values.get('STATIC_URL', '/static/'),
            MEDIA_URL=settings_values.get('MEDIA_URL', '/media/'),
            STATIC_ROOT=settings_values.get('STATIC_ROOT', '/vol/web/static'),
            MEDIA_ROOT=settings_values.get('MEDIA_ROOT', '/vol/web/media'),
            ROOT_URLCONF='app.urls',
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ],
        )
    django.setup()


def main():
    settings_values = extract_settings_values()
    configure_django(settings_values)

    from django.test.utils import get_runner
    from django.conf import settings

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests(['core.tests'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    main()
