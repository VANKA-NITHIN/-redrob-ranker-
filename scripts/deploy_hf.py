"""
Deploy Streamlit app to HuggingFace Spaces.
Usage: set HF_TOKEN=hf_... && python scripts/deploy_hf.py

Get your token at: https://huggingface.co/settings/tokens
"""
import os
from huggingface_hub import HfApi

SPACE_NAME = "redrob-ranker"
NAMESPACE = "VANKA-NITHIN"

hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("=" * 60)
    print("HuggingFace API Token Required")
    print("=" * 60)
    print("\n1. Go to: https://huggingface.co/settings/tokens")
    print("2. Click 'New token' → name it 'redrob-ranker' → Role: 'write'")
    print("3. Copy the token (starts with hf_)")
    print("\nThen run:")
    print('   set HF_TOKEN=hf_your_token_here')
    print('   python scripts/deploy_hf.py')
    print("\nOr manually at https://huggingface.co/new-space:")
    print("  Space Name: redrob-ranker, SDK: Streamlit")
    print("  Upload: app.py, requirements.txt, config.py, ranker.py")
    print("  Create data/ folder with sample_candidates.json")
    exit(1)

api = HfApi(token=hf_token)

# Check / create Space
try:
    api.get_space_repo(f"{NAMESPACE}/{SPACE_NAME}")
    print(f"Space exists: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")
except Exception:
    api.create_repo(
        repo_id=f"{NAMESPACE}/{SPACE_NAME}",
        repo_type="space",
        space_sdk="streamlit",
        private=False,
    )
    print(f"Space created: https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")

# Upload files
files = [
    ("app.py", "app.py"),
    ("requirements.txt", "requirements.txt"),
    ("config.py", "config.py"),
    ("ranker.py", "ranker.py"),
    ("data/sample_candidates.json", "data/sample_candidates.json"),
]
for local, remote in files:
    if os.path.exists(local):
        print(f"Uploading {local}...")
        api.upload_file(
            path_or_fileobj=local,
            path_in_repo=remote,
            repo_id=f"{NAMESPACE}/{SPACE_NAME}",
            repo_type="space",
        )

print(f"\n✅ Deployed!")
print(f"   https://huggingface.co/spaces/{NAMESPACE}/{SPACE_NAME}")
print(f"   https://{NAMESPACE}-{SPACE_NAME}.hf.space")
print("(App takes ~2-3 min to build)")
