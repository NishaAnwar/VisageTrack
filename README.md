# Face Recognition Based Attendance System

## Folder Structure
```
face_recognition_project/
│
├── main.py                          ← Run this to launch the app
├── db.py                            ← CSV-based data storage
├── student.py                       ← Student management
├── train.py                         ← Train face recognition model
├── face_recognition_module.py       ← Live face recognition + attendance marking
├── attendance.py                    ← View/export attendance records
├── developer.py                     ← Developer info + Help screen
├── help_module.py                   ← Help import helper
├── requirements.txt                 ← Python dependencies
│
├── haarcascade_frontalface_default.xml 
│
├── data/                            ← Face images stored here automatically
├── trained_model/                   ← recognizer.xml saved here after training
└── attendance_records/              ← students.csv and attendance.csv stored here
```

## Setup (one time)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Haar Cascade
Download `haarcascade_frontalface_default.xml` from:
https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml

Place it in the project root folder (same folder as main.py).

### 3. Run the app
```bash
python main.py
```

## How to Use

1. **Student Details** → Add students and capture their face photos
2. **Train Data** → Train the model on captured photos
3. **Face Detector** → Start camera; recognized students are marked Present automatically
4. **Attendance** → View records, search by name/roll, export to CSV

## No MySQL Required
All data is stored in simple CSV files inside `attendance_records/`.
- `students.csv` — student records
- `attendance.csv` — attendance log
