import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.create_dailogue_subject import create_dialog_subject
from src.components.subject_card import subject_card
from src.components.share_subject_dailog import share_subject_dailog
from src.components.add_photos_dailog import add_photos_dailog
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
)


def teacher_dashboard():
    teacher_data = st.session_state["teacher_data"]
    c1, c2 = st.columns(2, gap="xxlarge")

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}")
        if st.button(
            "Logout",
            type="secondary",
            key="mn"
        ):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data 
            st.rerun()




    st.space()
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3 = st.columns(3)   

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',  type=type1, width='stretch', icon=':material/ar_on_you:', key='takeattnd'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()


    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:', key='mngsub'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()


    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records', type=type3, width='stretch', icon=':material/cards_stack:', key='attnrcrd'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()                


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()



    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()

    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()    


    footer_dashboard()   

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("You haven't created subject please create")
        return
    subject_option = {f"{s['name']} -- {s['subject_code']}": s["subject_id"] for s in subjects}

    col1 , col2 = st.columns([3,1])
    with col1:
        select_subject_label = st.selectbox("Select Subjects", options=list(subject_option.keys()))

    with col2:
        if st.button("🌄Add Photo", type="primary", icon=":material/photo_prints:", width='stretch', key='addphoto'):
            add_photos_dailog() 

    select_subject_id = subject_option(select_subject_label)

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:'):
                st.session_state.attendance_images = []
                st.rerun()

        # with c2:
        #     has_photos = bool(st.session_state.attendance_images)     
        #     if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:'):
        #         with st.spinner('Deep scanning classroom photos ... '):
        #             all_detected_id = {}

        #             for idx, img in enumerate(st.session_state.attendance_images) :
        #                 img_np = np.array(img.convert('RGB'))
        #                 detected ,_, = predict_attendance(img_np)

        #             if detected:
        #                 for sid in detected.keys():
        #                     student_id = int(sid)

        #                     all_detected_id.setdefault(student_id, []).append(f"Photo {idx+1}")

        #             enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()   
                

             


    

def teacher_tab_manage_subjects():
  teacher_id = st.session_state.teacher_data["teacher_id"]
  col1, col2 = st.columns(2)

  with col1:
      st.header("Manage Subjects")
  with col2:
      if st.button("Create Subject", width="stretch"):
          create_dialog_subject(teacher_id)  

  subjects = get_teacher_subjects(teacher_id)

  if subjects:
      for sub in subjects:
          stats = [
              ("👥", "Students", sub["total_students"]),
              ("🕰️", "Classes", sub["total_classes"]),
          ]     

      def share_btn():
            if st.button(f"Share Code: {sub['name']}", width= "content", key=f"Share_{sub["subject_code"]}", icon=":material/share:"):
                share_subject_dailog(sub['name'], sub['subject_code'])  
                st.space()            


      subject_card(
        name = sub ['name' ],
        code = sub['subject_code'],
        section = sub['section'],
        stats=stats,
        footer_callback = share_btn  
        )   
 
  else:
      st.info("NO SUBJECT FOUND: CREATE ONE ABOVE")






def teacher_tab_attendance_records():
    st.header("Attendance records")          
    





def login_teacher(username, password):
    if not username or not password:
        return False

    teacher = teacher_login(username, password)

    if teacher:
        st.session_state["user_role"] = "teacher"
        st.session_state["teacher_data"] = teacher
        st.session_state["is_logged_in"] = True
        return True

    return False


def teacher_screen_login():
    c1, c2 = st.columns(2, gap="xxlarge")

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbckbttn2",
            shortcut="control+backspace",
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Login Using Password", text_alignment="center")
    st.space()
    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter Username",
        placeholder="Salim Kha"
    )

    teacher_pass = st.text_input(
        "Enter Password",
        type="password",
        placeholder="Enter Password"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button(
            "Login",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch",
            key='login'
        ):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back!", icon="✅")

                import time
                time.sleep(1)

                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button(
            "Register Instead",
            icon=":material/passkey:",
            shortcut="control+enter",
            type="primary",
            width="stretch",
            key='register'
        ):
            st.session_state["teacher_login_type"] = "register"
            st.rerun()

    footer_dashboard()


def register_teacher(
    teacher_username,
    teacher_name,
    teacher_pass,
    teacher_pass_confirm,
):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"

    if check_teacher_exists(teacher_username):
        return False, "Username already taken"

    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(
            teacher_username,
            teacher_pass,
            teacher_name,
        )
        return True, "Successfully Created! Login now"

    except Exception as e:
        return False, f"Unexpected Error: {e}"


def teacher_screen_register():
    c1, c2 = st.columns(2, gap="xxlarge")

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbckbttn3",
            shortcut="control+backspace",
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Register Your Teacher Profile", text_alignment="center")

    st.space()
    st.space()

    teacher_name = st.text_input(
        "Enter Name",
        placeholder="Salim Kha",
    )

    teacher_username = st.text_input(
        "Enter Username",
        placeholder="Salimkha786",
    )

    teacher_pass = st.text_input(
        "Enter Password",
        type="password",
        placeholder="Enter Password",
    )

    teacher_pass_confirm = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm Password",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button(
            "Login Instead",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch",
            key='lgn'
        ):
            st.session_state["teacher_login_type"] = "login"
            st.rerun()

    with btnc2:
        if st.button(
            "Register Now",
            icon=":material/passkey:",
            shortcut="control+enter",
            type="primary",
            width="stretch",
            key='rgtr'
        ):
            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm,
            )

            if success:
                st.success(message)

                import time
                time.sleep(2)

                st.session_state["teacher_login_type"] = "login"
                st.rerun()

            else:
                st.error(message)

    footer_dashboard()


def teacher_screen():
    style_base_layout()
    style_background_dashboard()

    if "teacher_data" in st.session_state:
        teacher_dashboard()

    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        teacher_screen_login()

    elif st.session_state.teacher_login_type== "register":
        teacher_screen_register()


teacher_screen()