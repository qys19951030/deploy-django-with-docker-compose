#!/usr/bin/env python
"""
Verification script for static and media file configuration.

Run this to verify that Django's static/media settings are configured correctly.
This script uses only ASCII characters for terminal compatibility.

It can run both inside Docker container and on local development machines,
without requiring PostgreSQL or any other database to be available.
"""
import os
import sys
import ast


def extract_settings_values():
    """Extract static/media related values from settings.py without loading Django."""
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
                    if target.id in ['STATIC_URL', 'MEDIA_URL', 'STATIC_ROOT', 'MEDIA_ROOT', 'DEBUG', 'SECRET_KEY', 'INSTALLED_APPS']:
                        try:
                            values[target.id] = ast.literal_eval(node.value)
                        except (ValueError, SyntaxError):
                            if target.id == 'SECRET_KEY':
                                values[target.id] = 'fallback-secret-key-for-verification'
                            elif target.id == 'DEBUG':
                                values[target.id] = True

    return values


def configure_django(settings_values):
    """Configure Django with minimal required settings."""
    import django
    from django.conf import settings as django_settings

    if not django_settings.configured:
        django_settings.configure(
            DEBUG=settings_values.get('DEBUG', True),
            SECRET_KEY=settings_values.get('SECRET_KEY', 'test-secret-key'),
            INSTALLED_APPS=[
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.staticfiles',
            ],
            STATIC_URL=settings_values.get('STATIC_URL', '/static/'),
            MEDIA_URL=settings_values.get('MEDIA_URL', '/media/'),
            STATIC_ROOT=settings_values.get('STATIC_ROOT', '/vol/web/static'),
            MEDIA_ROOT=settings_values.get('MEDIA_ROOT', '/vol/web/media'),
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
        )
    django.setup()
    return django_settings


def print_separator():
    print("=" * 60)


