# 🐳 Dockerized Attendance System

A modern, lightweight Attendance System built with Python Flask and packaged in a Docker container. Designed with a sleek, dark-mode user interface, this system provides administrators with daily session management and prevents duplicate attendance entries.

---

## ✨ Features

- **Daily Sessions:** Easily start a "New Day" from the admin dashboard to generate a fresh, active attendance link while invalidating the old one.
- **Roll Number Verification:** Enforces strict database-level unique constraints so a student cannot submit the same Roll Number twice in a single session.
- **Device Restriction (Anti-Spam):** Uses browser cookies to flag devices that have already marked attendance, preventing students from spamming submissions for their friends from the same browser.
- **Premium UI/UX:** A beautiful, responsive, and glassmorphic interface built with vanilla CSS.
- **Fully Dockerized:** Runs completely inside a Docker container, including its own internal SQLite database. No external dependencies required on your host machine other than Docker.

---

## 🚀 Getting Started

### Prerequisites
You must have [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine) installed and running on your machine.

### Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abhinavmishra123/dockerized-attendance-system.git
   cd dockerized-attendance-system
   ```

2. **Build the Docker Image:**
   ```bash
   docker build -t attendance-app .
   ```

3. **Run the Docker Container:**
   ```bash
   docker run -d -p 5000:5000 attendance-app
   ```
   *Note: This runs the container in detached mode (`-d`) and maps port 5000 on your machine to port 5000 in the container.*

---

## 🖥️ How to Use

### For Administrators
1. Open your web browser and navigate to **[http://localhost:5000](http://localhost:5000)**.
2. This is your **Admin Dashboard**. Here, you will see a list of everyone who has marked their attendance for the current active session.
3. You will also see a **Shared Link**. Copy this link and send it to your students.
4. When a new day begins (or a new class), click the **"Start New Day (Reset Link)"** button. This will immediately expire the old link and generate a new one, allowing students to submit their attendance again for the new session.

### For Students
1. Click the shared link provided by the administrator (e.g., `http://localhost:5000/attendance/<session-id>`).
2. Enter your **Full Name** and **Roll Number**.
3. Click Submit.
4. *If you attempt to submit again from the same browser, or if you try to use a Roll Number that has already been recorded for that day, the system will deny your request.*

---

## 🛠️ Technology Stack
- **Backend:** Python 3.11, Flask
- **Database:** SQLite (In-Memory/Container-Local)
- **Frontend:** HTML5, CSS3 (Vanilla)
- **Deployment:** Docker
