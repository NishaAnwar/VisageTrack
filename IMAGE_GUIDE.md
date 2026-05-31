# 🖼️ Image Guide — Face Recognition Attendance System

All images go inside the **`images/`** folder in your project directory.

---

## 📌 Main Window (`main.py`)

### 1. Main Banner (optional wide header image)
- **Filename:** `images/main_banner.jpg`
- **Recommended size:** 1200 × 160 px
- **What it shows:** Below the header bar — a wide campus/technology banner
- **Download:** https://www.pexels.com/search/university%20campus%20technology/
  - Suggested search: "university campus technology banner"
  - Pick a landscape photo (wide). Free download on Pexels.

### 2. Main Logo (top-left corner)
- **Filename:** `images/main_logo.png`
- **Recommended size:** 60 × 60 px (square, transparent PNG)
- **Download:** https://www.flaticon.com/free-icons/face-recognition
  - Search "face recognition" → download PNG → resize to 60×60

### 3. Navigation Button Icons (optional, one per button)
Place these in `images/` to show an icon above each menu button:

| Filename                    | Button         | Free icon source                              |
|-----------------------------|----------------|-----------------------------------------------|
| `icon_student.png`          | Student Details| https://www.flaticon.com/search?word=student  |
| `icon_camera.png`           | Face Detector  | https://www.flaticon.com/search?word=camera   |
| `icon_attendance.png`       | Attendance     | https://www.flaticon.com/search?word=checklist|
| `icon_train.png`            | Train Data     | https://www.flaticon.com/search?word=training |
| `icon_help.png`             | Help           | https://www.flaticon.com/search?word=help     |
| `icon_dev.png`              | Developer      | https://www.flaticon.com/search?word=developer|

- **Recommended size:** 64 × 64 px PNG (with transparent background)
- All icons are **optional** — if missing, buttons still work fine with emoji text.

---

## 📌 Student Window (`student.py`)

### Student Banner (title bar background)
- **Filename:** `images/student_banner.jpg`
- **Recommended size:** 1100 × 70 px
- **What it shows:** Behind the "STUDENT MANAGEMENT SYSTEM" title
- **Download:** https://www.pexels.com/search/students%20classroom/
  - Pick a wide landscape photo of students. Resize to 1100×70 in any image editor.

---

## 📌 Attendance Window (`attendance.py`)

### Attendance Banner (title bar background)
- **Filename:** `images/attendance_banner.jpg`
- **Recommended size:** 1000 × 65 px
- **What it shows:** Behind the "ATTENDANCE MANAGEMENT SYSTEM" title
- **Download:** https://www.pexels.com/search/attendance%20register/
  - A clean blue/green wide photo works best.

---

## 🛠️ How to Resize Images

**Option A — Free online tool:**
- Go to https://www.iloveimg.com/resize-image
- Upload your image → set exact width & height → download

**Option B — Using Paint (Windows):**
1. Open image in Paint
2. Home → Resize → set pixels → uncheck "Maintain aspect ratio" → enter width & height
3. Save as JPG or PNG

---

## ✅ Quick Summary

| File path                        | Size (px)    | Required? | Used in         |
|----------------------------------|--------------|-----------|-----------------|
| `images/main_banner.jpg`         | 1200 × 160   | Optional  | Main window     |
| `images/main_logo.png`           | 60 × 60      | Optional  | Main window     |
| `images/icon_student.png`        | 64 × 64      | Optional  | Main window     |
| `images/icon_camera.png`         | 64 × 64      | Optional  | Main window     |
| `images/icon_attendance.png`     | 64 × 64      | Optional  | Main window     |
| `images/icon_train.png`          | 64 × 64      | Optional  | Main window     |
| `images/icon_help.png`           | 64 × 64      | Optional  | Main window     |
| `images/icon_dev.png`            | 64 × 64      | Optional  | Main window     |
| `images/student_banner.jpg`      | 1100 × 70    | Optional  | Student window  |
| `images/attendance_banner.jpg`   | 1000 × 65    | Optional  | Attendance window|

> All images are **optional** — the system works perfectly without them.
> If a file is missing, that section simply shows a plain colour background.
