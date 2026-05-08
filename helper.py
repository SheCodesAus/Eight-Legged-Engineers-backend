import json
import os
from pathlib import Path
from urllib.request import urlopen

from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from jwt.algorithms import ECAlgorithm

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

supabase_url = os.environ.get("SUPABASE_URL")
if not supabase_url:
  raise ValueError("SUPABASE_URL environment variable is not set.")

jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
with urlopen(jwks_url) as response:
  jwks = json.loads(response.read().decode("utf-8"))

keys = jwks.get("keys", [])
if not keys:
  raise ValueError(f"No JWK keys returned from {jwks_url}")

public_key = None
last_error = None
for jwk in keys:
  try:
    public_key = ECAlgorithm.from_jwk(json.dumps(jwk))
    break
  except Exception as exc:
    last_error = exc

if public_key is None:
  raise ValueError(f"Unable to parse any JWKS key from {jwks_url}: {last_error}")

pem = public_key.public_bytes(
  encoding=serialization.Encoding.PEM,
  format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode("utf-8")

print(pem)