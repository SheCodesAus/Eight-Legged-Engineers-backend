# Project Handover (Supabase + Django API)

This handover documents how to test the current authentication and CRUD behavior from Insomnia and curl, with focus on superuser workflows.

## 1) Stack And Auth Model

- Backend: Django + DRF
- Auth provider: Supabase Auth
- Django API auth: Supabase Bearer JWT decoded in `users.authentication.SupabaseAuthentication`
- Key point: API calls are authenticated by Supabase access token, not Django session login.

## 2) Base URLs

- Supabase Auth: `https://hyqwxbhjdjvxoftdcqvh.supabase.co/auth/v1`
- Django API (local): `http://127.0.0.1:8000/api`

## 3) Suggested Variables

Use these as Insomnia environment vars or shell variables:

- `SUPABASE_URL=https://hyqwxbhjdjvxoftdcqvh.supabase.co/auth/v1`
- `DJANGO_API=http://127.0.0.1:8000/api`
- `ANON_KEY=<supabase_anon_key>`
- `SUPERUSER_EMAIL=<email>`
- `SUPERUSER_PASSWORD=<password>`
- `ACCESS_TOKEN=<set after login>`

## 4) Superuser Workflow (Insomnia + curl)

### Step A. Login (Supabase)

Insomnia:

- Method: `POST`
- URL: `{{ SUPABASE_URL }}/token?grant_type=password`
- Headers:
  - `apikey: {{ ANON_KEY }}`
  - `Content-Type: application/json`
- Body:

```json
{
  "email": "{{ SUPERUSER_EMAIL }}",
  "password": "{{ SUPERUSER_PASSWORD }}"
}
```

curl:

```bash
curl -X POST "https://hyqwxbhjdjvxoftdcqvh.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"SUPERUSER_EMAIL","password":"SUPERUSER_PASSWORD"}'
```

Expected:

- `200 OK`
- Response includes `access_token` and `refresh_token`

### Step B. View End User List

Insomnia:

- Method: `GET`
- URL: `{{ DJANGO_API }}/users/`
- Header: `Authorization: Bearer {{ ACCESS_TOKEN }}`

curl:

```bash
curl -X GET "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Expected:

- Superuser/staff sees all users.
- Non-staff sees only their own user record.

### Step C. View Kids List

Insomnia:

- Method: `GET`
- URL: `{{ DJANGO_API }}/kids/`
- Header: `Authorization: Bearer {{ ACCESS_TOKEN }}`

curl:

```bash
curl -X GET "http://127.0.0.1:8000/api/kids/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Expected (current behavior):

- Only kids belonging to the authenticated user are returned, including for superuser.

### Step D. View Venue List

Insomnia:

- Method: `GET`
- URL: `{{ DJANGO_API }}/venues/`

curl:

```bash
curl -X GET "http://127.0.0.1:8000/api/venues/"
```

Expected:

- Returns all non-archived venues (`is_archived=false`).

### Step E. Update End User

Insomnia:

- Method: `PATCH`
- URL: `{{ DJANGO_API }}/users/<USER_ID>/`
- Headers:
  - `Authorization: Bearer {{ ACCESS_TOKEN }}`
  - `Content-Type: application/json`
- Body example:

```json
{
  "username": "updated_name",
  "email": "updated@example.com"
}
```

curl:

```bash
curl -X PATCH "http://127.0.0.1:8000/api/users/USER_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"updated_name","email":"updated@example.com"}'
```

Expected:

- Superuser can update any user record.

### Step F. Update Kid

Insomnia:

- Method: `PATCH`
- URL: `{{ DJANGO_API }}/kids/<KID_ID>/`
- Headers:
  - `Authorization: Bearer {{ ACCESS_TOKEN }}`
  - `Content-Type: application/json`
- Body example:

```json
{
  "birth_month": 8,
  "birth_year": 2021
}
```

curl:

```bash
curl -X PATCH "http://127.0.0.1:8000/api/kids/KID_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"birth_month":8,"birth_year":2021}'
```

Expected (current behavior):

- Works only for kids owned by authenticated user.
- Kid records of other users are not accessible.

### Step G. Update Venue

Insomnia:

- Method: `PATCH`
- URL: `{{ DJANGO_API }}/venues/<VENUE_ID>/`
- Headers:
  - `Authorization: Bearer {{ ACCESS_TOKEN }}`
  - `Content-Type: application/json`
- Body example:

```json
{
  "name": "Updated Venue Name",
  "is_published": true
}
```

curl:

```bash
curl -X PATCH "http://127.0.0.1:8000/api/venues/VENUE_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Venue Name","is_published":true}'
```

Expected:

- Venue updates succeed for valid payload.

### Step H. Delete End User

Insomnia:

- Method: `DELETE`
- URL: `{{ DJANGO_API }}/users/<USER_ID>/`
- Header: `Authorization: Bearer {{ ACCESS_TOKEN }}`

curl:

```bash
curl -X DELETE "http://127.0.0.1:8000/api/users/USER_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Expected:

- Superuser can delete any user (`204 No Content`).

### Step I. Delete Kid

Insomnia:

- Method: `DELETE`
- URL: `{{ DJANGO_API }}/kids/<KID_ID>/`
- Header: `Authorization: Bearer {{ ACCESS_TOKEN }}`

curl:

```bash
curl -X DELETE "http://127.0.0.1:8000/api/kids/KID_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Expected (current behavior):

- Works only for own kid.
- Other users' kids are not deletable from this endpoint.

### Step J. Delete Venue

Current state:

- `DELETE /api/venues/<id>/` is not implemented.
- Endpoint should return `405 Method Not Allowed`.

curl:

```bash
curl -X DELETE "http://127.0.0.1:8000/api/venues/VENUE_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Step K. Logout

Option 1: Django logout wrapper endpoint

Insomnia:

- Method: `POST`
- URL: `{{ DJANGO_API }}/auth/logout/`
- Header: `Authorization: Bearer {{ ACCESS_TOKEN }}`

curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/logout/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Option 2: Direct Supabase logout

Insomnia:

- Method: `POST`
- URL: `{{ SUPABASE_URL }}/logout`
- Headers:
  - `apikey: {{ ANON_KEY }}`
  - `Authorization: Bearer {{ ACCESS_TOKEN }}`

curl:

```bash
curl -X POST "https://hyqwxbhjdjvxoftdcqvh.supabase.co/auth/v1/logout" \
  -H "apikey: ANON_KEY" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Important:

- Always remove access/refresh tokens from client storage after logout.

## 5) Known Current Limitations

- Superuser can manage all users.
- Superuser cannot globally list/update/delete all kids through `/api/kids/`; endpoint is scoped to `request.user`.
- Venue delete is not implemented.
- Venue permissions are more open than user/kid endpoints.

## 6) Useful Endpoint Index

- `POST /auth/v1/token?grant_type=password` (Supabase login)
- `POST /auth/v1/logout` (Supabase logout)
- `GET /api/users/`
- `PATCH /api/users/<id>/`
- `DELETE /api/users/<id>/`
- `GET /api/kids/`
- `PATCH /api/kids/<id>/`
- `DELETE /api/kids/<id>/`
- `GET /api/venues/`
- `PATCH /api/venues/<id>/`
- `POST /api/auth/logout/` (Django wrapper logout)

---

Generated: 2026-05-09
