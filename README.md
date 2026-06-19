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

To verify the static/media configuration is correct:

```bash
# Run Django tests (includes static/media checks)
docker-compose run --rm app sh -c "python manage.py test"

# Run the dedicated verification script
docker-compose run --rm app sh -c "python /scripts/verify_static_media.py"
```

### Development

In development mode (`DEBUG=1`), Django serves both static and media files directly.
Media files are stored in `./data/web/media/` on your local machine.
