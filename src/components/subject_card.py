import streamlit as st

def subject_card(name, code, section, stats=None, footer_callback=None, card_key=None):
    html = f"""
        
        <div style="background: #ffb8c7;  border-left: 8px solid #EB459E; padding: 25px; border-radius:20px; border: 1px solid black; margin-bottom: 20px; !important">
        
       <h3 style="margin:0; color: #1e293b; font-size: 1.5rem ">{name}</h3>
       <p style="color:#64748b; margin:10px 0;">Code : <span style="background:#E0E3FF; color:#5865F2" padding: 2x 8px; border-radius: 5px; >{code} </span> | Section : {section}</p>
    
        """
    if stats:
        html += """
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
         """
        for icon, label, value in stats:
            html += f'<div style="background: #EB459E10; padding:5px 12px; border-radius:12px; font-size:0.9rem">{icon} <b>{value}</b> {label} </div>'


        html += "</div>"


    st.markdown(html, unsafe_allow_html=True)    

    
    if footer_callback:
        button_key = f"footer_btn_{card_key}" if card_key else None
        if st.button("❌ Unenroll", type="secondary", use_container_width=True, key=button_key):
            footer_callback()  