import urllib.request
import json
import os

# CREDENTIALS
URL = "https://pharmacy-db-frnonato-lgtm.turso.io/v2/pipeline"
TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzM2ODQ1MDksImlkIjoiMDE5Y2Y3ZDQtNDkwMS03YWUxLTg3MTMtMWI2MDBmODY1OWNiIiwicmlkIjoiNzAxMDkxNGUtODY1ZC00YjFlLWIzZDItZGU5MWE3OTZlNzBjIn0.qybDl8-wJr4zKmTRCjHzpU8DQkHrCjjwji9Y7ridE0wnXTzJO3MemNT5sD_kciMpCrGzmrEvUsfzGcNed3i2Bw"

def test_connection():
    print(f"🔍 Testing connection to {URL}...")
    
    # Simple query to test
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": "SELECT 1;"}}
        ]
    }
    
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            print(f"✅ Success! Status: {status}")
            print(f"Response: {body}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} {e.reason}")
        print(f"Error Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_connection()
