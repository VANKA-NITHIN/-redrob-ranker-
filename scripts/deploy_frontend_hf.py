"""
Deploy React frontend to HuggingFace as a Static Space.

Usage:
    export HF_TOKEN=hf_...
    python scripts/deploy_frontend_hf.py

Prerequisites:
    - Frontend must be built first (the script builds it if dist/ is missing)
    - huggingface_hub package installed
"""
import os
import subprocess
import sys
from pathlib import Path

from huggingface_hub import HfApi

# ── Configuration ───────────────────────────────────────────────────────────

SPACE_NAME = "redrob-frontend"
NAMESPACE = "vankanithin"
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

# ── Token Check ─────────────────────────────────────────────────────────────

hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("=" * 60)
    print("HuggingFace API Token Required")
    print("=" * 60)
    print()
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Click 'New token' -> name it 'redrob-frontend' -> Role: 'write'")
    print("3. Copy the token (starts with hf_)")
    print()
    print("Then run:")
    print("   export HF_TOKEN=hf_your_token_here")
    print("   python scripts/deploy_frontend_hf.py")
    sys.exit(1)

api = HfApi(token=hf_token)
print("[OK] Authenticated with HuggingFace Hub")

# ── Build frontend if needed ────────────────────────────────────────────────

if not DIST_DIR.exists():
    print("[BUILD] dist/ not found. Building the frontend...")
    result = subprocess.run(
        ["npx", "vite", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("[FAIL] Build failed:")
        print(result.stderr)
        sys.exit(1)
    print("[OK] Frontend built successfully")
else:
    print(f"[DIST] Using existing dist/ at {DIST_DIR}")

# ── Create or Get Space ─────────────────────────────────────────────────────

repo_id = f"{NAMESPACE}/{SPACE_NAME}"
print(f"\n[SPACE] Setting up Space: {repo_id}")

try:
    api.create_repo(
        repo_id=repo_id,
        repo_type="space",
        space_sdk="static",
        private=False,
    )
    print(f"[OK] Created Space: https://huggingface.co/spaces/{repo_id}")
except Exception as e:
    err_msg = str(e)
    if "409" in err_msg or "already exists" in err_msg.lower():
        print("[INFO] Space already exists (using existing)")
    else:
        print(f"[FAIL] Error creating Space: {e}")
        print()
        print("Please create the Space manually:")
        print(f"  1. Go to https://huggingface.co/new-space")
        print(f"  2. Space Name: {SPACE_NAME}")
        print(f"  3. SDK: Static")
        print(f"  4. Create the Space, then re-run this script")
        sys.exit(1)

# ── Upload Files ────────────────────────────────────────────────────────────

print(f"\n[UPLOAD] Uploading files from {DIST_DIR}...")

# Upload the entire dist/ directory in one efficient call
api.upload_folder(
    folder_path=str(DIST_DIR),
    path_in_repo=".",
    repo_id=repo_id,
    repo_type="space",
    delete_patterns=["*.md", "*.svg", "*.css", "style.css"],  # Clean up default HF template files
)

# Count uploaded files
uploaded = sum(1 for _ in DIST_DIR.rglob("*") if _.is_file())

print(f"\n[DONE] Uploaded {uploaded} files.")
print()
print(f"Space:  https://huggingface.co/spaces/{repo_id}")
print(f"App:    https://{NAMESPACE}-{SPACE_NAME}.static.hf.space")
