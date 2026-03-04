# Capstone News

Capstone News is a Django-based news platform with role-based access control, article approval workflow, reader subscriptions, email notifications, and REST API support using Django REST Framework (DRF).

## Features

- Custom user roles: Reader, Journalist, and Editor
- Journalist article submission workflow
- Editor approval queue for pending articles
- Journalist article editing with re-approval after changes
- Reader subscriptions to journalists and publishers
- Email notifications to subscribers when an article is approved
- REST API with JWT authentication
- Automated tests
- MariaDB database support
- Environment-variable based configuration

---

## Tech Stack

- Python
- Django
- Django REST Framework
- MariaDB
- Bootstrap 5
- PyMySQL
- SimpleJWT

---

## Project Structure

```text
capstone_news/
│
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── signals.py
│   ├── admin.py
│   └── migrations/
│
├── news/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   └── templates/news/
│
├── api/
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── urls.py
│   └── tests/
│
├── templates/
│   ├── base.html
│   └── registration/
│       ├── login.html
│       └── register.html
│
└── static/
    └── ...
```

---

## Setup Instructions

These instructions are written for Windows PowerShell.

### 1. Clone the repository

```powershell
git clone https://github.com/SergioZanela/capstone_news.git
cd capstone_news
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

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

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and update the values for your local environment.

Example:

```env
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=capstone_news
DB_USER=root
DB_PASSWORD=your_mariadb_password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@capstonenews.local
```

### 5. Create the MariaDB database

Open MariaDB:

```powershell
mariadb -u root -p
```

Then run:

```sql
CREATE DATABASE capstone_news CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

If `mariadb` is not available in PowerShell, use the full path to your MariaDB client executable.

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

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

---

## Environment Variables

The project loads configuration from `.env`.

Required values:

```env
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=capstone_news
DB_USER=root
DB_PASSWORD=your_mariadb_password
DB_HOST=127.0.0.1
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@capstonenews.local
```

`.env.example` is included as a template.
Create your local `.env` by copying `.env.example` and replacing the placeholder values with your own configuration.

---

## User Roles

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

### Editor
- Can review pending articles in the approval queue
- Can approve or reject articles
- Can create and manage publishers

---

## Publisher Management

Publishers are managed through the editor interface in the main application.

Editor workflow:
1. Log in as an Editor
2. Open the **Publishers** page from the navigation bar
3. Click **Add Publisher**
4. Create the publisher
5. Journalists can then assign that publisher to articles

---

## Article Workflow

### Journalist workflow
1. Log in as a Journalist
2. Open **Submit Article**
3. Create a new article
4. The article is saved as pending
5. Open **My Articles** to view submitted articles
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

## Authentication and Registration

- The project uses Django authentication for the web interface
- Login and logout use Django's built-in auth views
- Registration uses the custom user registration form
- Public self-registration supports Reader and Journalist accounts
- Editor accounts should be created through administration

---

## Email Notifications

When an editor approves an article, the application sends an email notification to readers who are subscribed to:
- the article's publisher
- and/or the article's journalist

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

## Suggested Test Flow

1. Clone the repository
2. Create and activate the virtual environment
3. Install dependencies
4. Copy `.env.example` to `.env`
5. Update `.env` with valid MariaDB credentials
6. Create the MariaDB database
7. Run migrations
8. Create a superuser
9. Start the server
10. Log in to the application or admin area

Suggested functional test flow:
1. Create an Editor account
2. Create a Journalist account
3. Create a Reader account
4. Log in as an Editor and create one or more publishers
5. Log in as a Journalist and submit an article
6. Edit the article if required
7. Log in as an Editor and approve the article
8. Log in as a Reader and test subscriptions
9. Verify article approval email behaviour

---

## Running Tests

Run all tests:

```powershell
python manage.py test
```

Run article API tests:

```powershell
python manage.py test api.tests.test_article_api
```

Run email notification tests:

```powershell
python manage.py test news.tests.test_email_notifications
```

---
