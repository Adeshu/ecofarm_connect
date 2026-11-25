# EcoFarm Connect — Gamified Sustainable Farming Platform

A Django web application that teaches sustainable farming through quests, farm tracking, courses, badges and a leaderboard. It includes a chatbot and a REST API for future mobile clients.

## Features

- Custom user model with registration, login and public profiles.
- Quest system with categories, difficulty levels and step-by-step instructions.
- Farm and crop management with activity logging and statistics.
- Gamification: points, levels, badges, achievements and a global leaderboard.
- Course catalogue with lessons, enrolment, progress and certificates.
- Dashboard with activity feeds and progress summaries.
- Public farm directory and achievement showcase.
- Chatbot endpoint and REST API.
- Django admin for all core models.

## Tech stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 |
| Database | MySQL (`mysqlclient`) |
| UI | Django templates, Bootstrap 4, crispy forms |
| API | Django REST Framework, django-filter, CORS headers |
| Background jobs | Celery + Redis |
| Static files | WhiteNoise |
| Reports | ReportLab, openpyxl |
| Config | python-decouple + python-dotenv |

## Django apps

| App | Responsibility |
|---|---|
| `accounts` | Users, authentication, profiles |
| `quests` | Quest catalogue and completion |
| `farms` | Farms, crops, activities, public directory |
| `gamification` | Points, badges, achievements, leaderboard |
| `courses` | Courses, lessons, enrolment, certificates |
| `core` | Dashboard and shared views |
| `api` | REST endpoints |
| `chatbot` | Chatbot integration |

## Project structure

```text
ecofarm-connect/
├── manage.py
├── requirements.txt
├── .env.example
├── sustainable_farming_web/     # Settings, URLs, WSGI/ASGI
├── accounts/  quests/  farms/  gamification/  courses/  core/  api/  chatbot/
├── templates/                   # Shared templates
├── static/                      # Source static assets
├── fixtures/                    # Sample data
├── create_sample_data_extended.py
└── setup.sh
```

## Prerequisites

- Python 3.10+
- MySQL 8+
- Redis (optional, for Celery and caching)

## Setup

1. Create the database:

   ```sql
   CREATE DATABASE sustainable_db CHARACTER SET utf8mb4;
   ```

2. Install dependencies:

   ```powershell
   python -m venv venv
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Configure the environment:

   ```powershell
   Copy-Item .env.example .env
   ```

   Set `SECRET_KEY` and the MySQL credentials. Never commit `.env`.

4. Migrate and create an admin account:

   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   .\venv\Scripts\python.exe manage.py createsuperuser
   ```

5. Load sample data (optional):

   ```powershell
   .\venv\Scripts\python.exe manage.py loaddata fixtures/sample_courses.json
   .\venv\Scripts\python.exe manage.py shell
   ```

   Then run `create_sample_data_extended.py` inside the shell if you want a fuller demo dataset.

6. Start the server:

   ```powershell
   .\venv\Scripts\python.exe manage.py runserver
   ```

Open <http://127.0.0.1:8000/>.

## Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode |
| `ALLOWED_HOSTS` | Comma-separated host names |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection |
| `EMAIL_*` | Outgoing email configuration |
| `REDIS_URL` | Redis / Celery broker |
| `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `GENERATIVE_AI_KEY` | Optional AI/chatbot keys |

## Performance and scale notes

- Quest, farm and gamification queries are ordinary Django ORM queries; indexes exist on the main foreign keys.
- Redis and Celery are optional for local development and can be enabled in production for background tasks.
- Use MySQL in production; the project is already configured for it.
- Run `manage.py collectstatic` before deploying behind WhiteNoise.

## Security notes

- `.env`, `venv/`, `staticfiles/`, `media/`, `logs/` and `*.sql` dumps are git-ignored.
- Database credentials have no hard-coded fallback in source control.
- The historical SQL dump that contained demo user data has been removed from the repository.
- Set `DEBUG=False` and a strong `SECRET_KEY` in production.

## Licence

Educational project.
