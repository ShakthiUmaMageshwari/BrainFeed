# Deployment Guide for BrainFeed 🚀

This project is a **Full-Stack Application** (Python Backend + HTML Frontend).
It **CANNOT** be hosted on GitHub Pages (which only supports static sites).

However, you can host the code on GitHub and deploy the live app to a free backend service.

---

## option 1: The Easiest Way (Render.com)

**Render** offers a free tier for Python web services.

1.  **Push code to GitHub:**
    -   Create a new repository on GitHub.
    -   Run these commands in your project folder:
        ```bash
        git init
        git add .
        git commit -m "Initial commit"
        git branch -M main
        git remote add origin https://github.com/YOUR_USERNAME/brainfeed.git
        git push -u origin main
        ```

2.  **Deploy on Render:**
    -   Go to [dashboard.render.com](https://dashboard.render.com/).
    -   Click **New +** -> **Web Service**.
    -   Connect your GitHub repository.
    -   **Settings:**
        -   **Runtime:** Python 3
        -   **Build Command:** `pip install -r backend/requirements.txt`
        -   **Start Command:** `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
    -   Click **Create Web Service**.

---

## Option 2: Docker (Universal)

You can run this anywhere (AWS, Azure, DigitalOcean) using Docker.

1.  **Create a `Dockerfile`** in the root directory:
    ```dockerfile
    FROM python:3.10-slim

    WORKDIR /app

    COPY backend/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

2.  **Build & Run:**
    ```bash
    docker build -t brainfeed .
    docker run -p 8000:8000 brainfeed
    ```

---

## Option 3: GitHub Codespaces (For Demo)

If you just want to show it off without setting up a server:
1.  Push code to GitHub.
2.  Click the Green **"Code"** button -> **Codespaces**.
3.  Click **"Create codespace on main"**.
4.  In the terminal, run: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
5.  GitHub will give you a private URL to view the running app.

---

## ⚠️ Important Note on Database
This project uses **SQLite** (`brainfeed.db`).
-   On platforms like Render/Heroku (Free Tier), the filesystem is **ephemeral**.
-   This means the database may reset every time you redeploy or after inactivity.
-   **Solution for Production:** Switch to **PostgreSQL**.
    -   Change `backend/db/database.py` to use `os.getenv("DATABASE_URL")`.
