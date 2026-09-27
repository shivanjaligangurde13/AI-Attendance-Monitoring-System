import streamlit as st
from src.ui.base_layout import style_bg_dashboard, style_base_layout

def teacher_screen():
  st.header("Teacher screen")

  style_base_layout()

  style_bg_dashboard()