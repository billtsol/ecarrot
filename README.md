# ecarrot

Online Shop

## Django Documentation

This project uses Django, a high-level Python web framework, to build web applications. Django provides a command-line interface (CLI) that allows you to perform various tasks related to your Django project.

### Django Commands

Django commands are executed using the `manage.py` script located in the root directory of your Django project. Here are some of the basic Django commands you can use:

- `django-admin startproject myproject` : Creates a new Django project
- `python manage.py runserver`: Starts the development server and runs your Django application locally.
- `python manage.py migrate`: Applies any pending database migrations to keep your database schema up to date.
- `python manage.py createsuperuser`: Creates a superuser account that has administrative privileges in the Django admin interface.
- `python manage.py makemigrations`: Creates new database migration files based on the changes you made to your models.
- `python manage.py shell`: Opens an interactive Python shell with your Django project's environment loaded, allowing you to interact with your project's models and data.
- `python manage.py collectstatic`: Collects all static files from your Django project and copies them to a single location for deployment.

## Docker Compose Documentation

- `docker-compose up`: Builds, (re)creates, starts, and attaches to containers for a service
- `docker-compose down`: Stops and removes containers, networks, and volumes created by `up`
- `docker-compose build`: Builds or rebuilds services.
- `docker-compose run --rm app sh -c "python manage.py test"`: One-off command on a service defined in your docker-compose.yml. `app` is the name of the service defined in your docker-compose.yml file.
