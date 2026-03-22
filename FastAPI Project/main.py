from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
from math import ceil

app = FastAPI()

# Root
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


# Doctors Data
doctors = [
    {"id": 1, "name": "Dr. Smith", "specialization": "Cardiologist", "fee": 800, "experience_years": 15, "is_available": True},
    {"id": 2, "name": "Dr. Patel", "specialization": "Dermatologist", "fee": 500, "experience_years": 8, "is_available": True},
    {"id": 3, "name": "Dr. Khan", "specialization": "Pediatrician", "fee": 600, "experience_years": 10, "is_available": False},
    {"id": 4, "name": "Dr. Mehta", "specialization": "General", "fee": 300, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Sharma", "specialization": "Cardiologist", "fee": 900, "experience_years": 18, "is_available": True},
    {"id": 6, "name": "Dr. Roy", "specialization": "Dermatologist", "fee": 450, "experience_years": 6, "is_available": False},
]

appointments = []
appt_counter = 1


# ---------------- Helper Functions ----------------
def find_doctor(doctor_id):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    return None


def calculate_fee(base_fee, appointment_type, senior_citizen=False):
    original_fee = base_fee

    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    if senior_citizen:
        fee = fee * 0.85

    return round(original_fee), round(fee)


def filter_doctors_logic(specialization=None, max_fee=None, min_experience=None, is_available=None):
    filtered = doctors

    if specialization is not None:
        filtered = [d for d in filtered if d["specialization"].lower() == specialization.lower()]

    if max_fee is not None:
        filtered = [d for d in filtered if d["fee"] <= max_fee]

    if min_experience is not None:
        filtered = [d for d in filtered if d["experience_years"] >= min_experience]

    if is_available is not None:
        filtered = [d for d in filtered if d["is_available"] == is_available]

    return filtered


# ---------------- Models ----------------
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True


# ---------------- Doctor Routes ----------------
@app.get("/doctors")
def get_doctors():
    available = [d for d in doctors if d["is_available"]]
    return {
        "total": len(doctors),
        "available_count": len(available),
        "doctors": doctors
    }


@app.get("/doctors/summary")
def doctors_summary():
    most_exp = max(doctors, key=lambda x: x["experience_years"])
    cheapest = min(doctors, key=lambda x: x["fee"])

    spec_count = {}
    for d in doctors:
        spec_count[d["specialization"]] = spec_count.get(d["specialization"], 0) + 1

    return {
        "total_doctors": len(doctors),
        "available_doctors": len([d for d in doctors if d["is_available"]]),
        "most_experienced_doctor": most_exp["name"],
        "cheapest_fee": cheapest["fee"],
        "specialization_counts": spec_count
    }


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    return {"results": filter_doctors_logic(specialization, max_fee, min_experience, is_available)}


@app.post("/doctors", status_code=201)
def add_doctor(doc: NewDoctor):
    for d in doctors:
        if d["name"].lower() == doc.name.lower():
            raise HTTPException(status_code=400, detail="Doctor already exists")

    new_doc = doc.dict()
    new_doc["id"] = len(doctors) + 1
    doctors.append(new_doc)
    return new_doc


@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[int] = None, is_available: Optional[bool] = None):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if fee is not None:
        doctor["fee"] = fee
    if is_available is not None:
        doctor["is_available"] = is_available

    return doctor


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for appt in appointments:
        if appt["doctor_id"] == doctor_id and appt["status"] == "scheduled":
            raise HTTPException(status_code=400, detail="Doctor has active appointments")

    doctors.remove(doctor)
    return {"message": "Doctor deleted successfully"}


# ---------------- Appointment Routes ----------------
@app.get("/appointments")
def get_appointments():
    return {"total": len(appointments), "appointments": appointments}


@app.post("/appointments")
def create_appointment(request: AppointmentRequest):
    global appt_counter

    doctor = find_doctor(request.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doctor["is_available"]:
        raise HTTPException(status_code=400, detail="Doctor not available")

    original_fee, final_fee = calculate_fee(
        doctor["fee"], request.appointment_type, request.senior_citizen
    )

    appointment = {
        "appointment_id": appt_counter,
        "patient": request.patient_name,
        "doctor_id": doctor["id"],
        "doctor_name": doctor["name"],
        "date": request.date,
        "type": request.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    appt_counter += 1
    doctor["is_available"] = False

    return appointment


@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "confirmed"
            return appt
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "cancelled"
            doctor = find_doctor(appt["doctor_id"])
            if doctor:
                doctor["is_available"] = True
            return appt
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "completed"
            return appt
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.get("/appointments/active")
def active_appointments():
    active = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return active


@app.get("/appointments/by-doctor/{doctor_id}")
def appointments_by_doctor(doctor_id: int):
    return [a for a in appointments if a["doctor_id"] == doctor_id]


# ---------------- Search / Sort / Pagination Doctors ----------------
@app.get("/doctors/search")
def search_doctors(keyword: str):
    results = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]

    if not results:
        return {"message": "No doctors found"}

    return {"total_found": len(results), "results": results}


@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee"):
    if sort_by not in ["fee", "name", "experience_years"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    sorted_docs = sorted(doctors, key=lambda x: x[sort_by])
    return {"sorted_by": sort_by, "doctors": sorted_docs}


@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    total = len(doctors)
    total_pages = ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": doctors[start:end]
    }


# ---------------- Appointment Search / Sort / Pagination ----------------
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    return [
        a for a in appointments
        if patient_name.lower() in a["patient"].lower()
    ]


@app.get("/appointments/sort")
def sort_appointments(sort_by: str):
    if sort_by not in ["final_fee", "date"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    return sorted(appointments, key=lambda x: x[sort_by])


@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 3):
    total = len(appointments)
    total_pages = ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": appointments[start:end]
    }


# ---------------- Browse Doctors (Filter + Sort + Pagination) ----------------
@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = doctors

    if keyword:
        result = [
            d for d in result
            if keyword.lower() in d["name"].lower()
            or keyword.lower() in d["specialization"].lower()
        ]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    total_pages = ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "results": result[start:end]
    }
