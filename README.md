# Student Registration Flask Application

## Overview

This project is a student registration system built with Flask and MySQL. It allows users to register students through a web form and view all registered students. The project will be deployed in two phases:

1. **Monolithic Architecture** on an EC2 instance using Ubuntu.
2. **Microservices Architecture**, containerized with Docker and orchestrated using Kubernetes, deployed via CI/CD pipelines.

## Features

- Register students through a web form (`register.html`)
- View all registered students (`student.html`)
- Data stored in a MySQL database
- Built using Flask (Python)
- Initially deployed as a monolithic application
- Later transitioned to microservices (`docker-compose.yml` & `Dockerfile`) and lastly deployed on Kubernetes cluster (`manifest files`), using CI/CD

---

## Monolithic Deployment on EC2

### Step 1: Launch EC2 Instance

- Use **Ubuntu AMI**

### Step 2: System Setup

```bash
sudo apt update
python3 --version   # Check if Python is installed
sudo apt install python3.12-venv -y
```

### Step 3: Project Setup

```bash
mkdir pyapp
cd pyapp
git init
git pull https://github.com/harshkhalkar/student-registration-flask-application.git
```

Use only the following files for now:
- `app.py`
- `requirements.txt`
- `templates/register.html`
- `templates/student.html`
Ignore other files like `Dockerfile`, `docker-compose.yml` and else for now.

### Step 4: MySQL Setup

```bash
sudo apt install mysql-server -y
sudo mysql_secure_installation
```

Login to MySQL:

```bash
sudo mysql
```

Run the following to configure root user and initialize database:

```bash
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_new_password';
FLUSH PRIVILEGES;
EXIT;
```
Then:

```bash
mysql -u root -p < init.sql
```

Or run the SQL manually (see `init.sql` content below).

### Step 5: Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Step 6: Access Application

Visit: http://<public-ip>:5000

## File Structure (for Monolithic Setup)

```bash
.
├── app.py
├── requirements.txt
├── init.sql
└── templates
    ├── register.html
    └── student.html
```

## Database Schema (`init.sql`)

```sql
CREATE DATABASE IF NOT EXISTS studentsdb;
USE studentsdb;

CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  course VARCHAR(100) NOT NULL,
  address VARCHAR(100) NOT NULL,
  phone VARCHAR(100) NOT NULL,
  contact VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---
# Appending next Content Soon


