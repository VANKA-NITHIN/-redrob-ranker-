"""
Deploy Streamlit app to HuggingFace Spaces.
Uses HuggingFace API token from environment variable or prompts to create one.
"""
import os
import sys
from huggingface_hub import HfApi

HF_EMAIL = "vankanithin2004@gmail.com"
SPACE_NAME = "redrob-ranker"
NAMESPACE = "VANKA-NITHIN"

# Check if HF_TOKEN is set in environment
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("=" * 60)
    print("HuggingFace API Token Required")
    print("=" * 60)
    print(f"\nEmail: {HF_EMAIL}")
    print("\nTo deploy, you need a HuggingFace API token.")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Click 'New token'")
    print("3. Name it 'redrob-ranker' with 'write' role")
    print("4. Copy the token (starts with hf_)")
    print("\nThen run:")
    print(f"  set HF_TOKEN=hf_your_token_here")
    print(f"  python scripts/deploy_hf.py")
    print("\nOr manually create the Space at:")
    print(f"  https://huggingface.co/new-space")
    print("\nSettings: Space Name = 'redrob-ranker', SDK = 'Streamlit'")
    print("Then upload: app.py, requirements.txt, config.py, ranker.py")
    print("And create a 'data' folder with sample_candidates.json")
    sys.exit(1)

api = HfApi(token=hf_token)
print(f"Logged in as: {HF_EMAIL}")

# Check if Space exists, create if not
try:
    space_info = api.get_space_repo(f"{NAMESPACE}/{SPACE_NAME}")
    print(f"Space exists: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")
except Exception:
    print(f"Creating Space: {NAMESPACE}/{SPACE_NAME}...")
    api.create_repo(
        repo_id=f"{NAMESPACE}/{SPACE_NAME}",
        repo_type="space",
        space_sdk="streamlit",
        private=False,
    )
    print(f"Space created: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")

# Upload files
print("\nUploading files...")
files_to_upload = [
    ("app.py", "app.py"),
    ("requirements.txt", "requirements.txt"),
    ("config.py", "config.py"),
    ("ranker.py", "ranker.py"),
    ("data/sample_candidates.json", "data/sample_candidates.json"),
]

for local_path, repo_path in files_to_upload:
    if os.path.exists(local_path):
        print(f"  Uploading {local_path}...")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=f"{NAMESPACE}/{SPACE_NAME}",
            repo_type="space",
        )
    else:
        print(f"  Skipping {local_path} (not found)")

print(f"\n✅ Deployment complete!")
print(f"   Space: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")
print(f"   App:   https://{NAMESPACE}-{SPACE_NAME}.hf.space")
print("\nNote: The app may take 2-3 minutes to build after first upload.")
