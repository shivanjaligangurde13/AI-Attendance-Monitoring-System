import streamlit as st
from src.ui.base_layout import style_bg_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exists, create_teacher, teacher_login
from src.database.db import enroll_student_to_subject, uneroll_student_to_subject
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.components.dialog_enroll import enroll_dialog
from src.pipelines.voice_pipeline import get_voice_embedding
from PIL import Image
from src.database.db import get_all_students, create_student, get_student_subject, get_student_attendance
from src.components.subject_card import subject_card
import numpy as np
import time


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    col1, col2 = st.columns(2, vertical_alignment='center', gap='large')
    with col1:
        header_dashboard()
    with col2:
        st.subheader(f""" Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['login_type'] = None
            del st.session_state.student_data
            st.rerun()


    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll in Subject", type = 'primary', width= "stretch"):
            enroll_dialog()

    st.divider()
    with st.spinner('Loading your enrolled subjects...'):
        subjects = get_student_subject(student_id)
        logs= get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attendance": 0}

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attendance'] += 1

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(sid,{"total": 0, "attendance": 0})
        def unroll_button():
            if st.button("Unenroll from this course", type= 'tertiary', width= 'stretch'):
                uneroll_student_to_subject(student_id, sid)
                st.toast("Unenrolled successfully")
        
        with cols[i % 2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('🗓️', 'Total', stats['total']),
                    ('✅', "Attended", stats['attendance'])
                ],
                footer_callback= unroll_button
            )


    footer_dashboard()


def student_screen():

    style_base_layout()
    style_bg_dashboard()

    show_registration = False

    if (
        "student_data" in st.session_state
        and st.session_state.get("user_role") == "student"
    ):
        student_dashboard()
        return

    col1, col2 = st.columns(2, vertical_alignment='center', gap='large')

    with col1:
        header_dashboard()

    with col2:
        if st.button(
            "Go back to Home",
            type='secondary',
            key='loginbackbtn',
            shortcut="control+backspace"
        ):
            st.session_state['login_type'] = None
            st.rerun()

    st.space()
    st.space()

    st.header("Login using FaceID", text_alignment='center')
    st.space()

    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning....'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("Face not found")

            elif num_faces > 1:
                st.warning("Multiple faces found")

            else:
                if detected:
                    student_Id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next(
                        (s for s in all_students if s['student_id'] == student_Id),
                        None
                    )

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome back {student['name']}")
                        time.sleep(1)
                        st.rerun()

                else:
                    st.info('Face not recognized! You might be new student')
                    show_registration = True

    if show_registration:
        with st.container(border=True):
            st.header("Register New profile")
            new_name = st.text_input(
                "Emter your name",
                placeholder="Enter your name"
            )

            st.subheader('Optional: Voice enrollment')
            st.info("Enroll your for voice only attendance")

            audio_date = None

            try:
                audio_data = st.audio_input(
                    "Record a short phrase like I am present, My name is Riya"
                )
            except Exception:
                st.error("Audio Dat failed!")

            if st.button("Create Account", type='primary'):
                if new_name:
                    with st.spinner("Creating profile..."):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)

                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None

                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Hii {new_name}")
                                time.sleep(1)
                                st.rerun()

                        else:
                            st.error("Couldn't capture your facial recognition")

                else:
                    st.warning("Please enter your name")

    footer_dashboard()