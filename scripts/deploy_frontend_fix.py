"""
Fix HuggingFace static space deployment by uploading README.md config.
Uses UTF-8 encoding explicitly for emoji compatibility.
"""
import io
import os
import sys
from huggingface_hub import HfApi

REPO_ID = "vankanithin/redrob-frontend"
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("Error: HF_TOKEN not set")
    sys.exit(1)

api = HfApi(token=hf_token)
print("[OK] Connected to HuggingFace Hub")

# Create README.md with proper YAML front matter for static space
# Use the trophy emoji that works on HF
lines = [
    "---",
    "title: Redrob AI Talent Intelligence Platform",
    "emoji: \U0001F3C6",
    "colorFrom: blue",
    "colorTo: purple",
    "sdk: static",
    "pinned: false",
    "---",
    "",
    "# Redrob AI Talent Intelligence Platform",
    "",
    "AI-powered candidate ranking system for the Redrob Hackathon.",
    "",
    "## API Backend",
    "",
    "This frontend requires the backend API running at:",
    "https://vankanithin-redrob-ranker.hf.space/api",
]
readme_content = "\n".join(lines)

# Write with explicit UTF-8 encoding
readme_path = os.path.join(DIST_DIR, "README.md")
with io.open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content)
print("[OK] Created README.md with UTF-8 encoding")

# Upload README.md first
print("[UPLOAD] Uploading README.md...")
with io.open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()
api.upload_file(
    path_or_fileobj=content.encode("utf-8"),
    path_in_repo="README.md",
    repo_id=REPO_ID,
    repo_type="space",
)
print("[OK] README.md uploaded")

# Upload all dist files
print("[UPLOAD] Uploading all frontend files...")
for root, dirs, files in os.walk(DIST_DIR):
    for f in files:
        if f == "README.md":
            continue
        local = os.path.join(root, f)
        remote = os.path.relpath(local, DIST_DIR).replace(os.sep, "/")
        api.upload_file(
            path_or_fileobj=local,
            path_in_repo=remote,
            repo_id=REPO_ID,
            repo_type="space",
        )
        print("  Uploaded:", remote)

print()
print("[DONE] All files uploaded successfully!")
print("Space:", "https://huggingface.co/spaces/" + REPO_ID)
print("App:", "https://" + REPO_ID.replace("/", "-") + ".static.hf.space")
