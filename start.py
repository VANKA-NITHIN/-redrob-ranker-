"""
Development helper: starts both FastAPI backend and Vite frontend dev server.
Usage: python start.py
"""
import subprocess
import sys
import os
import signal
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    procs = []

    print("=" * 60)
    print("  Redrob AI — Enterprise Talent Intelligence Platform")
    print("=" * 60)
    print()
    print("Starting development servers...")
    print()

    # Start FastAPI backend
    print("[BACKEND]  Starting FastAPI on http://localhost:8000")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=ROOT,
    )
    procs.append(backend)

    # Wait a moment for backend to start
    time.sleep(2)

    # Start Vite frontend
    frontend_dir = os.path.join(ROOT, "frontend")
    if os.path.isdir(frontend_dir) and os.path.isfile(os.path.join(frontend_dir, "package.json")):
        print("[FRONTEND] Starting Vite dev server on http://localhost:5173")
        frontend = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            shell=True,
        )
        procs.append(frontend)
    else:
        print("[FRONTEND] No frontend directory found, skipping")

    print()
    print("=" * 60)
    print("  App running:")
    print("    Frontend:  http://localhost:5173")
    print("    Backend:   http://localhost:8000")
    print("    API Docs:  http://localhost:8000/api/docs")
    print("  Press Ctrl+C to stop all servers")
    print("=" * 60)

    try:
        # Wait for processes
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        for p in procs:
            try:
                p.terminate()
                p.wait(timeout=5)
            except Exception:
                p.kill()
        print("All servers stopped.")

if __name__ == "__main__":
    main()
