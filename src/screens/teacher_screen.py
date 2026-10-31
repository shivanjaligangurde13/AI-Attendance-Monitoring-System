import streamlit as st
from src.ui.base_layout import style_bg_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.database.db import check_teacher_exists, create_teacher, teacher_login, create_subject, get_teacher_subject, get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
import numpy as np
from src.database.config import supabase
from src.pipelines.face_pipeline import predict_attendance
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_result import attendance_result_dialog
from src.components.voice_attendance_dialog import voice_attendance_dialog

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
  col1, col2 = st.columns(2, vertical_alignment='center', gap='large')
  with col1:
    header_dashboard()
  with col2:
    st.subheader(f""" Welcome, {teacher_data['name']} """)
    if st.button("Logout", type='secondary', key='loginbackbtn',shortcut="control+backspace"):
          st.session_state['login_type'] = None
          del st.session_state.teacher_data
          st.rerun()


  st.space()

  if "current_teacher_state" not in st.session_state:
    st.session_state.current_teacher_state = 'take_attendance'
  tab1, tab2, tab3 = st.columns(3)

  with tab1:
    type1 = "primary" if st.session_state.current_teacher_state =='take_attendance' else "tertiary"
    if st.button('Take Attendance',type = type1, width='stretch', icon=':material/ar_on_you:'):
      st.session_state.current_teacher_state = 'take_attendance'
      st.rerun()

  with tab2:
    type2 = "primary" if st.session_state.current_teacher_state == 'manage_subjects' else "tertiary"
    if st.button('Manage Subjects', type= type2,width='stretch', icon=':material/book_ribbon:'):
      st.session_state.current_teacher_state = 'manage_subjects'
      st.rerun()

  with tab3:
    type3 = "primary" if st.session_state.current_teacher_state == 'attendance_records' else "tertiary"
    if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
      st.session_state.current_teacher_state = 'attendance_records'
      st.rerun()


  st.divider()

  if st.session_state.current_teacher_state == "take_attendance":
    teacher_tab_take_attendance()

  if st.session_state.current_teacher_state == "manage_subjects":
    teacher_tab_manage_subjects()

  if st.session_state.current_teacher_state == "attendance_records":
    teacher_tab_attendance_records()

  footer_dashboard()

  
# TAB: TAKE ATTENDANCE:
def teacher_tab_take_attendance():
  teacher_id = st.session_state.teacher_data['teacher_id']
  st.header("Take AI attendance")

  if 'attendance_images' not in st.session_state:
    st.session_state.attendance_images =[]

  subjects = get_teacher_subject(teacher_id)

  if not subjects:
    st.warning("You haven't created any subjects yet! Please create one to begin")
    return 

  subject_options = {
    f"{s['name']} - {s['subject_id']}": s['subject_id']
    for s in subjects
  }

  col1, col2 = st.columns([3,1], vertical_alignment='bottom')

  with col1:
    selected_subject_label = st.selectbox('Select subject', options = list(subject_options.keys()))

  with col2:
    if st.button("Add photos", type = "primary", icon = ":material/imagesmode:", width = 'stretch'):
      add_photos_dialog()

  selected_subject_id = subject_options[selected_subject_label]

  if st.session_state.attendance_images:
    st.header("Added photos")
    gallery_cols = st.columns(4)

    for idx, img in enumerate(st.session_state.attendance_images):
      with gallery_cols[idx%4]:
        st.image(img,width='stretch', caption=f'Photo{idx+1}' )

  c1,c2,c3 = st.columns(3)
  has_photos = bool(st.session_state.attendance_images)

  with c1:
    if st.button("Clear all photos", width='stretch', type = "tertiary", icon = ":material/delete:", disabled= not has_photos):
      st.session_state.attendance_images = []
      st.rerun()

  with c2:
    if st.button("Run face analysis", width='stretch', type = "secondary", icon = ":material/analytics:", disabled=not has_photos):
      with st.spinner("Deep scanning classroom photos...."):
        all_detected_id = {}

        for idx, img in enumerate(st.session_state.attendance_images):
          img_np = np.array(img.convert('RGB'))

          detected, _, _ = predict_attendance(img_np)


          if detected:
            for sid in detected.keys():
              student_id = int(sid)

              all_detected_id.setdefault(student_id,[]).append(f"Photo {idx+1}")

        enrolled_res = supabase.table("subject_students").select("*, students(*)").eq('subject_id', selected_subject_id).execute()

        enrolled_students = enrolled_res.data
        if not enrolled_students:
          st.warning("No students enrolled in this course")

        else:
          results, attendance_to_log = [], []

          current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

          for node in enrolled_students:
            student = node['students']
            sources = all_detected_id.get(int(student['student_id']), [])
            is_present = len(sources) >0

            results.append({
              "Name": student['name'],
              "ID": student['student_id'],
              "Source": ",".join(sources) if is_present else "-",
              "Status": " ✅Present" if is_present else "❌ Absent"
            }
            )

            attendance_to_log.append({
              'student_id': student['student_id'],
              'subject_id': selected_subject_id,
              "timestamp": current_timestamp,
              "is_present": bool(is_present)
            })

          attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

  with c3:
    if st.button("Use Voice Attendance", type = "primary", width='stretch', icon = ":material/mic:"):
      voice_attendance_dialog(selected_subject_id)


        




# TAB: MANAGE SUBJECTS:
def teacher_tab_manage_subjects():
  teacher_id = st.session_state.teacher_data['teacher_id']
  col1, col2 = st.columns(2)

  with col1:
    st.header('Manage Subjects')
  with col2:
    if st.button('Create New Subject', width='stretch'):
      create_subject_dialog(teacher_id)


  #LIST ALL SUBJECT
  subjects = get_teacher_subject(teacher_id)
  if subjects:
    for sub in subjects:
      stats = [
        ("👥", "Students", sub['total_students']),
        ("⏰", "Classes", sub['total_classes'])
      ]

      def share_btn():
        if st.button(f"Share Code: {sub['name']}", key =f"share_{sub['subject_code']}", icon= ":material/share:"):
          share_subject_dialog(sub['name'], sub['subject_code'])
        st.space()

      subject_card(
        name = sub['name'],
        code = sub['subject_code'],
        section = sub['section'],
        stats = stats,
        footer_callback = share_btn
      )
  else:
    st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")









#TAB: ATTENDANCE RECORDS

def teacher_tab_attendance_records():
  st.header("Attendance records")

  teacher_id = st.session_state.teacher_data['teacher_id']

  records = get_attendance_for_teacher(teacher_id)
  if not records:
    return

  data = []

  for r in records:
    ts = r.get('timestamp')

    data.append({
      "ts_group":ts.split(".")[0] if ts else None,
      "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p ") if ts else "N'A",
      "Subject":r['subjects']['name'],
      "Subject Code":r['subjects']['subject_code'],
      "is_present":bool(r.get('is_present', False))
    })

  df = pd.DataFrame(data)
  summary = (
    df.groupby(['ts_group', 'Time', 'Subject','Subject Code']).agg(
      Present_Count = ('is_present', 'sum'),
      Total_Count = ('is_present','count')
    ).reset_index()
  )

  summary['Attendance Stats'] = (
    "✅"+ summary['Present_Count'].astype(str) + " /"+ summary['Total_Count'].astype(str) + 'Students'
  )

  display_df = (summary.sort_values(by = 'ts_group', ascending=False)[['Time','Subject','Subject Code', 'Attendance Stats']])

  st.dataframe(display_df, width='stretch', hide_index = True)




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