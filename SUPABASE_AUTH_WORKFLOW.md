# PlayPal Supabase Authentication Workflow

This document provides a complete step-by-step guide for end users to interact with the PlayPal backend using Supabase authentication. It covers all key workflows: account creation, sign-in, adding kids, retrieving profile data, and logout.

---

## Overview

PlayPal uses **Supabase** for authentication. The workflow involves:
1. Creating an account through Supabase
2. Obtaining a JWT access token from Supabase
3. Using the token to access protected API endpoints
4. Adding and managing kids' profiles
5. Logging out

**Base URL:** `http://localhost:8000/api/` (or your deployed server URL)

## Insomnia Auth Matrix

In Insomnia, set the request auth to `Bearer Token` only for the protected PlayPal API endpoints below. Leave auth off for the public Supabase login/signup calls.

| Endpoint | Method | Needs Supabase Auth in Insomnia? | Notes |
|---|---:|---|---|
| `https://{SUPABASE_URL}/auth/v1/signup` | POST | No | Public Supabase sign-up request |
| `https://{SUPABASE_URL}/auth/v1/token?grant_type=password` | POST | No | Public Supabase sign-in request |
| `POST /api/auth/webhook/` | POST | No | Called by Supabase webhooks, not by the end user |
| `GET /api/users/me/` | GET | Yes | Use `Authorization: Bearer {access_token}` |
| `PATCH /api/users/me/` | PATCH | Yes | Use `Authorization: Bearer {access_token}` |
| `GET /api/kids/` | GET | Yes | Use `Authorization: Bearer {access_token}` |
| `POST /api/kids/` | POST | Yes | Use `Authorization: Bearer {access_token}` |
| `DELETE /api/kids/{kid_id}/` | DELETE | Yes | Use `Authorization: Bearer {access_token}` |
| `POST /api/auth/logout/` | POST | Yes | Use `Authorization: Bearer {access_token}` |

### Insomnia Setup

For the protected API requests, configure Insomnia like this:

1. Open the request in Insomnia.
2. Go to the Auth tab.
3. Choose `Bearer Token`.
4. Paste the Supabase `access_token`.
5. Send the request.

For signup and sign-in requests, leave Auth disabled and only send the `apikey` header plus JSON body.

---

## Workflow 1: Create a User Account with Supabase Auth

### Step 1.1: Sign Up via Supabase
Create a new account directly with Supabase using their authentication endpoint.

**Endpoint:** `https://{SUPABASE_URL}/auth/v1/signup`  
**Method:** `POST`  
**Headers:**
```
Content-Type: application/json
apikey: {SUPABASE_ANON_KEY}
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": "abc123def456",
    "email": "user@example.com",
    "email_confirmed_at": "2026-05-09T10:30:00Z",
    "created_at": "2026-05-09T10:30:00Z"
  },
  "session": {
    "access_token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "refresh_token": "refresh_token_xyz"
  }
}
```

### Step 1.2: Automatic User Creation in PlayPal
When you sign up via Supabase, a corresponding user is automatically created in the PlayPal backend through:
- **Webhook**: Supabase sends an INSERT event to `POST /api/auth/webhook/`
- **First Auth**: On first API call with the token, the `SupabaseAuthentication` class auto-creates the Django user

**Result:** Your PlayPal account is created with:
- `email`: Your registered email
- `supabase_uid`: Your unique Supabase user ID
- `username`: Your Supabase UID
- Empty `kids` list (no children added yet)

---

## Workflow 2: Sign In with Supabase Auth

### Step 2.1: Log In via Supabase
Sign in with your existing Supabase account credentials.

**Endpoint:** `https://{SUPABASE_URL}/auth/v1/token?grant_type=password`  
**Method:** `POST`  
**Headers:**
```
Content-Type: application/json
apikey: {SUPABASE_ANON_KEY}
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_xyz",
  "user": {
    "id": "abc123def456",
    "email": "user@example.com"
  }
}
```

**Common Error:** If Supabase returns `400` with `email not confirmed`, the account exists but has not been verified yet. Confirm the email in the Supabase dashboard, or disable email confirmation for local development before retrying this request in Insomnia.

