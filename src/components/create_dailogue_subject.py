import streamlit as st

from src.database.db import create_subject


@st.dialog("Create New Subjects")
def create_dialog_subject(teahcer_id):
    st.write("Enter the detail new subjects")

    sub_id = st.text_input("Subject Code", placeholder="AL101")
    sub_name = st.text_input("Subject Name", placeholder="AI&ML")
    sub_section = st.text_input("Section", placeholder="A")

    if st.button("Create Subject Now", type="primary", width="stretch"):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teahcer_id)
                st.toast("Subject Created Successfully")
                st.rerun()
            except Exception as e:
                st.error( f"error {str(e)}")

        else:
            st.warning("Please fill the all section")            