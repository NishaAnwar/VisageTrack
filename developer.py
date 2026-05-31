from tkinter import *


class Developer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x400+300+200")
        self.root.title("Developer")
        self.root.configure(bg="#1a1a2e")

        Label(self.root, text="DEVELOPER",
              font=("Arial", 22, "bold"), bg="#1a1a2e", fg="white"
              ).pack(pady=20)

        text = (
            "Face Recognition Based Attendance System\n\n"
            "Developed by:\n"
            "  • Nisha Anwar\n"
            "This system uses OpenCV's LBPH face recognizer\n"
            "and Haar Cascade classifier for real-time face detection.\n\n"
            "Student data and attendance records are stored\n"
            "locally using CSV files.\n\n"
                   )

        Label(self.root, text=text,
              font=("Arial", 13), bg="#1a1a2e", fg="#cccccc",
              justify=LEFT
              ).pack(padx=40, pady=10)


class Help:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x450+300+200")
        self.root.title("Help")
        self.root.configure(bg="#1a1a2e")

        Label(self.root, text="HOW TO USE",
              font=("Arial", 20, "bold"), bg="#1a1a2e", fg="white"
              ).pack(pady=20)

        steps = (
            "STEP 1 — Student Details\n"
            "   → Add each student with their ID, name, roll number, etc.\n"
            "   → Click 'Take Photo' to capture 100 face samples.\n\n"
            "STEP 2 — Train Data\n"
            "   → Click 'Train Now' to train the face recognition model.\n"
            "   → Wait until training is complete before using recognition.\n\n"
            "STEP 3 — Face Detector\n"
            "   → Click 'Start Face Recognition' to open the camera.\n"
            "   → Recognized students are automatically marked Present.\n\n"
            "STEP 4 — Attendance\n"
            "   → View, search, import, or export attendance records.\n\n"
            "NOTE:\n"
            "   → haarcascade_frontalface_default.xml must be in the\n"
            "     project folder.\n"
            "   → Download it from OpenCV GitHub if missing."
        )

        Label(self.root, text=steps,
              font=("Arial", 11), bg="#1a1a2e", fg="#cccccc",
              justify=LEFT
              ).pack(padx=30, pady=5)


if __name__ == "__main__":
    root = Tk()
    Developer(root)
    root.mainloop()
