# 🔔 Vikunja Reminder Webhook

This project adds automatic **1-day and 3-hour before** reminders to tasks in [Vikunja](https://vikunja.io) using a FastAPI webhook listener.

When a task is created or updated in Vikunja, this webhook scans all projects and ensures tasks with due dates get reminders added — without manual effort.

---

## 🚀 Features

- 📬 Auto-adds reminders relative to task due dates
- 🔁 Runs every time a task changes (via webhook)
- ✅ Skips placeholder or past due dates
- 🔐 Authenticates via Vikunja's `/login` API
- 🐳 Runs in a lightweight Python Docker container

---

## 📦 Directory Structure

```bash
vikunja-reminder-webhook/
├── Dockerfile
├── webhook_listener.py
└── docker-compose.yml  # (optional if integrating into a stack)
