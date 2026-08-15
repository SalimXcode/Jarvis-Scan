import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.components.auto_enroll_dailog import auto_enroll_dailog

if "login_type" not in st.session_state:
    st.session_state.login_type = None

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

login_type = st.session_state.get("login_type")

if login_type is None:
    home_screen()

elif login_type == "teacher":
    teacher_screen()

elif login_type == "student":
    student_screen()


join_code = st.query_params.get('join-code')
if join_code:
    if st.session_state.login_type != 'student':
        st.session_state.login_type = 'student'
        st.rerun()
    if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
        auto_enroll_dailog(join_code)  