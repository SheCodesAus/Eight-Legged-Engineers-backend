# PlayPal Backend

> Eight Legged Engineers

Django REST API backend for PlayPal — a platform for parents to discover, save, and rate kid-friendly venues and activities across NSW.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Common Django Commands](#common-django-commands)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Deployment](#deployment-heroku)

---

## Tech Stack

- Python 3.12
- Django 5.1
- Django REST Framework
- PostgreSQL (production) / SQLite (local dev)
- Supabase (authentication)
- Heroku (deployment)

---

## Prerequisites

### Install Python

**Windows:**
1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. During installation, check **Add Python to PATH**
3. Verify in PowerShell:
```powershell
python --version
```

**Mac:**
1. Install Homebrew if not already installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
2. Install Python:
```bash
brew install python@3.12
```
3. Verify:
```bash
python3 --version
```

> On Mac, use `python3` and `pip3` in place of `python` and `pip` for all commands below.

### Install Django

Once your virtual environment is activated (see Local Setup below), Django is installed via `requirements.txt`. To install it manually:

**Windows:**
```powershell
pip install django
```

**Mac:**
```bash
pip3 install django
```

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/SheCodesAus/Eight-Legged-Engineers-backend.git
cd Eight-Legged-Engineers-backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows (PowerShell):**
```powershell
& venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Create a `.env` file in the root of the repo with the following variables:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_JWT_PUBLIC_KEY=your-supabase-jwt-public-key
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 5. Run migrations

```bash
cd playpal
python manage.py migrate
```

### 6. Import data

```bash
python manage.py import_venues data/NSW_Kids_Activities_Eateries.csv
python manage.py import_suburbs data/suburbs.csv
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

---

## Common Django Commands

| Command | Description |
|---------|-------------|
| `python manage.py runserver` | Start the local dev server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py makemigrations` | Generate migrations from model changes |
| `python manage.py createsuperuser` | Create an admin superuser |
| `python manage.py shell` | Open the Django interactive shell |
| `python manage.py dbshell` | Open the database shell (PostgreSQL) |
| `python manage.py check` | Check the project for errors |

---

## Authentication

All protected endpoints require a Supabase JWT passed as a Bearer token:

```
Authorization: Bearer <supabase_access_token>
Content-Type: application/json
```

On first login, a Django user is automatically created and linked to the Supabase account via `supabase_uid`. No separate registration is required.

---

## API Endpoints

Base URL:
- **Local:** `http://127.0.0.1:8000/api/`
- **Production:** `https://play-pal.herokuapp.com/api/`

---

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/users/` | Required (staff) | List all users |
| `GET` | `/api/users/me/` | Required | Get own profile including kids |
| `PATCH` | `/api/users/me/` | Required | Update own profile |
| `GET` | `/api/users/<id>/` | Required | Get a user by ID |
| `POST` | `/api/auth/webhook/` | None | Supabase auth webhook (internal) |
| `POST` | `/api/auth/logout/` | Required | Logout and invalidate Supabase session |

---

### Kids

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/kids/` | Required | List own kids |
| `POST` | `/api/kids/` | Required | Add a kid |
| `PATCH` | `/api/kids/<id>/` | Required | Update a kid |
| `DELETE` | `/api/kids/<id>/` | Required | Delete a kid |

**POST / PATCH body:**
```json
{
  "birth_month": 7,
  "birth_year": 2018
}
```

**Validation rules:**
- `birth_month`: 1–12
- `birth_year`: must be within the last 12 years (e.g. 2014 or later in 2026)

---

### Venues

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/venues/` | None | List all non-archived venues |
| `POST` | `/api/venues/` | None | Create a venue |
| `GET` | `/api/venues/<id>/` | None | Get a single venue with ratings |
| `PATCH` | `/api/venues/<id>/` | Required (admin) | Update a venue |
| `DELETE` | `/api/venues/<id>/` | Required (admin) | Soft delete a venue |

**Query parameters for `GET /api/venues/`:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `main_category` | Filter by category | `Activity` or `Eatery` |
| `suburb` | Filter by suburb name | `Bondi Beach` |
| `indoor_outdoor` | Filter by setting | `Indoor` or `Outdoor` |
| `age` | Filter by kid's age | `5` |

**Soft delete:** `DELETE /api/venues/<id>/` sets `is_archived=True`. This cascades to archive all associated ratings and saved venue entries automatically.

---

### Ratings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/venues/<venue_id>/ratings/` | None | List all ratings for a venue |
| `POST` | `/api/venues/<venue_id>/ratings/` | Required | Add a rating to a venue |
| `GET` | `/api/venues/<venue_id>/ratings/<id>/` | None | Get a single rating |

**POST body:**
```json
{
  "rating_type": "yes"
}
```

Rating values: `yes` or `no`

---

### Saved Venues

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/saved/` | Required | List the user's saved venues |
| `POST` | `/api/saved/` | Required | Save a venue |
| `DELETE` | `/api/saved/<venue_id>/` | Required | Unsave a venue |

**POST body:**
```json
{
  "venue_id": 1
}
```

When an admin soft deletes a venue, it is automatically removed from all users' saved lists.

---

### Suburbs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/suburbs/` | None | Suburb autocomplete search |

---

## Project Structure

```
Eight-Legged-Engineers-backend/
├── playpal/
│   ├── playpal/          # Project settings and root URL config
│   ├── users/            # CustomUser and Kids models, Supabase auth
│   ├── venues/           # Venue, Rating, SavedVenue models
│   └── suburbs/          # Suburb autocomplete
├── venv/                 # Virtual environment (not committed)
├── .env                  # Environment variables (not committed)
└── requirements.txt
```

---

## Deployment (Heroku)

```bash
heroku login
heroku run "cd playpal && python manage.py migrate" --app play-pal
heroku run "cd playpal && python manage.py createsuperuser" --app play-pal
```

Open a database shell on Heroku:
```bash
heroku run "cd playpal && python manage.py dbshell" --app play-pal
```
