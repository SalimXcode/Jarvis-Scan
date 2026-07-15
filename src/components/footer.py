import streamlit as st



def footer_home():
    logo_url = "https://avatars.githubusercontent.com/u/206970561?s=400&u=b1127e0d9e4b29258a1769125ecd3dbca61af508&v=4"

    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:white;"> Created by🖤SalimXcode</p>
        <img src='{logo_url}' style='max-height:25px' />
        </div>

        """, unsafe_allow_html=True)