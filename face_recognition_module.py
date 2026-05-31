from tkinter import *
from tkinter import messagebox
import cv2
import os
import json
import db

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "trained_model")
MODEL_PATH = os.path.join(MODEL_DIR, "recognizer.xml")
MAP_PATH   = os.path.join(MODEL_DIR, "id_map.json")
HAAR       = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")


class Face_Recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x270+400+250")
        self.root.title("Face Recognition")
        self.root.configure(bg="#1a1a2e")

        Label(self.root, text="Face Recognition",
              font=("Arial", 20, "bold"), bg="#1a1a2e", fg="white"
              ).pack(pady=30)

        self.info = Label(
            self.root,
            text="Press the button to start the camera.",
            font=("Arial", 11), bg="#1a1a2e", fg="#aaa"
        )
        self.info.pack()

        self.stat = Label(
            self.root, text="",
            font=("Arial", 10), bg="#1a1a2e", fg="#00d4ff"
        )
        self.stat.pack(pady=4)

        Button(
            self.root, text="📷  Start Face Recognition",
            command=self.face_recog,
            font=("Arial", 13, "bold"),
            bg="#e94560", fg="white", relief=FLAT,
            padx=15, pady=8, cursor="hand2"
        ).pack(pady=15)

    # ------------------------------------------------------------------
    def face_recog(self):
        # ── pre-checks ────────────────────────────────────────────────
        if not os.path.exists(MODEL_PATH):
            messagebox.showerror(
                "Model Missing",
                "No trained model found.\nPlease train the dataset first."
            )
            return

        if not os.path.exists(MAP_PATH):
            messagebox.showerror(
                "Map Missing",
                "id_map.json not found.\nPlease re-train the dataset."
            )
            return

        if not os.path.exists(HAAR):
            messagebox.showerror(
                "Missing File",
                "haarcascade_frontalface_default.xml not found in project folder."
            )
            return

        # ── load model + ID map ───────────────────────────────────────
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read(MODEL_PATH)

        with open(MAP_PATH) as f:
            raw_map = json.load(f)

        # flip:  integer_label → original string ID  e.g. 1 → "2022-CE-5"
        int_to_str = {int(v): k for k, v in raw_map.items()}

        face_cascade = cv2.CascadeClassifier(HAAR)
        cap          = cv2.VideoCapture(0)

        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Could not open camera.")
            return

        self.info.config(text="Camera running… press ENTER to stop.")
        self.stat.config(text="")
        self.root.update()

        # ── main loop ─────────────────────────────────────────────────
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                roi               = gray[y:y+h, x:x+w]
                numeric_id, conf  = clf.predict(roi)
                confidence_pct    = int(100 * (1 - conf / 300))

                # reverse-map integer label → original student ID string
                original_id = int_to_str.get(numeric_id, None)
                student     = db.get_student_by_id(original_id) \
                              if original_id else None

                if confidence_pct > 77 and student:
                    name  = student["name"]
                    roll  = student["roll"]
                    dep   = student["dep"]
                    color = (0, 255, 0)

                    marked = db.mark_attendance(original_id, roll, name, dep)
                    label  = "✔ Marked!" if marked else "Already marked"

                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    for i, txt in enumerate([
                        f"Name: {name}",
                        f"Roll: {roll}",
                        f"Dept: {dep}",
                        label
                    ]):
                        cv2.putText(
                            frame, txt,
                            (x, y - 70 + i*18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2
                        )

                    self.stat.config(
                        text=f"Last recognised: {name} ({roll})"
                    )
                    self.root.update()

                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(
                        frame, "Unknown Face",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                    )

            cv2.imshow("Face Recognition  —  press ENTER to stop", frame)
            if cv2.waitKey(1) == 13:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.info.config(text="Camera closed.")
        self.stat.config(text="")


if __name__ == "__main__":
    root = Tk()
    Face_Recognition(root)
    root.mainloop()
