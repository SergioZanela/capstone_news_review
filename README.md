# Capstone News

Capstone News is a Django-based news platform with role-based access control, article approval workflow, reader subscriptions, email notifications, and REST API support using Django REST Framework (DRF).

This repository is the clean review submission for the final Django News Application capstone project. It includes the application source code, Sphinx-generated documentation, Docker support, and reviewer-friendly setup instructions.

## What was added for this task

This submission was updated to satisfy the documentation and containerisation assessment requirements:

- Added and reviewed `.gitignore` to exclude local-only and sensitive files.
- Kept `.env` private and provided `.env.example` for setup guidance.
- Added concise module, class, and method docstrings in selected project files.
- Generated Sphinx documentation and stored it in the `docs/` folder.
- Added a `Dockerfile` to run the project in a container.
- Added a `.dockerignore` file to keep Docker builds clean.
- Updated setup instructions for both local virtual environment use and Docker use.
- Confirmed the project works locally and can also run in Docker with the correct database host settings.

---

## Features

- Custom user roles: Reader, Journalist, and Editor
- Journalist article submission workflow
- Journalist article editing with re-approval after changes
- Journalist **My Articles** page
- Editor approval queue for pending articles
- Editor publisher management from the main application UI
- Reader subscriptions to journalists and publishers
- Email notifications to subscribers when an article is approved
- REST API with JWT authentication
- Automated tests
- MariaDB database support
- Environment-variable based configuration

---

## Tech Stack

- Python 3.13
- Django
- Django REST Framework
- MariaDB
- PyMySQL
- SimpleJWT
- Sphinx
- Docker
- Bootstrap 5

---

## Project Structure

```text
capstone_news_review/
│
├── manage.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
│
├── config/
├── accounts/
├── news/
├── api/
├── core/
├── integrations/
├── templates/
├── static/
└── docs/
    ├── source/
    └── build/html/
```

---

## Branches used for this task

The assessment work was organised using separate branches before being merged into `main`:

- `docs` - docstrings, Sphinx setup, generated documentation
- `container` - Docker configuration
- `main` - final merged submission branch

---

## Environment variables

This project loads settings from a `.env` file (not committed to Git).

Two example templates are provided:

- **Local / non-Docker:** copy `.env.example` → `.env`
- **Docker:** copy `.env.docker.example` → `.env.docker`

> Note (Docker Desktop on Windows/macOS): when the database runs on your host machine, Docker typically needs `DB_HOST=host.docker.internal` instead of `127.0.0.1`.

---

## Local setup with virtual environment (Windows PowerShell)

### 1. Clone the repository

```powershell
git clone https://github.com/SergioZanela/capstone_news_review.git
cd capstone_news_review
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the environment file

```powershell
Copy-Item .env.example .env
```

> Edit `.env` and set your own values (DB credentials, secret key, etc.).

### 5. Create the MariaDB database

```powershell
mariadb -u root -p
CREATE DATABASE capstone_news CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 6. Apply migrations

```powershell
python manage.py migrate
```

### 7. Create a superuser

```powershell
python manage.py createsuperuser
```

### 8. Run the development server

```powershell
python manage.py runserver
```

### 9. Open:

```text
`http://127.0.0.1:8000/`
```

### Docker setup

### 1. Create the Docker environment file

```powershell
Copy-Item .env.docker.example .env.docker
```

> Edit `.env.docker` and set your own values.

### 2. Build the Docker image

```powershell
docker build -t capstone-news-app .
```

### 3. Run the container

```powershell
docker run --env-file .env.docker -p 8000:8000 capstone-news-app
```

### Open:

```text
`http://localhost:8000/`
```

---

## User roles

### Reader
- Can register through the application
- Can view approved articles
- Can subscribe to journalists
- Can subscribe to publishers

### Journalist
- Can register through the application
- Can submit new articles
- Can view their own articles
- Can edit their own articles
- Edited articles are returned to pending approval
- Can manage articles through the **My Articles** page

### Editor
- Can review pending articles in the approval queue
- Can approve or reject articles
- Can create publishers from the main application UI
- Can manage the visible publisher workflow used by journalists

---

## Publisher workflow

Publishers are managed through the main application interface.

1. Log in as an Editor
2. Open the **Publishers** page from the navigation bar
3. Click **Add Publisher**
4. Create the publisher
5. Journalists can then assign that publisher when creating or editing articles

---

## Article workflow

### Journalist workflow
1. Log in as a Journalist
2. Open **Submit Article**
3. Create a new article
4. The article is saved as pending
5. Open **My Articles** to review existing submissions
6. Edit the article if needed
7. After editing, the article returns to pending approval

### Editor workflow
1. Log in as an Editor
2. Open **Approval Queue**
3. Review pending articles
4. Approve or reject the article

### Reader workflow
1. Log in as a Reader
2. Open any approved article
3. Subscribe to the journalist and/or publisher from the article page

---

## Authentication and registration

- The web interface uses Django authentication.
- Login and logout use Django's built-in auth views.
- Registration uses the custom user registration form.
- Public self-registration supports Reader and Journalist accounts.
- Editor accounts should be created through administration.

---

## Email notifications

When an editor approves an article, the application sends email notifications to readers subscribed to:

- the article's publisher
- the article's journalist

For local development, the console email backend can be used through `.env`.

---

## REST API

The project exposes REST endpoints so users can interact with articles, subscriptions, publishers, and newsletters using JSON.

### Authentication

- Session authentication
- JWT authentication with SimpleJWT

Token endpoints:

```text
POST /api/token/
POST /api/token/refresh/
```

### Main API endpoints

#### Articles
```text
GET    /api/articles/
POST   /api/articles/
GET    /api/articles/<id>/
PUT    /api/articles/<id>/
PATCH  /api/articles/<id>/
DELETE /api/articles/<id>/
```

#### Subscribed articles
```text
GET /api/articles/subscribed/
```

#### Editor approval
```text
GET  /api/articles/pending/
POST /api/articles/<id>/approve/
POST /api/articles/<id>/reject/
```

#### Publishers
```text
GET /api/publishers/
GET /api/publishers/<id>/
```

#### Publisher subscriptions
```text
GET    /api/publisher-subscriptions/
POST   /api/publisher-subscriptions/
DELETE /api/publisher-subscriptions/<id>/
```

#### Journalist subscriptions
```text
GET    /api/journalist-subscriptions/
POST   /api/journalist-subscriptions/
DELETE /api/journalist-subscriptions/<id>/
```

#### Newsletters
```text
GET               /api/newsletters/
POST              /api/newsletters/
GET               /api/newsletters/<id>/
PUT/PATCH/DELETE  /api/newsletters/<id>/manage/
```

#### Publisher memberships
```text
GET /api/publisher-memberships/
GET /api/publisher-memberships/<id>/
```

---

## Documentation

Sphinx documentation is included in the `docs/` folder.

Generated HTML output is available in:

```text
docs/build/html/index.html
```

This documentation was generated from the project source code and selected docstrings added for the assessment task.

---

## Running tests

### Run all tests:

```powershell
python manage.py test
```

### Run article API tests:

```powershell
python manage.py test api.tests.test_article_api
```

### Run email notification tests:

```powershell
python manage.py test news.tests.test_email_notifications
```

---
