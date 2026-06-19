<div align="center">
    <a href="https://londonappdeveloper.com" target="_blank">
        <img src="https://londonappdeveloper.com/wp-content/uploads/2024/11/banner.svg" alt="Banner image" />
    </a>
</div>

<div align="center">
    <p>Full-Stack Consulting and Courses.</p>
    <a href="https://londonappdeveloper.com" target="_blank">Website</a> |
    <a href="https://londonappdeveloper.teachable.com/" target="_blank">Courses</a> |
    <a href="https://londonappdeveloper.com/tutorials/" target="_blank">Tutorials</a> |
    <a href="https://londonappdeveloper.com/consulting/" target="_blank">Consulting
</div>

<br /><br >

# Deploying Django with Docker Compose

This is the finished source code for the tutorial [Deploying Django with Docker Compose](https://londonappdeveloper.com/deploying-django-with-docker-compose/).

In this tutorial, we teach you how to prepare and deploying a Django project to an AWS EC2 instance using Docker Compose.

## Static & Media Files

This project uses the following URL conventions:

- **Static files**: `/static/` (served by Nginx in production, Django in dev)
- **Media files** (user uploads): `/media/` (served by Nginx in production, Django in dev)

### File Structure

Both static and media files are stored under `/vol/web/` inside the containers:
- Static files: `/vol/web/static/`
- Media files: `/vol/web/media/`

### Verifying Configuration

Two verification entry points are provided. Both work inside Docker and on local machines (no PostgreSQL required).

---

#### Quick Check: Run Django Test Suite

**What it verifies**: 12 unit tests covering URL configuration, path settings, URL helpers, staticfiles discovery, and debug-mode routing.

**Local machine** (recommended for fast validation):
```bash
python scripts/run_tests.py
```

**Inside Docker container**:
```bash
docker-compose run --rm app sh -c "python manage.py test core.tests"
```

**Expected output**:
```
Ran 12 tests in ...s

OK
```

---

#### Detailed Report: Run Verification Script

**What it verifies**: 10 detailed checks across 6 categories with human-readable output, including actual generated URLs and discovered file paths.

**Local machine**:
```bash
python scripts/verify_static_media.py
```

**Inside Docker container**:
```bash
docker-compose run --rm app sh -c "python /scripts/verify_static_media.py"
```

**Expected output** (all 10 checks pass):
```
============================================================
Static & Media Configuration Verification
============================================================

[1/6] Checking URL configurations...
  [PASS] STATIC_URL = '/static/'
  [PASS] MEDIA_URL = '/media/'

[2/6] Checking root directory configurations...
  [PASS] STATIC_ROOT = '/vol/web/static'
  [PASS] MEDIA_ROOT = '/vol/web/media'

[3/6] Checking URL helpers...
  [PASS] static('admin/css/base.css') = '/static/admin/css/base.css'
  [PASS] default_storage.url('test-file.txt') = '/media/test-file.txt'

[4/6] Checking directory structure...
  [PASS] STATIC_ROOT and MEDIA_ROOT share parent directory: /vol/web

[5/6] Checking staticfiles discovery...
  [PASS] admin/css/base.css found via staticfiles finders
         Path: ...

[6/6] Checking debug mode URL routing...
  [PASS] DEBUG mode MEDIA route regex = '^media/(?P<path>.*)$'
  [PASS] DEBUG mode STATIC route regex = '^static/(?P<path>.*)$'

============================================================
Results: 10 passed, 0 failed

All critical checks passed.
```

---

### Development

In development mode (`DEBUG=1`):
- Django serves static files via the `staticfiles` app at `/static/`
- Django serves media files via the URL pattern in `urls.py` at `/media/`
- Media files are stored in `./data/web/media/` on your local machine
- Static files are collected to `./data/web/static/` (for reference only)

### Production

In production (deployed via `docker-compose-deploy.yml`):
- Nginx serves static files directly from the shared volume at `/static/`
- Nginx serves media files directly from the shared volume at `/media/`
- Django (via uWSGI) handles all dynamic requests
