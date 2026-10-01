import streamlit as st
from src.ui.base_layout import style_bg_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exists, create_teacher, teacher_login

def teacher_screen():
  style_base_layout()
  style_bg_dashboard()

  if "teacher_data" in st.session_state:
    teacher_dashboard()
    return
  elif "teacher_login_state" not in st.session_state:
    st.session_state.teacher_login_state = "login"

  if st.session_state.teacher_login_state == "register":
      teacher_screen_register()
  else:
      teacher_screen_login()



# TEACHER DASHBOARD
def teacher_dashboard():
  teacher_data = st.session_state.teacher_data
  st.header(f""" Welcome, {teacher_data['name']} """)



# TEACHER LOGIN CHECKS

def login_teacher(teacher_username, teacher_pass):
  if not teacher_username or not teacher_pass:
    return False, "Username and password are required"

  teacher = teacher_login(teacher_username, teacher_pass)

  if teacher:
    st.session_state.user_role = 'teacher'
    st.session_state.teacher_data = teacher
    st.session_state.logged_in = True
    return True, "Login successful"
  return False, "Invalid username or password"

#TEACHER LOGIN SCREEN

def teacher_screen_login():
  col1, col2 = st.columns(2, vertical_alignment='center', gap='large')
  with col1:
    header_dashboard()
  with col2:
    if st.button("Go back to Home", type='secondary', key='loginbackbtn',shortcut="control+backspace"):
          st.session_state['login_type'] = None
          st.rerun()
  
  st.header("Login using password")
  st.space()
  st.space()
  teacher_username = st.text_input("Enter username", placeholder="@divyasharma")

  teacher_pass = st.text_input("Enter Password", placeholder="Enter your password", type="password")

  st.divider()
  btnc1, btnc2  = st.columns(2)

  with btnc1:
    if st.button("Login", icon=':material/passkey:', shortcut='control+enter', width="stretch"):
      success, message = login_teacher(teacher_username, teacher_pass)
      if success:
        st.toast("Welcome back!", icon= "👋")
        import time
        time.sleep(1)
        st.rerun()
      else:
        st.error(message)
      

  with btnc2:
    if st.button("Register Instead", icon=":material/passkey:",width="stretch",type="primary"):
      st.session_state.teacher_login_state = 'register'

  footer_dashboard()





# TEACHER REGISTER CHECKS

def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
  if not teacher_username or not teacher_name or not teacher_pass or not teacher_pass_confirm:
     return False, "All fields are required"
  if check_teacher_exists(teacher_username):
    return False, "Username already exist"
  if teacher_pass != teacher_pass_confirm:
    return False, "Password doesn't match"

  try:
    create_teacher(teacher_username, teacher_name,teacher_pass)
    return True, "Sucessfully Created! Login Now"
  except Exception as e:
     return False, "Unexpected Error Occurred!"





#TEACHER REGISTER SCREEN

def teacher_screen_register():
  col1, col2 = st.columns(2, vertical_alignment='center', gap='large')
  with col1:
    header_dashboard()
  with col2:
    if st.button("Go back to Home", type='secondary', key='loginbackbtn',shortcut="control+backspace"):
      st.session_state['login_type'] = None
      st.rerun()
  
  st.header("Register Teacher profile")
  st.space()
  st.space()
  teacher_username = st.text_input("Enter username", placeholder="@divyasharma")
  teacher_name = st.text_input("Enter Name", placeholder="Divya ")
  
  teacher_pass = st.text_input("Enter password", placeholder="Enter your password", type="password")

  teacher_pass_confirm = st.text_input("Confirm Password", placeholder="Confirm your password", type="password")

  st.divider()
  btnc1, btnc2  = st.columns(2)

  with btnc1:
    if st.button("Register", icon=':material/passkey:', shortcut='control+enter', width="stretch"):
      success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
      if success:
        st.success(message)
        import time
        time.sleep(2)
        st.session_state.teacher_login_state = "login"
      else:
       st.error(message)
  with btnc2:
    if st.button("Login Instead", icon=":material/passkey:",width="stretch",type="primary"):
       st.session_state.teacher_login_state = 'login'

  footer_dashboard()