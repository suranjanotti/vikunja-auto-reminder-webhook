from fastapi import FastAPI, Request
import requests
from datetime import datetime, timedelta
import pytz
import os
import logging

app = FastAPI()

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# === CONFIGURATION ===
API_URL = os.getenv("VIKUNJA_API", "https://your-vikunja-instance/api/v1")
USERNAME = os.getenv("VIKUNJA_USERNAME", "your-username")
PASSWORD = os.getenv("VIKUNJA_PASSWORD", "your-password")
REMINDER_OFFSET = timedelta(days=1) + timedelta(hours=3)

@app.post("/webhook")
async def handle_webhook(_: Request):
    logging.info("Webhook received, scanning all tasks...")

    try:
        # === LOGIN ===
        login_resp = requests.post(
            f"{API_URL}/login",
            json={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        login_resp.raise_for_status()
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # === GET ALL PROJECTS ===
        projects_resp = requests.get(f"{API_URL}/projects", headers=headers)
        projects_resp.raise_for_status()
        projects = projects_resp.json()

        # === PROCESS TASKS IN PROJECTS ===
        for project in projects:
            project_id = project["id"]
            task_resp = requests.get(f"{API_URL}/projects/{project_id}/tasks", headers=headers)
            if task_resp.status_code != 200:
                print(f"Failed to get tasks for project {project_id}: {task_resp.text}")
                continue

            tasks = task_resp.json()
            for task in tasks:
                task_id = task["id"]
                task_title = task.get("title", f"(task id {task_id})")
                existing_reminders = task.get("reminders", [])
                due_date_str = task.get("due_date")

                if not due_date_str or existing_reminders:
                    continue  # Skip if no due date or already has reminders

                if due_date_str.startswith("0001-01-01"):
                    print(f"Skipping task {task_title}: placeholder due date.")
                    continue

                try:
                    due_dt = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                except Exception:
                    print(f"Skipping task {task_title}: invalid due date format.")
                    continue

                if due_dt < datetime.now(pytz.utc):
                    print(f"Skipping task {task_title}: due date is in the past.")
                    continue

                # Fetch the full task data before modifying
                full_task_resp = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers)
                if full_task_resp.status_code != 200:
                    print(f"Failed to get full task {task_id}: {full_task_resp.status_code} {full_task_resp.text}")
                    continue

                full_task = full_task_resp.json()
                full_task["reminders"] = [
                    {"relative_period": -86400, "relative_to": "due_date"},
                    {"relative_period": -10800, "relative_to": "due_date"}
                ]

                print(f"Updating task '{task_title}' with reminders via POST /tasks/{task_id}")
                post_resp = requests.post(
                    f"{API_URL}/tasks/{task_id}",
                    headers={**headers, "Content-Type": "application/json"},
                    json=full_task
                )

                if post_resp.status_code != 200:
                    print(f"Failed to update task '{task_title}': {post_resp.status_code} {post_resp.text}")

    except Exception as e:
        logging.exception(f"Error running reminder logic: {e}")

    return {"status": "reminder logic executed"}
