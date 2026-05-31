"""
student.py  —  Student Management with:
  • Real-time per-field validation (red border + inline error BESIDE the hint)
  • Autocomplete on text fields (suggestions from previously saved students)
  • Compact single-row layout — all fields visible without scrolling
"""

from tkinter import *
from tkinter import ttk, messagebox
import cv2, os, re
import db
from validators import validate_student, validate_student_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data")
IMG_DIR   = os.path.join(BASE_DIR, "images")
os.makedirs(DATA_DIR, exist_ok=True)
HAAR = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")

BG       = "#f0f4f8"
HDR_BG   = "#0f3460"
ERR_FG   = "#c0392b"
ENTRY_OK = "#ffffff"
ENTRY_ERR= "#ffc8c8"


def _load_bg(widget, filename, w, h):
    try:
        from PIL import Image, ImageTk
        path = os.path.join(IMG_DIR, filename)
        if not os.path.exists(path): return None
        img = Image.open(path).resize((w, h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = Label(widget, image=photo, bd=0)
        lbl.image = photo
        lbl.place(x=0, y=0, relwidth=1, relheight=1)
        return lbl
    except Exception:
        return None


# ── Autocomplete Entry ────────────────────────────────────────────────────────
class AutocompleteEntry(Entry):
    def __init__(self, master, suggestions_source, textvariable=None, **kwargs):
        super().__init__(master, textvariable=textvariable, **kwargs)
        self._src    = suggestions_source
        self._var    = textvariable
        self._lb_win = None
        self._lb     = None
        self.bind("<KeyRelease>", self._on_key)
        self.bind("<FocusOut>",   lambda e: self.after(150, self._hide))
        self.bind("<Escape>",     lambda e: self._hide())
        self.bind("<Down>",       self._focus_lb)

    def _on_key(self, event):
        if event.keysym in ("Return","Tab","Escape","Up","Down"): return
        typed = (self._var.get() if self._var else self.get()).strip().lower()
        if not typed: self._hide(); return
        matches = [s for s in self._src() if typed in s.lower()]
        if matches: self._show(matches)
        else: self._hide()

    def _show(self, matches):
        self._hide()
        x, y = self.winfo_rootx(), self.winfo_rooty() + self.winfo_height()
        w = self.winfo_width()
        self._lb_win = Toplevel(self)
        self._lb_win.wm_overrideredirect(True)
        self._lb_win.wm_geometry(f"{w}x{min(110, len(matches)*22)}+{x}+{y}")
        self._lb_win.attributes("-topmost", True)
        sb = Scrollbar(self._lb_win, orient=VERTICAL)
        self._lb = Listbox(self._lb_win, yscrollcommand=sb.set,
                           font=("Arial", 10), selectbackground="#3498db",
                           selectforeground="white", relief=SOLID, bd=1)
        sb.config(command=self._lb.yview)
        sb.pack(side=RIGHT, fill=Y)
        self._lb.pack(side=LEFT, fill=BOTH, expand=True)
        for m in matches: self._lb.insert(END, m)
        self._lb.bind("<ButtonRelease-1>", self._pick)
        self._lb.bind("<Return>", self._pick)

    def _pick(self, event=None):
        if not self._lb: return
        sel = self._lb.curselection()
        if sel:
            val = self._lb.get(sel[0])
            if self._var: self._var.set(val)
            else: self.delete(0, END); self.insert(0, val)
        self._hide(); self.focus_set()

    def _focus_lb(self, event=None):
        if self._lb: self._lb.focus_set(); self._lb.selection_set(0)

    def _hide(self):
        if self._lb_win:
            try: self._lb_win.destroy()
            except: pass
            self._lb_win = self._lb = None


# ── FieldRow: ONE grid row, error label replaces hint when invalid ────────────
class FieldRow:
    def __init__(self, parent, row, label_text, var, hint,
                 validator=None, suggestions_source=None):
        self.var       = var
        self.validator = validator
        self._hint     = hint

        Label(parent, text=label_text, font=("Arial", 10), bg=BG, fg="#333",
              anchor=W).grid(row=row, column=0, sticky=W, padx=(10,4), pady=2)

        if suggestions_source:
            self.entry = AutocompleteEntry(
                parent, suggestions_source, textvariable=var,
                font=("Arial", 10), width=22, relief=SOLID, bd=1, bg=ENTRY_OK)
        else:
            self.entry = Entry(parent, textvariable=var, font=("Arial", 10),
                               width=22, relief=SOLID, bd=1, bg=ENTRY_OK)
        self.entry.grid(row=row, column=1, padx=4, pady=2, sticky=W)

        # hint / error label — same column 2, toggles text & colour
        self.info_lbl = Label(parent, text=hint, font=("Arial", 8),
                              bg=BG, fg="#999", anchor=W, width=22)
        self.info_lbl.grid(row=row, column=2, sticky=W, padx=2)

        self.entry.bind("<FocusOut>", self._check)

    def _check(self, event=None):
        if not self.validator: return
        val = self.var.get().strip()
        err = self.validator(val)
        if err:
            self.entry.config(bg=ENTRY_ERR)
            self.info_lbl.config(text=f"⚠ {err}", fg=ERR_FG)
        else:
            self.entry.config(bg=ENTRY_OK)
            self.info_lbl.config(text="✔ OK" if val else self._hint, fg="#27ae60" if val else "#999")

    def clear_error(self):
        self.entry.config(bg=ENTRY_OK)
        self.info_lbl.config(text=self._hint, fg="#999")

    def force_check(self):
        self._check()


# ── Student window ────────────────────────────────────────────────────────────
class Student:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x680+0+0")
        self.root.title("Student Management")
        self.root.configure(bg=BG)

        # StringVars
        self.var_std_id   = StringVar()
        self.var_std_name = StringVar()
        self.var_roll     = StringVar()
        self.var_dep      = StringVar()
        self.var_course   = StringVar()
        self.var_year     = StringVar()
        self.var_semester = StringVar()
        self.var_div      = StringVar()
        self.var_gender   = StringVar()
        self.var_dob      = StringVar()
        self.var_email    = StringVar()
        self.var_phone    = StringVar()
        self.var_address  = StringVar()
        self.var_teacher  = StringVar()
        self.var_photo    = StringVar(value="No")

        # Title bar
        title_frame = Frame(self.root, bg=HDR_BG, height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)
        _load_bg(title_frame, "student_banner.jpg", 1200, 60)
        Label(title_frame, text="STUDENT MANAGEMENT SYSTEM",
              font=("Arial", 18, "bold"), bg=HDR_BG, fg="white"
              ).pack(side=LEFT, padx=20, pady=12)

        body = Frame(self.root, bg=BG)
        body.pack(fill=BOTH, expand=True, padx=10, pady=8)

        # ── LEFT: form ────────────────────────────────────────────────────────
        left = LabelFrame(body, text="Student Details",
                          font=("Arial", 11, "bold"), bg=BG, fg=HDR_BG,
                          relief=GROOVE, bd=2)
        left.pack(side=LEFT, fill=BOTH, padx=5)

        # Autocomplete sources
        def names():     return list({s["name"]    for s in db.get_all_students()})
        def teachers():  return list({s["teacher"] for s in db.get_all_students() if s["teacher"]})
        def addresses(): return list({s["address"] for s in db.get_all_students() if s["address"]})
        def emails():    return list({s["email"]   for s in db.get_all_students() if s["email"]})
        def phones():    return list({s["phone"]   for s in db.get_all_students() if s["phone"]})

        # Validators
        def _req_id(v):
            if not v: return "Required"
            if not re.fullmatch(r"[A-Za-z0-9_\-]{2,30}", v): return "Letters/digits/- only, 2-30 chars"
            return None
        def _req_name(v):
            if not v: return "Required"
            if not re.fullmatch(r"[A-Za-z ]{2,60}", v): return "Letters & spaces only"
            return None
        def _req_roll(v):
            if not v: return "Required"
            if not v.isdigit(): return "Digits only (e.g. 12)"
            if not (1 <= int(v) <= 9999): return "Must be 1–9999"
            return None
        def _opt_email(v):
            if not v: return None
            if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", v): return "Invalid email format"
            return None
        def _opt_phone(v):
            if not v: return None
            if not re.fullmatch(r"\+?\d{7,15}", v): return "7–15 digits, optional +"
            return None
        def _opt_dob(v):
            if not v: return None
            from datetime import datetime
            try:
                dt = datetime.strptime(v, "%d/%m/%Y")
                if dt > datetime.now(): return "Cannot be in the future"
                if not (5 <= (datetime.now()-dt).days//365 <= 100): return "Age must be 5–100"
            except ValueError: return "Use DD/MM/YYYY"
            return None

        # Build field rows (all on consecutive grid rows — compact)
        field_defs = [
            ("Student ID *", self.var_std_id,   "e.g. 2022-CE-5",      _req_id,   None),
            ("Name *",       self.var_std_name,  "letters & spaces",    _req_name, names),
            ("Roll No. *",   self.var_roll,      "whole number",        _req_roll, None),
            ("Email",        self.var_email,     "user@example.com",    _opt_email,emails),
            ("Phone",        self.var_phone,     "03001234567",         _opt_phone,phones),
            ("DOB",          self.var_dob,       "DD/MM/YYYY",          _opt_dob,  None),
            ("Address",      self.var_address,   "Street / City",       None,      addresses),
            ("Teacher",      self.var_teacher,   "Class teacher name",  None,      teachers),
        ]

        self._field_rows = []
        for r, (lbl, var, hint, validator, src) in enumerate(field_defs):
            fr = FieldRow(left, r, lbl, var, hint, validator, src)
            self._field_rows.append(fr)

        # Dropdowns (continue from row 8)
        combos = [
            ("Department", self.var_dep,
             ["Computer Engineering","Electrical Engineering","Computer Science"]),
            ("Course",     self.var_course,
             ["Circuit Analysis","Calculus","Programming Fundamentals"]),
            ("Year",       self.var_year,      ["2022-23","2023-24","2024-25"]),
            ("Semester",   self.var_semester,  ["1st","2nd","3rd","4th","5th","6th","7th","8th"]),
            ("Division",   self.var_div,       ["A","B","C"]),
            ("Gender",     self.var_gender,    ["Male","Female","Other"]),
        ]
        for i, (label, var, values) in enumerate(combos):
            r = len(field_defs) + i
            Label(left, text=label, font=("Arial", 10), bg=BG, fg="#333"
                  ).grid(row=r, column=0, sticky=W, padx=(10,4), pady=2)
            cb = ttk.Combobox(left, textvariable=var, values=values,
                              font=("Arial", 10), state="readonly", width=21)
            cb.grid(row=r, column=1, padx=4, pady=2, sticky=W)
            if values: cb.current(0)

        # Photo radio
        pr = len(field_defs) + len(combos)
        Label(left, text="Photo Sample", font=("Arial", 10), bg=BG, fg="#333"
              ).grid(row=pr, column=0, sticky=W, padx=(10,4), pady=2)
        rf = Frame(left, bg=BG)
        rf.grid(row=pr, column=1, sticky=W, padx=4)
        Radiobutton(rf, text="Yes", variable=self.var_photo, value="Yes", bg=BG,
                    font=("Arial", 10)).pack(side=LEFT)
        Radiobutton(rf, text="No",  variable=self.var_photo, value="No",  bg=BG,
                    font=("Arial", 10)).pack(side=LEFT, padx=8)

        # Buttons
        btn_frame = Frame(left, bg=BG)
        btn_frame.grid(row=pr+1, column=0, columnspan=3, pady=8)
        btn_cfg = dict(font=("Arial", 10, "bold"), fg="white",
                       relief=FLAT, width=12, pady=4, cursor="hand2")
        Button(btn_frame, text="💾 Save",       bg="#2ecc71", command=self.add_data,       **btn_cfg).grid(row=0, column=0, padx=3)
        Button(btn_frame, text="✏ Update",      bg="#3498db", command=self.update_data,    **btn_cfg).grid(row=0, column=1, padx=3)
        Button(btn_frame, text="🗑 Delete",     bg="#e74c3c", command=self.delete_data,    **btn_cfg).grid(row=0, column=2, padx=3)
        Button(btn_frame, text="🔄 Reset",      bg="#95a5a6", command=self.reset_data,     **btn_cfg).grid(row=1, column=0, padx=3, pady=3)
        Button(btn_frame, text="📷 Take Photo", bg="#9b59b6", command=self.generate_dataset,**btn_cfg).grid(row=1, column=1, padx=3, pady=3)

        # ── RIGHT: table ──────────────────────────────────────────────────────
        right = LabelFrame(body, text="Students Record",
                           font=("Arial", 11, "bold"), bg=BG, fg=HDR_BG,
                           relief=GROOVE, bd=2)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

        cols = ("ID","Name","Roll","Dep","Course","Year","Sem","Gender","Photo")
        sx = ttk.Scrollbar(right, orient=HORIZONTAL)
        sy = ttk.Scrollbar(right, orient=VERTICAL)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=24)
        self.table = ttk.Treeview(right, columns=cols, show="headings",
                                  xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.config(command=self.table.xview)
        sy.config(command=self.table.yview)
        sx.pack(side=BOTTOM, fill=X)
        sy.pack(side=RIGHT,  fill=Y)
        self.table.pack(fill=BOTH, expand=True)

        for col in cols:
            self.table.heading(col, text=col)
            self.table.column(col, width=100, anchor=CENTER)

        self.table.tag_configure("odd",  background="#eaf4fb")
        self.table.tag_configure("even", background="#ffffff")
        self.table.bind("<ButtonRelease-1>", self.get_cursor)
        self.fetch_data()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _collect(self):
        return {
            "student_id":   self.var_std_id.get().strip(),
            "name":         self.var_std_name.get().strip(),
            "roll":         self.var_roll.get().strip(),
            "dep":          self.var_dep.get(),
            "course":       self.var_course.get(),
            "year":         self.var_year.get(),
            "semester":     self.var_semester.get(),
            "division":     self.var_div.get(),
            "gender":       self.var_gender.get(),
            "dob":          self.var_dob.get().strip(),
            "email":        self.var_email.get().strip(),
            "phone":        self.var_phone.get().strip(),
            "address":      self.var_address.get().strip(),
            "teacher":      self.var_teacher.get().strip(),
            "photo_sample": self.var_photo.get(),
        }

    def _validate_all(self):
        for fr in self._field_rows:
            fr.force_check()
        d = self._collect()
        errors = validate_student(d)
        if errors:
            messagebox.showerror("Fix these fields",
                                 "\n\n".join(f"• {e}" for e in errors))
            return None
        return d

    def fetch_data(self):
        self.table.delete(*self.table.get_children())
        for idx, s in enumerate(db.get_all_students()):
            tag = "odd" if idx % 2 else "even"
            self.table.insert("", END, tags=(tag,), values=(
                s["student_id"], s["name"], s["roll"], s["dep"],
                s["course"], s["year"], s["semester"],
                s["gender"], s["photo_sample"]
            ))

    def get_cursor(self, event=""):
        row = self.table.focus()
        if not row: return
        vals = self.table.item(row)["values"]
        if not vals: return
        s = db.get_student_by_id(str(vals[0]))
        if not s: return
        self.var_std_id.set(s["student_id"]); self.var_std_name.set(s["name"])
        self.var_roll.set(s["roll"]);         self.var_dep.set(s["dep"])
        self.var_course.set(s["course"]);     self.var_year.set(s["year"])
        self.var_semester.set(s["semester"]); self.var_div.set(s["division"])
        self.var_gender.set(s["gender"]);     self.var_dob.set(s["dob"])
        self.var_email.set(s["email"]);       self.var_phone.set(s["phone"])
        self.var_address.set(s["address"]);   self.var_teacher.set(s["teacher"])
        self.var_photo.set(s["photo_sample"])
        for fr in self._field_rows: fr.clear_error()

    def add_data(self):
        data = self._validate_all()
        if not data: return
        try:
            db.add_student(data)
            self.fetch_data()
            messagebox.showinfo("Success", "Student added successfully.")
            self.reset_data()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_data(self):
        data = self._validate_all()
        if not data: return
        try:
            db.update_student(data["student_id"], data)
            self.fetch_data()
            messagebox.showinfo("Success", "Student updated.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_data(self):
        sid = self.var_std_id.get().strip()
        if not sid:
            messagebox.showerror("Error", "Select a student first."); return
        if messagebox.askyesno("Delete", "Delete this student?"):
            db.delete_student(sid)
            self.fetch_data(); self.reset_data()
            messagebox.showinfo("Deleted", "Student deleted.")

    def reset_data(self):
        for var in [self.var_std_id, self.var_std_name, self.var_roll,
                    self.var_email, self.var_phone, self.var_dob,
                    self.var_address, self.var_teacher]:
            var.set("")
        self.var_photo.set("No")
        for fr in self._field_rows: fr.clear_error()

    def generate_dataset(self):
        sid = self.var_std_id.get().strip()
        err = validate_student_id(sid)
        if err: messagebox.showerror("Invalid Student ID", err); return
        if not os.path.exists(HAAR):
            messagebox.showerror("Missing File",
                "haarcascade_frontalface_default.xml not found."); return
        student = db.get_student_by_id(sid)
        if not student:
            messagebox.showerror("Not Found",
                f"Student ID '{sid}' not found. Please save first."); return

        face_classifier = cv2.CascadeClassifier(HAAR)
        cap = cv2.VideoCapture(0); img_id = 0
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Could not open camera."); return
        messagebox.showinfo("Info",
            f"Camera opening for: {student['name']} (ID: {sid})\nPress ENTER or wait for 100 photos.")
        while True:
            ret, frame = cap.read()
            if not ret: break
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                img_id += 1
                face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
                cv2.imwrite(os.path.join(DATA_DIR, f"user{sid}.{img_id}.jpg"), face)
                cv2.putText(frame, f"ID:{sid} {img_id}/100",
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.imshow("Capturing — press ENTER to stop", frame)
            if cv2.waitKey(1) == 13 or img_id >= 100: break
        cap.release(); cv2.destroyAllWindows()

        if img_id > 0:
            student["photo_sample"] = "Yes"
            db.update_student(sid, student); self.fetch_data()
            messagebox.showinfo("Done",
                f"Captured {img_id} samples for {student['name']}.\nNow train the model.")
        else:
            messagebox.showwarning("No Faces", "No faces captured. Try again.")


if __name__ == "__main__":
    root = Tk()
    Student(root)
    root.mainloop()