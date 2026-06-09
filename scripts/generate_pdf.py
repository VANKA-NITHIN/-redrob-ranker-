"""
Generate PDF of pitch_deck.html using Chrome headless mode.
"""
import subprocess
import os

html_path = os.path.abspath("pitch_deck.html")
pdf_path = os.path.abspath("pitch_deck.pdf")

# Convert Windows path to file URI
file_uri = "file:///" + html_path.replace("\\", "/")

# Chrome paths to try
chrome_paths = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe"),
]

for cp in chrome_paths:
    if os.path.exists(cp):
        print(f"Found Chrome at: {cp}")
        cmd = [
            cp,
            "--headless",
            "--disable-gpu",
            "--no-margins",
            f"--print-to-pdf={pdf_path}",
            file_uri,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"PDF generated: {pdf_path} ({size} bytes)")
            else:
                print(f"Chrome ran but PDF not found")
                print(f"stderr: {result.stderr}")
        except Exception as e:
            print(f"Error running Chrome: {e}")
        break
else:
    print("Chrome not found. Open pitch_deck.html in Chrome and press Ctrl+P to print to PDF.")
