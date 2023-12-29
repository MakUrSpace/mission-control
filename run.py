"""Python script passthrough to invoke the app with Gunicorn."""
import subprocess

def run_gunicorn():
    command = [
        "gunicorn",
        "-k", "eventlet",    # Worker class
        "-w", "1",           # Number of workers
        "--reload",          # Auto-reload on code changes
        "app:create_app()",  # Application factory
        "--bind", "0.0.0.0:5000"
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Gunicorn: {e}")

if __name__ == '__main__':
    run_gunicorn()
