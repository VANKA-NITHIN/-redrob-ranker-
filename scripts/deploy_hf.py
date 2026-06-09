"""
Deploy Streamlit app to HuggingFace Spaces.
Usage: export HF_TOKEN=hf_... && python scripts/deploy_hf.py
"""
import os
from huggingface_hub import HfApi

SPACE_NAME = "redrob-ranker"
NAMESPACE = "vankanithin"

hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("=" * 60)
    print("HuggingFace API Token Required")
    print("=" * 60)
    print()
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Click 'New token' -> name it 'redrob-ranker' -> Role: 'write'")
    print("3. Copy the token (starts with hf_)")
    print()
    print("Then run:")
    print("   export HF_TOKEN=hf_your_token_here")
    print("   python scripts/deploy_hf.py")
    exit(1)

api = HfApi(token=hf_token)
print("Authenticated with HuggingFace Hub")

# Try creating Space (HuggingFace accepts: gradio, docker, static for SDK)
# For Streamlit, need to use 'docker' SDK or create via web UI
try:
    api.create_repo(
        repo_id=f"{NAMESPACE}/{SPACE_NAME}",
        repo_type="space",
        space_sdk="docker",
        private=False,
    )
    print(f"Created Space: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")
except Exception as e:
    err_msg = str(e)
    if "409" in err_msg or "already exists" in err_msg.lower():
        print("Space already exists (OK)")
    elif "400" in err_msg:
        print(f"API doesn't support creating Streamlit Spaces directly.")
        print("Creating via alternative method...")
        # Try with 'static' SDK (simplest, we can override)
        try:
            api.create_repo(
                repo_id=f"{NAMESPACE}/{SPACE_NAME}",
                repo_type="space",
                space_sdk="static",
                private=False,
            )
            print(f"Created Space with static SDK")
        except Exception as e2:
            if "409" in str(e2) or "already exists" in str(e2).lower():
                print("Space already exists (OK)")
            else:
                print(f"Could not create space automatically: {e2}")
                print()
                print("Please create the Space manually:")
                print(f"  1. Go to https://huggingface.co/new-space")
                print(f"  2. Space Name: {SPACE_NAME}")
                print(f"  3. SDK: Docker (Streamlit support via Dockerfile)")
                print(f"  4. Create the Space, then re-run this script")
                exit(1)
    else:
        print(f"Error: {e}")
        print()
        print("Please create the Space manually:")
        print(f"  1. Go to https://huggingface.co/new-space")
        print(f"  2. Space Name: {SPACE_NAME}")
        print(f"  3. SDK: Docker")
        print(f"  4. Create the Space, then re-run this script")
        exit(1)

# Create Dockerfile for Streamlit
dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
"""
with open("Dockerfile", "w") as f:
    f.write(dockerfile_content)
print("Created Dockerfile")

# Upload files
files = [
    ("Dockerfile", "Dockerfile"),
    ("app.py", "app.py"),
    ("requirements.txt", "requirements.txt"),
    ("config.py", "config.py"),
    ("ranker.py", "ranker.py"),
    ("data/sample_candidates.json", "data/sample_candidates.json"),
]
for local, remote in files:
    if os.path.exists(local):
        print(f"Uploading {local} -> {remote}...")
        api.upload_file(
            path_or_fileobj=local,
            path_in_repo=remote,
            repo_id=f"{NAMESPACE}/{SPACE_NAME}",
            repo_type="space",
        )

print()
print("Done!")
print(f"Space: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")
print(f"App:   https://{NAMESPACE}-{SPACE_NAME}.hf.space")
print("(App builds in 2-3 min | check logs at the Space URL)")
