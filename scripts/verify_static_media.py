#!/usr/bin/env python
"""
Verification script for static and media file configuration.

Run this to verify that Django's static/media settings are configured correctly.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

django.setup()

from django.conf import settings
from django.templatetags.static import static
from django.core.files.storage import default_storage


def main():
    print("=" * 60)
    print("Static & Media Configuration Verification")
    print("=" * 60)

    errors = []
    warnings = []

    print("\n1. Checking URL configurations...")
    if settings.STATIC_URL == '/static/':
        print(f"   ✓ STATIC_URL = '{settings.STATIC_URL}'")
    else:
        errors.append(f"STATIC_URL should be '/static/', got '{settings.STATIC_URL}'")

    if settings.MEDIA_URL == '/media/':
        print(f"   ✓ MEDIA_URL = '{settings.MEDIA_URL}'")
    else:
        errors.append(f"MEDIA_URL should be '/media/', got '{settings.MEDIA_URL}'")

    if '/static/static/' in [settings.STATIC_URL, settings.MEDIA_URL]:
        errors.append("Found nested /static/static/ URL pattern")
    if '/static/media/' in [settings.STATIC_URL, settings.MEDIA_URL]:
        errors.append("Found nested /static/media/ URL pattern")

    print("\n2. Checking root directory configurations...")
    if settings.STATIC_ROOT == '/vol/web/static':
        print(f"   ✓ STATIC_ROOT = '{settings.STATIC_ROOT}'")
    else:
        warnings.append(f"STATIC_ROOT is '{settings.STATIC_ROOT}' (expected '/vol/web/static')")

    if settings.MEDIA_ROOT == '/vol/web/media':
        print(f"   ✓ MEDIA_ROOT = '{settings.MEDIA_ROOT}'")
    else:
        warnings.append(f"MEDIA_ROOT is '{settings.MEDIA_ROOT}' (expected '/vol/web/media')")

    print("\n3. Checking URL helpers...")
    static_url = static('admin/css/base.css')
    if static_url.startswith('/static/'):
        print(f"   ✓ static('admin/css/base.css') = '{static_url}'")
    else:
        errors.append(f"static() helper generated unexpected URL: {static_url}")

    media_url = default_storage.url('test-file.txt')
    if media_url.startswith('/media/'):
        print(f"   ✓ default_storage.url('test-file.txt') = '{media_url}'")
    else:
        errors.append(f"default_storage.url() generated unexpected URL: {media_url}")

    print("\n4. Checking directory structure...")
    static_root_parent = os.path.dirname(settings.STATIC_ROOT)
    media_root_parent = os.path.dirname(settings.MEDIA_ROOT)
    if static_root_parent == media_root_parent:
        print(f"   ✓ STATIC_ROOT and MEDIA_ROOT share parent directory: {static_root_parent}")
    else:
        warnings.append("STATIC_ROOT and MEDIA_ROOT have different parent directories")

    print("\n" + "=" * 60)
    if errors:
        print("❌ FAIL - Found errors:")
        for err in errors:
            print(f"   - {err}")
        return 1
    else:
        print("✅ PASS - All critical checks passed!")
        if warnings:
            print("\n⚠️  Warnings:")
            for warn in warnings:
                print(f"   - {warn}")
        return 0


if __name__ == '__main__':
    sys.exit(main())
