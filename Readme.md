# MedSaaS - Hospital Management System

A modern, full-stack Hospital Management System built with Django and Bootstrap 5. MedSaaS connects patients, doctors, and administrators on a single platform for appointment booking, doctor approval workflows, and health insights.

## Features

- Role-based access control (Admin, Doctor, Patient)
- Doctor registration with admin approval workflow
- Patient appointment booking with specialization filtering
- Doctor dashboard: appointment queue management, medical notes/prescriptions, health insights CRUD
- Admin dashboard: KPI metrics, doctor approval, appointment management/reassignment
- Public health insights page with category filters, search, and pagination
- Premium light-themed healthcare UI (Bootstrap 5)

## Tech Stack

- Backend: Django 4.2, SQLite
- Frontend: HTML5, Bootstrap 5, Django Templates
- Image handling: Pillow

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/medsaas.git
cd medsaas
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 6. Set the superuser role to ADMIN

By default, new users (including superusers) get the `PATIENT` role. To grant admin dashboard access, open the Django shell:

```bash
python manage.py shell
```

Then run:

```python
from core.models import CustomUser
u = CustomUser.objects.get(username='YOUR_SUPERUSER_USERNAME')
u.role = 'ADMIN'
u.save()
exit()
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Usage Walkthrough

1. **Sign up** at `/signup/` as either a Doctor or a Patient.
   - Patients get instant dashboard access.
   - Doctors are placed in a "Pending Approval" state until an admin approves them.

2. **Log in as Admin** (the superuser account configured in step 6) at `/login/`. You'll be redirected to `/dashboard/admin/`, where you can:
   - View KPI metrics (total doctors, patients, appointments, pending approvals)
   - Approve or revoke doctor accounts
   - Cancel or reassign appointments

3. **Log in as the approved Doctor** at `/login/`. You'll be redirected to `/dashboard/doctor/`, where you can:
   - Update your profile (specialization, experience, phone, profile picture)
   - Manage your appointment queue (approve, complete, cancel, add medical notes)
   - Create, edit, and delete Health Insight articles

4. **Log in as the Patient** at `/login/`. You'll be redirected to `/dashboard/patient/`, where you can:
   - Book an appointment by filtering doctors by specialization, choosing a date/time, and describing symptoms
   - View upcoming appointments and cancel them if needed
   - View prescription/notes history for completed appointments

5. **Browse Health Insights** at `/health-insights/` (publicly accessible) to filter by category and search articles. If no doctor-authored insights exist yet, five default system articles are shown.

## Project Structure

```
medsaas/
├── manage.py
├── requirements.txt
├── medsaas/          # Project settings, URLs, WSGI/ASGI
├── core/             # Models, views, forms, URLs, admin, decorators
├── templates/
│   ├── core/         # Public pages and dashboards
│   └── registration/ # Login, signup, password reset
└── static/
    ├── css/style.css
    └── img/          # Default images for doctors and health insights
```

## Notes

- `db.sqlite3`, `media/`, and `venv/` are excluded from version control via `.gitignore`. Each developer should run migrations locally to generate their own database.
- For production deployment, move `SECRET_KEY` to an environment variable and set `DEBUG = False` in `medsaas/settings.py`.