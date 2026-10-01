import streamlit as st
from src.ui.base_layout import style_bg_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exists, create_teacher, teacher_login
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from PIL import Image
from src.database.db import get_all_students, create_student
import numpy as np
import time


def student_dashboard():
    st.header("Dashboard Here")


def student_screen():

    style_base_layout()
    style_bg_dashboard()

    show_registration = False

    if (
        "session_data" in st.session_state
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
                        st.session_state.session_data = student
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
            st.info("Emroll your for voice only attendance")

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
                                st.session_state.session_data = response_data[0]
                                st.toast(f"Hii {new_name}")
                                time.sleep(1)
                                st.rerun()

                        else:
                            st.error("Couldn't capture your facial recognition")

                else:
                    st.warning("Please enter your name")

    footer_dashboard()