def main():
    print_separator()
    print("Static & Media Configuration Verification")
    print_separator()

    try:
        settings_values = extract_settings_values()
        settings = configure_django(settings_values)
    except Exception as e:
        print("ERROR: Failed to load configuration: %s" % str(e))
        import traceback
        traceback.print_exc()
        return 1

    errors = []
    warnings = []
    passed = 0
    failed = 0

    print("\n[1/6] Checking URL configurations...")
    if settings.STATIC_URL == '/static/':
        print("  [PASS] STATIC_URL = '%s'" % settings.STATIC_URL)
        passed += 1
    else:
        print("  [FAIL] STATIC_URL should be '/static/', got '%s'" % settings.STATIC_URL)
        errors.append("STATIC_URL should be '/static/', got '%s'" % settings.STATIC_URL)
        failed += 1

    if settings.MEDIA_URL == '/media/':
        print("  [PASS] MEDIA_URL = '%s'" % settings.MEDIA_URL)
        passed += 1
    else:
        print("  [FAIL] MEDIA_URL should be '/media/', got '%s'" % settings.MEDIA_URL)
        errors.append("MEDIA_URL should be '/media/', got '%s'" % settings.MEDIA_URL)
        failed += 1

    if '/static/static/' in [settings.STATIC_URL, settings.MEDIA_URL]:
        errors.append("Found nested /static/static/ URL pattern")
        failed += 1
    if '/static/media/' in [settings.STATIC_URL, settings.MEDIA_URL]:
        errors.append("Found nested /static/media/ URL pattern")
        failed += 1

    print("\n[2/6] Checking root directory configurations...")
    if settings.STATIC_ROOT == '/vol/web/static':
        print("  [PASS] STATIC_ROOT = '%s'" % settings.STATIC_ROOT)
        passed += 1
    else:
        print("  [WARN] STATIC_ROOT is '%s' (expected '/vol/web/static')" % settings.STATIC_ROOT)
        warnings.append("STATIC_ROOT is '%s' (expected '/vol/web/static')" % settings.STATIC_ROOT)

    if settings.MEDIA_ROOT == '/vol/web/media':
        print("  [PASS] MEDIA_ROOT = '%s'" % settings.MEDIA_ROOT)
        passed += 1
    else:
        print("  [WARN] MEDIA_ROOT is '%s' (expected '/vol/web/media')" % settings.MEDIA_ROOT)
        warnings.append("MEDIA_ROOT is '%s' (expected '/vol/web/media')" % settings.MEDIA_ROOT)

    print("\n[3/6] Checking URL helpers...")
    from django.templatetags.static import static
    static_url = static('admin/css/base.css')
    expected_static_url = '/static/admin/css/base.css'
    if static_url == expected_static_url:
        print("  [PASS] static('admin/css/base.css') = '%s'" % static_url)
        passed += 1
    else:
        print("  [FAIL] static() helper generated unexpected URL")
        print("         Expected: '%s'" % expected_static_url)
        print("         Got:      '%s'" % static_url)
        errors.append("static() helper generated unexpected URL: '%s'" % static_url)
        failed += 1

    from django.core.files.storage import default_storage
    media_url = default_storage.url('test-file.txt')
    expected_media_url = '/media/test-file.txt'
    if media_url == expected_media_url:
        print("  [PASS] default_storage.url('test-file.txt') = '%s'" % media_url)
        passed += 1
    else:
        print("  [FAIL] default_storage.url() generated unexpected URL")
        print("         Expected: '%s'" % expected_media_url)
        print("         Got:      '%s'" % media_url)
        errors.append("default_storage.url() generated unexpected URL: '%s'" % media_url)
        failed += 1

    print("\n[4/6] Checking directory structure...")
    static_root_parent = os.path.dirname(settings.STATIC_ROOT)
    media_root_parent = os.path.dirname(settings.MEDIA_ROOT)
    if static_root_parent == media_root_parent:
        print("  [PASS] STATIC_ROOT and MEDIA_ROOT share parent directory: %s" % static_root_parent)
        passed += 1
    else:
        print("  [WARN] STATIC_ROOT and MEDIA_ROOT have different parent directories")
        warnings.append("STATIC_ROOT and MEDIA_ROOT have different parent directories")

    print("\n[5/6] Checking staticfiles discovery...")
    from django.contrib.staticfiles import finders
    found = finders.find('admin/css/base.css')
    if found is not None:
        print("  [PASS] admin/css/base.css found via staticfiles finders")
        print("         Path: %s" % found)
        passed += 1
    else:
        print("  [FAIL] admin/css/base.css not found via staticfiles finders")
        errors.append("admin/css/base.css not found via staticfiles finders")
        failed += 1

    print("\n[6/6] Checking debug mode URL routing...")
    from django.conf.urls.static import static as static_helper

    media_patterns = static_helper(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if len(media_patterns) == 1:
        regex_pattern = media_patterns[0].pattern.regex.pattern
        expected_regex = r'^media/(?P<path>.*)$'
        if regex_pattern == expected_regex:
            print("  [PASS] DEBUG mode MEDIA route regex = '%s'" % regex_pattern)
            passed += 1
        else:
            print("  [FAIL] DEBUG mode MEDIA route mismatch")
            print("         Expected: '%s'" % expected_regex)
            print("         Got:      '%s'" % regex_pattern)
            errors.append("DEBUG mode MEDIA route mismatch")
            failed += 1
    else:
        print("  [FAIL] Expected 1 MEDIA route, got %d" % len(media_patterns))
        errors.append("Expected 1 MEDIA route, got %d" % len(media_patterns))
        failed += 1

    static_patterns = static_helper(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if len(static_patterns) == 1:
        regex_pattern = static_patterns[0].pattern.regex.pattern
        expected_regex = r'^static/(?P<path>.*)$'
        if regex_pattern == expected_regex:
            print("  [PASS] DEBUG mode STATIC route regex = '%s'" % regex_pattern)
            passed += 1
        else:
            print("  [FAIL] DEBUG mode STATIC route mismatch")
            print("         Expected: '%s'" % expected_regex)
            print("         Got:      '%s'" % regex_pattern)
            errors.append("DEBUG mode STATIC route mismatch")
            failed += 1
    else:
        print("  [FAIL] Expected 1 STATIC route, got %d" % len(static_patterns))
        errors.append("Expected 1 STATIC route, got %d" % len(static_patterns))
        failed += 1

    print()
    print_separator()
    print("Results: %d passed, %d failed" % (passed, failed))
    if warnings:
        print("Warnings: %d" % len(warnings))

    if errors:
        print("\nERRORS:")
        for err in errors:
            print("  - %s" % err)
        return 1
    else:
        print("\nAll critical checks passed.")
        if warnings:
            print("\nWARNINGS:")
            for warn in warnings:
                print("  - %s" % warn)
        return 0


if __name__ == '__main__':
    sys.exit(main())