### Step 2.2: Store the Token
Save the `access_token` locally (in your app's secure storage):
- Use it for all subsequent API requests
- Include it in the `Authorization` header: `Bearer {access_token}`
- Token expires in 3600 seconds (1 hour)
- Use `refresh_token` to get a new access token when expired

---

## Workflow 3: Add a Kid

### Step 3.1: Create a Kid Profile
Add a child to your account by specifying their birth month and year.

**Endpoint:** `POST /api/kids/`  
**Authentication:** Required (Bearer token)  
**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "birth_month": 3,
  "birth_year": 2018
}
```

**Field Explanations:**
- `birth_month`: Integer from 1-12 (1 = January, 12 = December)
- `birth_year`: Integer representing the year (minimum 2010)

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/kids/ \
  -H "Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "birth_month": 3,
    "birth_year": 2018
  }'
```

**Success Response (201):**
```json
{
  "id": 1,
  "birth_month": 3,
  "birth_year": 2018,
  "user": "abc123def456"
}
```

### Step 3.2: Verify Kid Was Added
The kid is now linked to your account with `user = abc123def456` (your Supabase UID).

**Possible Errors:**
- **401 Unauthorized**: Token is missing, invalid, or expired
- **400 Bad Request**: Missing required fields or invalid values
- **403 Forbidden**: Token signature verification failed

---

## Workflow 4: Get Your User Profile with Kids' Details

### Step 4.1: Retrieve Your Profile
Fetch your complete user profile including all your kids' information.

**Endpoint:** `GET /api/users/me/`  
**Authentication:** Required (Bearer token)  
**Headers:**
```
Authorization: Bearer {access_token}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "abc123def456",
  "supabase_uid": "abc123def456",
  "kids": [
    {
      "id": 1,
      "birth_month": 3,
      "birth_year": 2018,
      "created_at": "2026-05-09T10:35:22Z"
    },
    {
      "id": 2,
      "birth_month": 7,
      "birth_year": 2020,
      "created_at": "2026-05-09T10:36:15Z"
    }
  ]
}
```

**Response Field Explanations:**
- `id`: Your internal PlayPal user ID
- `email`: Your registered email address
- `username`: Your Supabase UID
- `supabase_uid`: Your unique identifier from Supabase
- `kids`: Array of your children's profiles
  - `id`: Internal kid ID
  - `birth_month`: Child's birth month (1-12)
  - `birth_year`: Child's birth year
  - `created_at`: ISO timestamp when the kid was added

### Step 4.2: Get Only Your Kids' List
If you only need the kids' data, you can extract from the profile response or make a separate request.

**Endpoint:** `GET /api/kids/`  
**Authentication:** Required (Bearer token)  
**Headers:**
```
Authorization: Bearer {access_token}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/kids/ \
  -H "Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "birth_month": 3,
    "birth_year": 2018,
    "created_at": "2026-05-09T10:35:22Z"
  },
  {
    "id": 2,
    "birth_month": 7,
    "birth_year": 2020,
    "created_at": "2026-05-09T10:36:15Z"
  }
]
```

---

## Workflow 5: Log Out

### Step 5.1: Log Out via PlayPal Backend
Call the logout endpoint to invalidate your session on the server side.

**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** Required (Bearer token)  
**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Success Response (200):**
```json
{
  "detail": "Logged out. Clear client-side tokens to complete logout."
}
```

**Possible Responses:**

| Status | Response | Meaning |
|--------|----------|---------|
| 200 | `{"detail": "Logged out. Clear client-side tokens..."}` | Successfully logged out |
| 401 | `{"detail": "Authentication credentials were not provided."}` | No valid token provided |
| 502 | `{"detail": "Supabase logout failed.", ...}` | Issue reaching Supabase |

### Step 5.2: Clear Client-Side Tokens
After receiving a successful response:
1. **Delete** the `access_token` from your local storage
2. **Delete** the `refresh_token` from your local storage
3. Redirect to the login page
4. You are now fully logged out

### Step 5.3: Full Logout Flow (with Supabase)
The backend automatically:
1. Calls `POST /auth/v1/logout` to Supabase
2. Invalidates the session on the Supabase side
3. Confirms logout to your client

No additional calls to Supabase are needed from your client.

---

## Common Tasks & Examples

### Task: Refresh Your Access Token (When Expired)

