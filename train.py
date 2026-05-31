from tkinter import *
from tkinter import messagebox
import cv2
import os
import json
import numpy as np
from PIL import Image

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODEL_DIR  = os.path.join(BASE_DIR, "trained_model")
MODEL_PATH = os.path.join(MODEL_DIR, "recognizer.xml")
MAP_PATH   = os.path.join(MODEL_DIR, "id_map.json")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR,  exist_ok=True)


class Train:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x320+300+200")
        self.root.title("Train Face Data")
        self.root.configure(bg="#1a1a2e")

        Label(self.root, text="Train Face Dataset",
              font=("Arial", 20, "bold"), bg="#1a1a2e", fg="white"
              ).pack(pady=30)

        self.status = Label(
            self.root,
            text="Click the button to start training.",
            font=("Arial", 12), bg="#1a1a2e", fg="#aaa"
        )
        self.status.pack(pady=10)

        self.progress = Label(
            self.root, text="",
            font=("Arial", 11), bg="#1a1a2e", fg="#00d4ff"
        )
        self.progress.pack()

        Button(
            self.root, text="▶  Train Now",
            command=self.train_classifier,
            font=("Arial", 14, "bold"),
            bg="#e94560", fg="white", relief=FLAT,
            padx=20, pady=8, cursor="hand2"
        ).pack(pady=20)

    # ------------------------------------------------------------------
    def train_classifier(self):
        images = [f for f in os.listdir(DATA_DIR)
                  if f.lower().endswith(".jpg")]

        if not images:
            messagebox.showerror(
                "No Data",
                f"No face images found in:\n{DATA_DIR}\n\n"
                "Please capture student photos first."
            )
            return

        self.status.config(text="Training in progress… please wait.")
        self.root.update()

        faces  = []
        ids    = []
        id_map = {}   # "2022-CE-5"  →  1  (string ID → integer label)

        for filename in images:
            path = os.path.join(DATA_DIR, filename)
            try:
                # ── load image ────────────────────────────────────────
                img    = Image.open(path).convert("L")
                img_np = np.array(img, dtype=np.uint8)

                # ── parse filename  user2022-CE-5.7.jpg ───────────────
                # Everything after "user" up to the LAST two dots is the ID.
                # e.g.  "user2022-CE-5.7.jpg"
                #        strip "user"  →  "2022-CE-5.7.jpg"
                #        rsplit on "." twice  →  ["2022-CE-5", "7", "jpg"]
                name_no_ext = filename[:-4]          # drop ".jpg"
                raw         = name_no_ext[4:]        # drop "user"
                # the img counter is the last token after the final dot
                raw_id      = raw.rsplit(".", 1)[0]  # "2022-CE-5"

                # ── map string ID → integer for OpenCV ────────────────
                if raw_id not in id_map:
                    id_map[raw_id] = len(id_map) + 1
                numeric_id = id_map[raw_id]

                faces.append(img_np)
                ids.append(numeric_id)

            except Exception as e:
                print(f"Skipping {filename}: {e}")
                continue

            self.progress.config(text=f"Loaded {len(faces)} images…")
            self.root.update()

        if not faces:
            messagebox.showerror(
                "Error",
                "Could not load any face images.\n"
                "Check that filenames follow the format:\n"
                "  user<StudentID>.<number>.jpg"
            )
            return

        # ── train & save model ────────────────────────────────────────
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))
        recognizer.save(MODEL_PATH)

        # ── save id_map so face_recognition can reverse-look-up ───────
        with open(MAP_PATH, "w") as f:
            json.dump(id_map, f, indent=2)

        self.status.config(
            text=f"✅  Training complete!  {len(faces)} images, "
                 f"{len(id_map)} student(s)."
        )
        self.progress.config(text=f"Model saved → {MODEL_PATH}")
        messagebox.showinfo(
            "Done",
            f"Training complete!\n"
            f"{len(faces)} images processed\n"
            f"{len(id_map)} unique student(s) enrolled."
        )


if __name__ == "__main__":
    root = Tk()
    Train(root)
    root.mainloop()
