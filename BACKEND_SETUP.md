# EduBond Django Backend

## 1. Install dependencies
```bash
pip install -r requirements.txt
```

## 2. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 3. Create admin user (optional)
```bash
python manage.py createsuperuser
```

## 4. Run server
```bash
python manage.py runserver
```

## 5. Configure real OTP email (SMTP)
Set environment variables before running server:

```bash
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST=smtp.gmail.com
set EMAIL_PORT=587
set EMAIL_HOST_USER=your_email@gmail.com
set EMAIL_HOST_PASSWORD=your_app_password
set EMAIL_USE_TLS=true
set DEFAULT_FROM_EMAIL=EduBond <your_email@gmail.com>
```

Important:
- `EMAIL_HOST_PASSWORD` must be a Gmail App Password, not your normal Gmail password.
- Enable Google 2-Step Verification before creating the App Password.
- Start the server in the same terminal where you set these variables.

Verify email first:

```bash
python manage.py test_email your_email@gmail.com
```

If that succeeds, OTP email should also work.

For local testing (no real email), keep default console backend.

## API base
`/api/`

## Main endpoints
- `POST /api/auth/send-otp/`
- `POST /api/auth/login/`
- `POST /api/auth/register/`
- `GET/PATCH /api/auth/profile/`
- `GET /api/auth/people/`
- `POST /api/auth/connect/<user_id>/`
- `GET/POST /api/community/posts/`
- `POST /api/community/posts/<post_id>/like/`
- `GET/POST /api/community/posts/<post_id>/comments/`
- `GET/POST /api/community/grievances/`
- `GET /api/community/suggestions/`
- `GET /api/community/events/`
- `GET/POST /api/marketplace/listings/`
- `GET/PATCH/DELETE /api/marketplace/listings/<id>/`
- `POST /api/marketplace/listings/<listing_id>/images/`
- `GET/POST /api/studyhub/materials/`
- `POST /api/studyhub/materials/<material_id>/download/`
- `GET /api/studyhub/subjects/`
- `GET /api/hostel/hostels/`
- `GET /api/hostel/hostels/<slug>/`
- `GET/POST /api/hostel/hostels/<slug>/faqs/`
- `GET/POST /api/chat/threads/`
- `GET/POST /api/chat/threads/<thread_id>/messages/`

## Notes
- Auth uses JWT (`Authorization: Bearer <access_token>`).
- OTP APIs return `dev_otp` only when `DEBUG=true`.
- File uploads use `multipart/form-data`.