**Endpoint:** `https://{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token`  
**Method:** `POST`  
**Headers:**
```
Content-Type: application/json
apikey: {SUPABASE_ANON_KEY}
```

**Request Body:**
```json
{
  "refresh_token": "your_refresh_token_here"
}
```

**Success Response (200):**
```json
{
  "access_token": "new_jwt_token_here",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Task: Update Your Profile

**Endpoint:** `PATCH /api/users/me/`  
**Authentication:** Required (Bearer token)  
**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body** (partial update):
```json
{
  "email": "newemail@example.com"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "abc123def456",
  "supabase_uid": "abc123def456",
  "kids": [...]
}
```

---

### Task: Delete a Kid

**Endpoint:** `DELETE /api/kids/{kid_id}/`  
**Authentication:** Required (Bearer token)  
**Headers:**
```
Authorization: Bearer {access_token}
```

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/kids/1/ \
  -H "Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (204):** No content (empty response)

---

## Error Handling

### Common HTTP Status Codes

| Status | Error | Cause | Solution |
|--------|-------|-------|----------|
| 400 | Bad Request | Missing/invalid fields | Check request body format |
| 401 | Unauthorized | Missing token or invalid token | Provide valid Bearer token |
| 403 | Forbidden | Token signature invalid | Refresh token via Supabase |
| 404 | Not Found | Resource doesn't exist | Check endpoint and IDs |
| 500 | Server Error | Backend issue | Contact support |

### Example Error Response (401):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Example Error Response (400):
```json
{
  "birth_month": ["Ensure this value is less than or equal to 12."],
  "birth_year": ["Ensure this value is greater than or equal to 2010."]
}
```

---

## Security Best Practices

1. **Store tokens securely**: Use encrypted local storage, not plain text
2. **Use HTTPS**: Always use HTTPS in production (not HTTP)
3. **Refresh tokens**: Get new access tokens before expiration using refresh tokens
4. **Clear tokens on logout**: Remove all tokens from client storage
5. **Don't share tokens**: Never share your access token with anyone
6. **Validate SSL certificates**: Always verify SSL in production
7. **Use secure endpoints**: Always use the official Supabase and PlayPal URLs

---

## Quick Reference Summary

| Action | Endpoint | Method | Auth Required |
|--------|----------|--------|---------------|
| Sign Up | `https://{SUPABASE_URL}/auth/v1/signup` | POST | No |
| Sign In | `https://{SUPABASE_URL}/auth/v1/token?grant_type=password` | POST | No |
| Refresh Token | `https://{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token` | POST | No |
| Get Profile | `/api/users/me/` | GET | Yes |
| Update Profile | `/api/users/me/` | PATCH | Yes |
| Get Kids | `/api/kids/` | GET | Yes |
| Add Kid | `/api/kids/` | POST | Yes |
| Delete Kid | `/api/kids/{kid_id}/` | DELETE | Yes |
| Logout | `/api/auth/logout/` | POST | Yes |

---

## Testing the Workflow

You can test this workflow using `curl`, **Postman**, or any HTTP client:

```bash
# 1. Sign up
curl -X POST https://your-supabase-url/auth/v1/signup \
  -H "apikey: your-anon-key" \
  -d '{"email":"test@example.com","password":"password123"}'

# 2. Extract access_token from response and use it

# 3. Add a kid
curl -X POST http://localhost:8000/api/kids/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -d '{"birth_month":5,"birth_year":2020}'

# 4. Get profile
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"

# 5. Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## Support & Troubleshooting

### Token Expired?
- Use your `refresh_token` to get a new `access_token`
- Try again with the new token

### "Invalid Token" Error?
- Ensure token is correctly formatted: `Authorization: Bearer {token}`
- Check that the token hasn't expired
- Verify you copied the full token without extra spaces

### Can't Access Kids or Profile?
- Verify you're authenticated (Bearer token in header)
- Make sure the token is from Supabase, not another source
- Ensure your Supabase account was created through the signup endpoint

### "Authentication Credentials Not Provided"?
- Add the `Authorization` header to your request
- Use the exact format: `Authorization: Bearer {access_token}`
- Don't include extra characters or whitespace

---

**Last Updated:** May 2026  
**Backend Framework:** Django REST Framework  
**Auth Provider:** Supabase  
**Token Algorithm:** ES256 (JWT)
