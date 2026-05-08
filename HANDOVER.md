**Project Handover**

- **Repo:** Eight-Legged-Engineers-backend
- **Project root:** playpal/
- **DB:** SQLite at playpal/db.sqlite3 (local development)

**Summary**

- Implemented Supabase-based authentication integration using a custom DRF authentication class (`users.authentication.SupabaseAuthentication`).
- Added `CustomUser.supabase_uid` and `Kids` model; created viewsets and serializers for users and kids.
- Fixed runtime migration/schema mismatches by restoring missing columns (`users_customuser.last_name`, `users_kids.created_at`) and by faking migrations when appropriate.
- Current auth path verifies Supabase JWTs with the public key from `.env` using `ES256` and a normalized PEM string.

**Current Status**

- Django dev server runs at `http://127.0.0.1:8000/`.
- `GET /api/users/` returns the users list (example: `[{"id":1,"email":"admin@admin.com","username":"Admin","supabase_uid":null,"kids":[]}]`).
- `POST /api/users/` requires a valid Supabase `access_token` (role `authenticated`) in the `Authorization: Bearer <token>` header.
- `.env` now stores `SUPABASE_JWT_PUBLIC_KEY` as a single quoted line with escaped newlines so python-dotenv parses it cleanly.

**Key Files**

- `playpal/playpal/settings.py` — reads `.env`, requires `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, and `SUPABASE_JWT_PUBLIC_KEY`, and normalizes the PEM key with `.replace('\\n', '\n')`.
- `playpal/users/authentication.py` — custom DRF auth that decodes ES256 tokens using the normalized public key from settings.
- `playpal/users/models.py` — `CustomUser`, `Kids`.
- `playpal/users/serializers.py` and `playpal/users/views.py` — DRF serializers & viewsets wired into `api/` router.

**Important Environment Values (.env)**

- `SUPABASE_URL` — e.g. `https://<project>.supabase.co`
- `SUPABASE_JWT_SECRET` — still present for legacy/local reference, but current JWT verification path uses the public key.
- `SUPABASE_JWT_PUBLIC_KEY` — store as a single dotenv-safe quoted line with `\n` escapes, not as multiple physical lines.
- `SUPABASE_SERVICE_ROLE_KEY` — service role key (privileged) — do NOT use for client sign-ins or frontend requests.
- `SUPABASE_JWKS_URL` — kept in `.env`, but current auth flow does not rely on JWKS.

**Reproducing & Local Commands**

1) Start dev server

```bash
cd playpal
c:/GitHub/Eight-Legged-Engineers-backend/venv/Scripts/python.exe manage.py runserver
```

2) Create/test a Supabase user and obtain an access token (Insomnia or curl)

Insomnia: POST `https://<PROJECT>.supabase.co/auth/v1/token?grant_type=password`
- Headers: `apikey: <ANON_KEY>` and `Content-Type: application/json`
- Body: `{"email":"you@example.com","password":"yourpassword"}`

curl example:

```bash
curl -s -X POST "https://<PROJECT>.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: <ANON_KEY>" -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'
```

Copy the `access_token` from the response. Verify payload locally:

```bash
python - <<'PY'
import jwt
tok = "<ACCESS_TOKEN>"
print(jwt.get_unverified_header(tok))
print(jwt.decode(tok, options={"verify_signature": False}))
PY
```

You should see `"role":"authenticated"` and a `sub` (user id) + `email` in the payload.

3) Call Django endpoint with token

```bash
curl -i -X POST http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","username":"newuser"}'
```

**Migration Fixes Applied**

- When Django migration history and DB schema diverged the pragmatic fix used was to:
  - Backup the DB file: `cp playpal/db.sqlite3 playpal/db.sqlite3.backup`
  - Add missing columns directly (SQLite `ALTER TABLE ... ADD COLUMN`) when safe.
  - Create an empty migration (if needed) and `python manage.py migrate users <migration> --fake` to align migration history.

**Troubleshooting**

- `403 Invalid token` — common causes:
  - You used an anon token (role `anon`) — it lacks `sub`/`email` and will be rejected.
  - You used the service role key as a token — do not do this for client requests.
  - `SUPABASE_JWT_PUBLIC_KEY` in `.env` is not a valid PEM value, or the `\n` escapes were pasted as real newlines.
  - The auth code is still using the wrong key variable; it should pass the normalized PEM value into `jwt.decode()`.
- `MalformedFraming` from PyJWT — usually means the PEM text in `.env` is malformed or not normalized before decoding.
- `python-dotenv could not parse statement` — caused by a broken multi-line `.env` value; fix the public key to a single quoted line with escaped newlines.

**Next Recommended Actions**

- Keep `SUPABASE_JWT_PUBLIC_KEY` formatted as a single quoted `.env` value with escaped newlines.
- Ensure `users.authentication.SupabaseAuthentication` continues to use the normalized PEM value from settings.
- Ensure `.env` contains correct `SUPABASE_URL` and the public key value, and do not commit `.env` to git.
- Commit any migration files created and deploy them; on remote run `python manage.py migrate` (do not `--fake` on remote unless you know DB already matches).

**Contacts / Notes**

- If you want, I can switch the auth path back to JWKS-based verification later, but the current repository state uses the public PEM key.

---
Generated: 2026-05-08
