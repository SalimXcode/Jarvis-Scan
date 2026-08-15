import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embeddings
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import numpy as np
from PIL import Image
from src.components.enroll_dailog import enroll_dailog
from src.components.subject_card import subject_card
import time


def student_dashboard():
    student_data = st.session_state["student_data"]
    student_id = st.session_state.student_data['student_id']
    
    c1, c2 = st.columns(2, gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if st.button(
            "Logout",
            type="secondary",
            key="loginbckbttn1",
            shortcut="control+backspace",
        ):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data 
            st.rerun()

    st.space()
    c1, c2 = st.columns(2)
    with c1:
        st.header("You Enrolled for subjects")
    with c2:
        if st.button("Enroll in subject", type="primary", width="stretch"):
            enroll_dailog()

    st.divider()

    with st.spinner("Loading your enroll subjects..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)
        
        stats_map = {}
        for log in logs:
            sid = log['subject_id'] 
            if sid not in stats_map:
                stats_map[sid] = {'total': 0, 'attended': 0}
            
            stats_map[sid]['total'] += 1
            if log.get('is_present', False):  # FIX: is_present check
                stats_map[sid]['attended'] += 1 

    cols = st.columns(2)
    
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        
        stats = stats_map.get(sid, {"total": 0, "attended": 0})
        
        # FIX: Stats ko tuple list mein convert karo
        stats_list = [
            ('📅', 'Total', stats['total']),
            ('✅', 'Attended', stats['attended'])
        ]
        
        # FIX: Unique key for each card
        card_key = f"card_{sid}_{student_id}"
        
        # FIX: Callback function define karo
        def unenroll_callback(subject_id=sid, student_id=student_id):
            try:
                unenroll_student_to_subject(student_id, subject_id)
                st.toast("Successfully unenrolled! 🎉")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to unenroll: {e}")
        
        with cols[i % 2]:
            # FIX: Subject card ko sahi parameters do
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats_list,
                footer_callback=unenroll_callback,  # FIX: Function pass karo, call nahi
                card_key=card_key
            )
    
    
    footer_dashboard()

def student_screen():
    show_registration = False
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return   

    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbckbttn11",
            shortcut="control+backspace",
        ):
            st.session_state["login_type"] = None
            st.rerun()
    
    st.header("Login Using FaceID", text_alignment="center")
    st.space()
    st.space()
    st.space()

    photo_source = st.camera_input("Position your face in the center")
    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("Ai is Scanning..."):
            detected, all_ids, face_num = predict_attendance(img)

            if face_num == 0:
                st.warning("Face Not Found")
            elif face_num > 1:
                st.warning("Multiple Faces Found")
            else:
                if detected:
                    detected_id = list(detected.keys())[0]
                    all_students = get_all_students()   
                    student = next((s for s in all_students if s["student_id"] == detected_id), None)   

                    if student:
                        st.session_state.is_logged_in = True 
                        st.session_state.user_role = "student"
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognized! You might be new student!")
                    show_registration = True
        
        if show_registration:
            with st.container(border=True):
                st.header("Register New Profile")
                new_name = st.text_input("Enter Your name", placeholder="E.g. Salim Kha")
 
                st.subheader("Optional: Voice Enrollment")
                st.info("Enroll your voice for only attendance")

                audio_data = None
                try:
                    audio_data = st.audio_input("Record short phrase Like: i am present, My name is Salim Kha")
                except Exception as e:
                    st.error("Audio Failed")

                if st.button("Create Account", type="primary"):
                    if new_name:
                        with st.spinner("Creating Profile...."):
                            img = np.array(Image.open(photo_source))
                            encodings = get_face_embeddings(img)
                            if encodings:
                                face_emb = encodings[0].tolist()
                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embeddings(audio_data.read())

                                response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)     
                                if response_data:
                                    train_classifier()
                                    st.session_state.is_logged_in = True 
                                    st.session_state.user_role = "student"
                                    st.session_state.student_data = response_data
                                    st.toast(f"Profile Created Hi! {new_name}")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("Couldn't capture your facial features or registration")
                    else:
                        st.warning("Please enter your name")
    
    footer_dashboard()