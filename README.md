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

Two layers of verification are provided to ensure the static/media setup is correct:

#### 1. Run Django Tests

This verifies settings, URL helpers, staticfiles discovery, and debug mode routing:

```bash
docker-compose run --rm app sh -c "python manage.py test core.tests"
```

You should see output similar to:
```
Ran 11 tests in ...s

OK
```

#### 2. Run Dedicated Verification Script

This provides a detailed, human-readable report of all checks:

```bash
docker-compose run --rm app sh -c "python /scripts/verify_static_media.py"
```

You should see all checks marked `[PASS]` with a final summary showing `All critical checks passed.`

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
