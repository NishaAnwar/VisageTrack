from tkinter import *
from tkinter import ttk, messagebox, filedialog
import csv
import os
import db
from validators import validate_attendance_roll, validate_search_term

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR  = os.path.join(BASE_DIR, "images")


def _load_bg(widget, filename, w, h):
    try:
        from PIL import Image, ImageTk
        path = os.path.join(IMG_DIR, filename)
        if not os.path.exists(path):
            return None
        img = Image.open(path).resize((w, h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = Label(widget, image=photo, bd=0)
        lbl.image = photo
        lbl.place(x=0, y=0, relwidth=1, relheight=1)
        return lbl
    except Exception:
        return None


class Attendance1:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x620+50+50")
        self.root.title("Attendance Record")
        self.root.configure(bg="#f0f4f8")

        # ── title bar ────────────────────────────────────────────────────────
        title_frame = Frame(self.root, bg="#0f3460", height=65)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)
        _load_bg(title_frame, "attendance_banner_.jfif", 1300, 472)
        Label(title_frame, text="ATTENDANCE MANAGEMENT SYSTEM",
              font=("Arial", 18, "bold"), bg="#0f3460", fg="white"
              ).pack(side=LEFT, padx=20, pady=15)

        # ── search bar ───────────────────────────────────────────────────────
        sf = Frame(self.root, bg="#e8edf3", relief=GROOVE, bd=1)
        sf.pack(fill=X, padx=10, pady=6)

        Label(sf, text="Search by Name / Roll:",
              font=("Arial", 11), bg="#e8edf3").pack(side=LEFT, padx=8, pady=6)
        self.search_var = StringVar()
        Entry(sf, textvariable=self.search_var,
              font=("Arial", 11), width=25, relief=SOLID, bd=1
              ).pack(side=LEFT, padx=5, pady=6)
        Button(sf, text="🔍 Search", command=self.search,
               font=("Arial", 11), bg="#3498db", fg="white",
               relief=FLAT, padx=10, cursor="hand2").pack(side=LEFT, padx=4)
        Button(sf, text="↺ Show All", command=self.fetch_data,
               font=("Arial", 11), bg="#2ecc71", fg="white",
               relief=FLAT, padx=10, cursor="hand2").pack(side=LEFT, padx=4)

        # ── summary stats bar ────────────────────────────────────────────────
        self.stats_lbl = Label(self.root, text="",
                               font=("Arial", 10, "italic"),
                               bg="#f0f4f8", fg="#555")
        self.stats_lbl.pack(anchor=E, padx=14)

        # ── table ────────────────────────────────────────────────────────────
        tf = Frame(self.root, bg="#f0f4f8")
        tf.pack(fill=BOTH, expand=True, padx=10, pady=4)

        cols = ("ID", "Roll", "Name", "Department", "Time", "Date", "Status")
        sx = ttk.Scrollbar(tf, orient=HORIZONTAL)
        sy = ttk.Scrollbar(tf, orient=VERTICAL)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=24)
        self.table = ttk.Treeview(tf, columns=cols, show="headings",
                                  xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.config(command=self.table.xview)
        sy.config(command=self.table.yview)
        sx.pack(side=BOTTOM, fill=X)
        sy.pack(side=RIGHT,  fill=Y)
        self.table.pack(fill=BOTH, expand=True)

        widths = [60, 80, 160, 180, 90, 110, 90]
        for col, w in zip(cols, widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=w, anchor=CENTER)

        self.table.tag_configure("present", background="#d5f5e3")
        self.table.tag_configure("absent",  background="#fadbd8")
        self.table.tag_configure("odd",     background="#eaf4fb")
        self.table.bind("<ButtonRelease-1>", self.get_cursor)

        # ── buttons ──────────────────────────────────────────────────────────
        bf = Frame(self.root, bg="#f0f4f8")
        bf.pack(pady=8)

        btn_cfg = dict(font=("Arial", 11, "bold"), fg="white",
                       relief=FLAT, padx=14, pady=6, cursor="hand2")
        Button(bf, text="📥 Import CSV", command=self.import_csv,
               bg="#9b59b6", **btn_cfg).grid(row=0, column=0, padx=8)
        Button(bf, text="📤 Export CSV", command=self.export_csv,
               bg="#e67e22", **btn_cfg).grid(row=0, column=1, padx=8)
        Button(bf, text="🗑 Delete Record", command=self.delete_record,
               bg="#e74c3c", **btn_cfg).grid(row=0, column=2, padx=8)

        self.fetch_data()

    # ── data ops ─────────────────────────────────────────────────────────────
    def fetch_data(self):
        self.table.delete(*self.table.get_children())
        records = db.get_all_attendance()
        present = sum(1 for r in records if r.get("status","").lower() == "present")
        for idx, r in enumerate(records):
            status = r.get("status", "")
            tag = "present" if status.lower() == "present" else "absent"
            self.table.insert("", END, tags=(tag,), values=(
                r["attendance_id"], r["roll"], r["name"],
                r["dep"], r["time"], r["date"], status
            ))
        total = len(records)
        self.stats_lbl.config(
            text=f"Total: {total}  |  Present: {present}  |  Absent: {total - present}"
        )

    def search(self):
        term = self.search_var.get().strip()
        if not term:
            self.fetch_data()
            return
        err = validate_search_term(term)
        if err:
            messagebox.showerror("Invalid Search", err)
            return
        term_lower = term.lower()
        self.table.delete(*self.table.get_children())
        found = 0
        for r in db.get_all_attendance():
            if term_lower in r["name"].lower() or term_lower in r["roll"].lower():
                status = r.get("status", "")
                tag = "present" if status.lower() == "present" else "absent"
                self.table.insert("", END, tags=(tag,), values=(
                    r["attendance_id"], r["roll"], r["name"],
                    r["dep"], r["time"], r["date"], status
                ))
                found += 1
        if found == 0:
            messagebox.showinfo("No Results", f"No records found for '{term}'.")

    def get_cursor(self, event=""):
        pass  # read-only view

    def delete_record(self):
        row = self.table.focus()
        if not row:
            messagebox.showerror("Error", "Select a record first.")
            return
        vals = self.table.item(row)["values"]
        if messagebox.askyesno("Delete", f"Delete attendance record ID {vals[0]}?"):
            records = [r for r in db.get_all_attendance()
                       if str(r["attendance_id"]) != str(vals[0])]
            with open(db.ATTENDANCE_FILE, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=db.ATTENDANCE_FIELDS)
                w.writeheader()
                w.writerows(records)
            self.fetch_data()

    def import_csv(self):
        path = filedialog.askopenfilename(
            title="Open CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            # Validate roll numbers in imported data
            bad_rolls = []
            for i, row in enumerate(rows, start=2):
                roll = row.get("roll", row.get("Roll", "")).strip()
                err = validate_attendance_roll(roll)
                if err:
                    bad_rolls.append(f"Row {i}: {err}")
            if bad_rolls:
                messagebox.showerror(
                    "Import Error – Invalid Roll Numbers",
                    "The following rows have invalid roll numbers and were not imported:\n\n" +
                    "\n".join(bad_rolls[:10]) +
                    ("\n…and more." if len(bad_rolls) > 10 else "")
                )
                return
            self.table.delete(*self.table.get_children())
            for row in rows:
                vals = list(row.values())
                self.table.insert("", END, values=vals)
            messagebox.showinfo("Imported", f"Loaded {len(rows)} records.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Save CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            rows = [self.table.item(r)["values"]
                    for r in self.table.get_children()]
            if not rows:
                messagebox.showerror("Error", "No data to export.")
                return
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["ID","Roll","Name","Department","Time","Date","Status"])
                w.writerows(rows)
            messagebox.showinfo("Exported",
                                f"Saved {len(rows)} records to {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = Tk()
    Attendance1(root)
    root.mainloop()
