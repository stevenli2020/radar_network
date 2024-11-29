import os
import requests
import subprocess

from constants import DOMAIN_URL


def is_ui_working(url):
    """
    Check if the UI is working by sending a GET request.
    """
    try:
        response = requests.get(url, timeout=10)  # 10 seconds timeout
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error checking UI: {e}")
        return False


def restart_nginx():
    """
    Restart the Nginx service using Docker Compose.
    """
    try:
        print("Restarting Nginx service...")
        subprocess.run(
            ["docker", "compose", "restart"],
            check=True,
            cwd="/app/nginx-server",  # Set the working directory
            env=os.environ.copy(),  # Pass environment variables to the subprocess
        )
        print("Nginx service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart Nginx service: {e}")


def main():
    """
    Check the UI and restart Nginx if needed.
    """
    print("Checking if UI is working...")
    if not is_ui_working(DOMAIN_URL):
        print("UI is not working. Restarting Nginx...")
        restart_nginx()
    else:
        print("UI is working fine.")


if __name__ == "__main__":
    main()
