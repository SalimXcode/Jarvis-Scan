from src.database.confiq import supabase
import bcrypt
from datetime import date


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


# ==================== TEACHER ====================

def check_teacher_exists(username):
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0


def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data[0] if response.data else None


def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None


def get_teacher(teacher_id):
    response = supabase.table("teachers").select("*").eq("teacher_id", teacher_id).execute()
    return response.data[0] if response.data else None


# ==================== STUDENT ====================

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data


def get_student(student_id):
    response = supabase.table("students").select("*").eq("student_id", student_id).execute()
    return response.data[0] if response.data else None


def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {
        'name': new_name,
        'face_embedding': face_embedding,
        'voice_embedding': voice_embedding
    }
    response = supabase.table('students').insert(data).execute()
    return response.data[0] if response.data else None


def update_face_embedding(student_id, embedding):
    response = supabase.table("students").update({"face_embedding": embedding}).eq("student_id", student_id).execute()
    return response.data


def update_voice_embedding(student_id, embedding):
    response = supabase.table("students").update({"voice_embedding": embedding}).eq("student_id", student_id).execute()
    return response.data


# ==================== SUBJECT ====================

def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data[0] if response.data else None


def get_subject_by_code(subject_code):
    response = supabase.table("subjects").select("*").eq("subject_code", subject_code).execute()
    return response.data[0] if response.data else None


def get_subject(subject_id):
    response = supabase.table("subjects").select("*").eq("subject_id", subject_id).execute()
    return response.data[0] if response.data else None


def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select(
        "*, subject_students(count), attendance_logs(timestamp)"
    ).eq("teacher_id", teacher_id).execute()

    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get("subject_students") else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions
        sub.pop("subject_students", None)
        sub.pop("attendance_logs", None)

    return subjects


def delete_subject(subject_id):
    # Delete related records first
    supabase.table("subject_students").delete().eq("subject_id", subject_id).execute()
    supabase.table("attendance_logs").delete().eq("subject_id", subject_id).execute()
    response = supabase.table("subjects").delete().eq("subject_id", subject_id).execute()
    return response.data


# ==================== ENROLLMENT ====================

def enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response = supabase.table('subject_students').insert(data).execute()
    return response.data


def unenroll_student_to_subject(student_id, subject_id):
    response = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data


def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def get_subject_students(subject_id):
    response = supabase.table('subject_students').select('*, students(*)').eq('subject_id', subject_id).execute()
    return response.data


def is_student_enrolled(student_id, subject_id):
    response = supabase.table('subject_students').select("*").eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return len(response.data) > 0


# ==================== ATTENDANCE ====================

def mark_attendance(student_id, subject_id, method="face", status="present"):
    data = {
        "student_id": student_id,
        "subject_id": subject_id,
        "method": method,
        "status": status,
        "timestamp": "now()"
    }
    response = supabase.table("attendance_logs").insert(data).execute()
    return response.data


def has_attended_today(student_id, subject_id):
    today = date.today().isoformat()
    response = supabase.table("attendance_logs").select("*").eq("student_id", student_id).eq("subject_id", subject_id).gte("timestamp", today).execute()
    return len(response.data) > 0


def get_student_attendance(student_id):
    response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def get_subject_attendance(subject_id):
    response = supabase.table('attendance_logs').select('*, students(name)').eq('subject_id', subject_id).order("timestamp", desc=True).execute()
    return response.data


def get_today_attendance(subject_id):
    today = date.today().isoformat()
    response = supabase.table('attendance_logs').select('*, students(name)').eq('subject_id', subject_id).gte("timestamp", today).execute()
    return response.data