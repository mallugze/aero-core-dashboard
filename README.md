# 🚀 AeroCore – AI-Powered Telemetry Monitoring System

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Django](https://img.shields.io/badge/Django-Framework-green?logo=django)
![Machine Learning](https://img.shields.io/badge/ML-TensorFlow%20%7C%20Keras-orange)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Frontend](https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JS-blue)
![Status](https://img.shields.io/badge/Project-Active-success)

---

## 📸 Project Preview

### 🏠 Landing Page
![Landing Page](images/landing.png)

### 📊 Diagnostic Dashboard
![Dashboard](images/dashboard.png)

### 🔐 Admin Access Control Panel
![Admin Panel](images/admin.png)

### 🌍 Fleet / Telemetry Overview
![Fleet Overview](images/fleet.png)



---

## 📌 Overview

AeroCore is a full-stack AI-powered web application designed to simulate real-world aerospace telemetry monitoring systems.
It enables engineers to upload engine telemetry data and receive predictive diagnostics, including Remaining Useful Life (RUL) and system health metrics.

---

## 🧠 Key Features

### 🔐 Secure Authentication & Approval Workflow

* Custom Django authentication system
* Admin-controlled user approval
* SMTP email notifications (approval/rejection)

---

### 🤖 Predictive Engine

* ML-based `predict()` function
* Calculates RUL, vibration, fuel flow

---

### 📊 Interactive Dashboard

* Tailwind CSS glassmorphism UI
* Real-time feedback & dynamic rendering

---

### 📄 PDF Reporting

* Generated using ReportLab
* Downloadable technical diagnostic reports

---



---

## 🛠️ Tech Stack

* Python, Django
* TensorFlow / Keras
* NumPy, Pandas
* HTML, Tailwind CSS, JavaScript
* SQLite
* ReportLab
* SMTP Email

---

## 🚀 Workflow

1. User requests access
2. Admin approves via backend
3. User uploads telemetry data
4. ML processes data
5. Results displayed
6. PDF report generated

---

## 🔐 Security

* CSRF protection
* Session-based authentication
* Admin approval workflow

---

## 🚀 Future Scope

* REST API (Django REST Framework)
* Real-time streaming (IoT)
* Cloud deployment

## 🐳 Docker Deployment

Run the entire application in a container with a single command:

### 1. Using Docker Compose (Recommended)
```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Build and launch the container
docker compose up --build
```
Access the application dashboard at `http://localhost:8000`.

### 2. Using Docker CLI
```bash
# Build the Docker image
docker build -t aerocore:latest .

# Run the container
docker run -p 8000:8000 --env-file .env.example aerocore:latest
```

---

## 👨‍💻 Author

Developed by **Mallikarjun**

---

## ⭐ Show Your Support

Give a ⭐ if you like this project!
