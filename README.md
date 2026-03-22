# MediCare Clinic – FastAPI Project

## Project Overview

MediCare Clinic is a FastAPI-based backend system for managing doctors and medical appointments. The system allows users to view doctors, filter/search/sort doctors, book appointments, manage appointment status, and perform pagination on records.

This project demonstrates REST API development using FastAPI, Pydantic validation, query parameters, filtering, sorting, pagination, and business logic implementation.

---

## Features

### Doctor Management

* View all doctors
* View doctor by ID
* Add new doctor
* Update doctor fee and availability
* Delete doctor (only if no active appointments)
* Filter doctors
* Search doctors
* Sort doctors
* Pagination
* Browse doctors (filter + sort + pagination)
* Doctors summary statistics

### Appointment Management

* Create appointment
* Confirm appointment
* Cancel appointment
* Complete appointment
* View all appointments
* View active appointments
* View appointments by doctor
* Search appointments
* Sort appointments
* Pagination for appointments

### Fee Calculation Logic

Appointment fee is calculated based on:

* In-person → Full fee
* Video → 80% of fee
* Emergency → 150% of fee
* Senior Citizen → Additional 15% discount after other calculations

---

## Technologies Used

* Python
* FastAPI
* Pydantic
* Uvicorn
* REST API
* Swagger UI (Automatic API Documentation)

---

## Project Structure

```
project/
│
├── main.py
├── README.md
└── requirements.txt
```

---

## Installation & Setup

1. Install dependencies:

```
pip install fastapi uvicorn
```

2. Run the server:

```
uvicorn main:app --reload
```

3. Open Swagger documentation:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Root

| Method | Endpoint | Description     |
| ------ | -------- | --------------- |
| GET    | /        | Welcome message |

### Doctors

| Method | Endpoint             |
| ------ | -------------------- |
| GET    | /doctors             |
| GET    | /doctors/{doctor_id} |
| GET    | /doctors/summary     |
| GET    | /doctors/filter      |
| GET    | /doctors/search      |
| GET    | /doctors/sort        |
| GET    | /doctors/page        |
| GET    | /doctors/browse      |
| POST   | /doctors             |
| PUT    | /doctors/{doctor_id} |
| DELETE | /doctors/{doctor_id} |

### Appointments

| Method | Endpoint                            |
| ------ | ----------------------------------- |
| GET    | /appointments                       |
| GET    | /appointments/active                |
| GET    | /appointments/by-doctor/{doctor_id} |
| GET    | /appointments/search                |
| GET    | /appointments/sort                  |
| GET    | /appointments/page                  |
| POST   | /appointments                       |
| POST   | /appointments/{id}/confirm          |
| POST   | /appointments/{id}/cancel           |
| POST   | /appointments/{id}/complete         |

---

## Example Appointment Request

```
POST /appointments
```

```json
{
  "patient_name": "Rahul",
  "doctor_id": 1,
  "date": "2026-04-10",
  "reason": "Fever and cold",
  "appointment_type": "video",
  "senior_citizen": true
}
```

---

## Learning Outcomes

This project demonstrates:

* REST API design
* CRUD operations
* Query parameters
* Filtering logic
* Sorting logic
* Pagination
* Business logic implementation
* Data validation using Pydantic
* FastAPI routing
* API testing using Swagger

---

## Future Improvements

* Database integration (SQLite/MySQL/PostgreSQL)
* User authentication (JWT)
* Admin dashboard
* Email notifications
* Payment integration
* Frontend (React / HTML / Bootstrap)

---

## Author
Shreya Sutar
MediCare Clinic FastAPI Project
