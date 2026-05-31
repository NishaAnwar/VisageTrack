from tkinter import *
from tkinter import messagebox
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR  = os.path.join(BASE_DIR, "images")

# ── image loader helper ───────────────────────────────────────────────────────
def _load_img(filename, width=None, height=None):
    """Return a PhotoImage or None if Pillow/file not available."""
    try:
        from PIL import Image, ImageTk
        path = os.path.join(IMG_DIR, filename)
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        if width and height:
            img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# ── lazy module loaders ───────────────────────────────────────────────────────
def load_student():
    from student import Student
    return Student

def load_train():
    from train import Train
    return Train

def load_face_recognition():
    from face_recognition_module import Face_Recognition
    return Face_Recognition

def load_attendance():
    from attendance import Attendance1
    return Attendance1

def load_help():
    from help_module import Help
    return Help

def load_developer():
    from developer import Developer
    return Developer


# ─────────────────────────────────────────────────────────────────────────────
class Face_Recognition_System:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x720+0+0")
        self.root.title("Face Recognition Based Attendance System")
        self.root.configure(bg="#1a1a2e")
        self._icon_refs = []   # keep PhotoImage references alive

        # ── header ────────────────────────────────────────────────────────────
        header = Frame(self.root, bg="#16213e", height=90)
        header.pack(fill=X)
        header.pack_propagate(False)

        # Optional header background: images/main_banner.jpg  (1200×90)
        logo_img = _load_img("main_logo.png", 100, 70)
        if logo_img:
            self._icon_refs.append(logo_img)
            Label(header, image=logo_img, bg="#16213e").pack(side=LEFT, padx=10, pady=15)

        Label(
            header,
            text="FACE RECOGNITION BASED ATTENDANCE SYSTEM",
            font=("Arial", 22, "bold"),
            bg="#16213e", fg="white"
        ).pack(side=LEFT, padx=10, pady=25)

        self.clock_lbl = Label(header, font=("Arial", 14, "bold"),
                               bg="#16213e", fg="#00d4ff")
        self.clock_lbl.pack(side=RIGHT, padx=20)
        self._tick()

        # ── optional full-width banner image ──────────────────────────────────
        banner = _load_img("main_banner.jpg", 1200, 160)
        if banner:
            self._icon_refs.append(banner)
            Label(self.root, image=banner, bd=0, bg="#1a1a2e").pack(fill=X)

        # ── button grid ───────────────────────────────────────────────────────
        grid = Frame(self.root, bg="#1a1a2e")
        grid.pack(expand=True, fill=BOTH, padx=40, pady=20)

        #  (label, icon_file, loader_fn)
        buttons = [
            ("  Student Details",  "icon_student.png",    self.student_details),
            ("  Face Detector",    "icon_camera.png",     self.face_data),
            ("  Attendance",       "icon_attendance.png", self.attendance_data),
            ("  Train Data",       "icon_train__.png",      self.train_data),
            ("  Help",             "icon_help.png",       self.help_data),
            ("  Developer",        "icon_dev.png",        self.develop_data),
        ]

        for i, (text, icon_file, cmd) in enumerate(buttons):
            r, c = divmod(i, 3)
            cell = Frame(grid, bg="#1a1a2e")
            cell.grid(row=r, column=c, padx=15, pady=12, sticky="nsew")

            icon_img = _load_img(icon_file, 64, 64)
            btn = Button(
                cell, text=text, command=cmd,
                font=("Arial", 13, "bold"),
                bg="#0f3460", fg="white",
                activebackground="#e94560", activeforeground="white",
                relief=FLAT, cursor="hand2",
                width=22, height=4,
                compound=TOP if icon_img else NONE,
                image=icon_img if icon_img else "",
            )
            if icon_img:
                self._icon_refs.append(icon_img)
            btn.pack(fill=BOTH, expand=True)

        for c in range(3):
            grid.columnconfigure(c, weight=1)
        for r in range(2):
            grid.rowconfigure(r, weight=1)

        # ── exit ──────────────────────────────────────────────────────────────
        Button(
            self.root, text="EXIT", command=self.i_exit,
            font=("Arial", 12, "bold"),
            bg="#e94560", fg="white", relief=FLAT, cursor="hand2"
        ).pack(pady=8, ipadx=20, ipady=5)

    # ── clock ─────────────────────────────────────────────────────────────────
    def _tick(self):
        self.clock_lbl.config(text=datetime.now().strftime("%H:%M:%S  %d/%m/%Y"))
        self.root.after(1000, self._tick)

    # ── navigation ────────────────────────────────────────────────────────────
    def _open(self, loader):
        win = Toplevel(self.root)
        loader()(win)

    def student_details(self):  self._open(load_student)
    def train_data(self):       self._open(load_train)
    def face_data(self):        self._open(load_face_recognition)
    def attendance_data(self):  self._open(load_attendance)
    def help_data(self):        self._open(load_help)
    def develop_data(self):     self._open(load_developer)

    def i_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    app = Face_Recognition_System(root)
    root.mainloop()
