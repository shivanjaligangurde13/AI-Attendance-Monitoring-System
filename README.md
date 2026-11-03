# SnapClass – AI-Powered Attendance Monitoring System

**SnapClass** is an AI-powered attendance management platform designed to simplify and automate classroom attendance using facial recognition and voice recognition technologies.

The application provides dedicated portals for students and teachers, enabling automated attendance tracking, subject management, student enrollment, and attendance record monitoring through a centralized platform.

Instead of relying entirely on manual attendance, SnapClass uses AI-based biometric identification to make the attendance process more convenient and efficient.

---

## 🚀 Key Features

### 1. AI-Based Facial Recognition
- Captures student facial data during registration.
- Generates facial embeddings using Dlib.
- Uses a Support Vector Machine (SVM) classifier for student identification.
- Supports real-time face-based student login.
- Detects multiple faces in classroom images.
- Automatically identifies enrolled students from classroom photographs.

### 2. Voice-Based Attendance
- Supports optional voice enrollment during student registration.
- Extracts voice embeddings using Resemblyzer.
- Processes audio recordings for speaker identification.
- Matches voice embeddings against registered student profiles.
- Provides an alternative attendance mechanism through voice recognition.

### 3. Student Portal
- Face-based student authentication.
- Student registration with facial and optional voice enrollment.
- View enrolled subjects.
- Enroll in subjects using shared enrollment codes.
- View subject-wise attendance statistics.
- Unenroll from subjects.

### 4. Teacher Portal
- Teacher registration and authentication.
- Create and manage subjects.
- Generate and share subject enrollment codes.
- Upload classroom photographs for AI-based attendance detection.
- Use voice-based attendance.
- Review attendance results before recording them.
- View historical attendance records.

### 5. Attendance Management
- Automated identification of present and absent students.
- Subject-wise attendance tracking.
- Timestamp-based attendance records.
- Centralized storage and retrieval of attendance information.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend / Application Framework | Streamlit |
| Face Recognition | Dlib, Face Recognition Models |
| Machine Learning | Scikit-learn, SVM |
| Voice Recognition | Resemblyzer |
| Audio Processing | Librosa |
| Image Processing | Pillow, NumPy |
| Data Processing | Pandas |
| Database / Backend Services | Supabase |
| Authentication Support | Bcrypt |
| QR Code Generation | Segno |
| Version Control | Git, GitHub |

---

## 🧠 How It Works

### Facial Recognition Workflow

1. **Student Registration:** A student captures their photograph through the application.
2. **Feature Extraction:** The system detects facial landmarks and generates a 128-dimensional facial embedding using Dlib.
3. **Model Training:** Facial embeddings of registered students are used to train an SVM classifier.
4. **Face Detection:** When a student logs in or a teacher uploads classroom photographs, the system detects faces.
5. **Student Identification:** Extracted facial embeddings are compared against registered student data.
6. **Attendance Processing:** Identified students are mapped to their respective subject enrollment records.
7. **Attendance Recording:** Attendance results are prepared and stored with timestamps.

### Voice Recognition Workflow

1. Students can optionally register their voice during profile creation.
2. The recorded audio is processed and converted into a voice embedding using Resemblyzer.
3. During voice attendance, audio is processed to extract speaker embeddings.
4. The extracted embeddings are compared with registered voice profiles.
5. Identified students are matched with their enrollment records for attendance processing.

---

## 🏗️ Project Architecture

The application follows a modular architecture that separates the user interface, business logic, AI processing pipelines, and database operations.

```text
SnapClass/
│
├── app.py
│
├── src/
│   ├── components/
│   │   ├── header.py
│   │   ├── footer.py
│   │   ├── subject_card.py
│   │   ├── dialog_enroll.py
│   │   ├── dialog_create_subject.py
│   │   ├── dialog_add_photo.py
│   │   ├── dialog_attendance_result.py
│   │   └── ...
│   │
│   ├── database/
│   │   ├── config.py
│   │   └── db.py
│   │
│   ├── pipelines/
│   │   ├── face_pipeline.py
│   │   └── voice_pipeline.py
│   │
│   ├── screens/
│   │   ├── home_screen.py
│   │   ├── student_screen.py
│   │   └── teacher_screen.py
│   │
│   └── ui/
│       └── base_layout.py
│
├── .streamlit/
│   └── secrets.toml
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

Follow these steps to run SnapClass locally.

### Prerequisites

- Python installed on your system.
- Git installed.
- A Supabase account and configured database.
- Required environment credentials.

### 1. Clone the Repository

```bash
git clone https://github.com/shivanjaligangurde13/AI-Attendance-Monitoring-System.git

cd AI-Attendance-Monitoring-System
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase Credentials

Create a file named `secrets.toml` inside the `.streamlit` directory.

```toml
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_api_key"
```

Replace the placeholder values with your Supabase project credentials.

**Important:** Never commit your actual API keys or credentials to GitHub. Keep `secrets.toml` excluded through `.gitignore`.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser.

---

## 🗄️ Database Integration

SnapClass uses Supabase as its backend database service.

The database manages information related to:

- Student profiles and biometric embeddings.
- Teacher profiles and authentication.
- Subjects and subject enrollment.
- Student-subject relationships.
- Attendance records and timestamps.

The application uses Supabase client operations to create, retrieve, and update application data.

---

## 🔐 Security and Privacy Considerations

- Teacher authentication is supported through password-based login.
- Password hashing is implemented using Bcrypt.
- Supabase credentials are configured through Streamlit secrets.
- Facial and voice embeddings are stored for biometric identification.

**Privacy consideration:** Biometric information is sensitive personal data. Appropriate consent, access controls, secure storage, and data deletion mechanisms should be implemented before deploying this system in a real educational environment.

---

## 🔮 Future Enhancements

- Improve recognition accuracy under different lighting and environmental conditions.
- Introduce liveness detection to reduce spoofing attempts.
- Implement advanced attendance analytics and visual reports.
- Add role-based access controls and enhanced security.
- Introduce cloud deployment and scalable infrastructure.
- Develop a responsive interface for mobile devices.
- Add automated notifications for attendance updates.

---

## 👩‍💻 Developer

**Shivanjali Gangurde**

Computer Engineering Student | AI/ML & Generative AI Enthusiast

- GitHub: [@shivanjaligangurde13](https://github.com/shivanjaligangurde13)

---

## 📌 Project Objective

The objective of SnapClass is to demonstrate how Artificial Intelligence, Machine Learning, Computer Vision, and Voice Processing can be integrated into a practical application to automate traditional attendance management workflows.

**SnapClass – Making Attendance Smarter, Faster, and More Efficient.**
