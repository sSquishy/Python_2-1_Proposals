import tkinter as tk
from tkinter import *
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from DBManipulation import ManipulateDB


class QueryForm:
    def __init__(self, window, manipulate_db):
        # Constructor
        self.window = window
        self.window.title("Enrollment Scheduling System")
        self.window.configure(bg="#bebebe")
        self.db = manipulate_db

        self.headingLabel = tk.Label(self.window, text="Q U E R Y   F O R M",
                                     font=("", 12), bg="#3f3f3f", pady=7)
        self.headingLabel.pack(fill=X)
        self.headingLabel.config(fg="white")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_pos = (screen_width - 800) // 2
        y_pos = (screen_height - 500) // 2
        self.window.geometry(f"800x500+{x_pos}+{y_pos}")

        # Canvases
        self.student_frame = tk.Frame(self.window, bg="#bebebe")
        self.student_frame.pack(fill=tk.BOTH, expand=True)

        # self.student_frame = None
        # self.frame = None
        # self.container_frame = None
        self.schedules_frame = None
        self.subjects_frame = None
        self.professors_frame = None
        self.major_frame = None
        self.minor_frame = None

        self.query = tk.StringVar()
        self.conn = sqlite3.connect('Database.db')
        self.strSQL = None
        self.cursor = None
        self.create_student_form()

    # -- Creates a Student Form to Verify Status as a student -- #
    def create_student_form(self):
        self.verification_frame = tk.LabelFrame(self.student_frame, text="Status Verification", 
                                                font=("Calibri"), bg="#bebebe")
        self.verification_frame.pack(padx=20, pady=20, fill=tk.BOTH)

        tk.Label(self.verification_frame, text="Enter Your Student ID: ", font=("Calibri", 14), 
                 bg="#bebebe").grid(row=0, column=0)
        self.id_entry = tk.Entry(self.verification_frame, font=("Calibri", 14))
        self.id_entry.grid(row=0, column=1, pady=20)

        self.verify_btn = tk.Button(self.verification_frame, text="Verify Status", width=15, 
                                    font=("Calibri", 14), bg="lightgray", 
                                    command=self.verify_student_status)
        self.verify_btn.grid(row=0, column=2)

        self.clear = tk.Button(self.verification_frame, text="Clear", width=15, 
                                   font=("Calibri", 14), bg="lightgray", 
                                   command=self.clear_btn)
        self.clear.grid(row=0, column=3)

        for widget in self.verification_frame.winfo_children():
            widget.grid_configure(padx=5, pady=10)

    # -- Checks from database if student ID exists or not
    def verify_student_status(self):
        student_id = self.id_entry.get()
        exists = self.db.is_student_id_exists(student_id)

        if not exists:
            messagebox.showinfo("Invalid Student ID", "The student ID does not exist in the database.")
        if exists:
            status = self.db.get_student_status(student_id)  # Get the student status separately
            if status == "Regular":
                self.create_widgets_regular()
                messagebox.showinfo("", "The entered student number is a regular.")
            if status == "Irregular":
                self.create_widgets_regular()
                messagebox.showinfo("", "The entered student number is an irregular.")

    # -- Creates Widgets based on Status -- Regular
    def create_widgets_regular(self):
        self.frame = tk.Frame(self.window, bg="#bebebe")
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, side=tk.TOP)
        self.container_frame = tk.Frame(self.window, bg="#bebebe")
        self.container_frame.pack(pady=20)

        # Widget Frame
        self.title_frame = tk.LabelFrame(self.frame, text="Queries", bg="#bebebe")
        self.title_frame.pack(fill=tk.BOTH, expand=True, padx=20, anchor=tk.CENTER)

        self.query_combobox = ttk.Combobox(self.title_frame, width=53, values=[
            "Tell me the available schedules for each subject in my Course", 
            "Give me the available subjects for my course",
            "Give me a list of all professors for my course",
            "Give me a list of Major Subjects",
            "Give me a list of Minor Subjects"], textvariable=self.query)
        self.query_combobox.grid(row=0, column=0)
        
        self.add_btn = tk.Button(self.title_frame, width=20, text="Inquire", command=self.btn_command)
        self.add_btn.grid(row=0, column=1)

        for widget in self.title_frame.winfo_children():
            widget.grid_configure(sticky="news", padx=5, pady=5)

    # Is a command based on the query entered by User
    def btn_command(self):
        selected_query = self.query.get()
        if selected_query == "Tell me the available schedules for each subject in my Course":
            self.available_schedules()
        elif selected_query == "Give me the available subjects for my course":
            self.available_subjects()
        elif selected_query == "Give me a list of all professors for my course":
            self.list_professors()
        elif selected_query == "Give me a list of Major Subjects":
            self.list_major_subjects()
        elif selected_query == "Give me a list of Minor Subjects":
            self.list_minor_subjects()
        else:
            messagebox.showwarning("Invalid Query", "Please select a valid query.")

    def available_schedules(self):
        self.clear_table()
        self.schedules_frame = tk.Frame(self.window)
        self.schedules_frame.pack(fill=tk.BOTH, expand=True)
        self.schedules_tree = ttk.Treeview(self.schedules_frame, columns=("Subject Name", "Year", "Semester", "Time Start", "Time End"), show="headings")
        self.schedules_tree.heading("#1", text="Subject Name")
        self.schedules_tree.heading("#2", text="Year")
        self.schedules_tree.heading("#3", text="Semester")
        self.schedules_tree.heading("#4", text="Time Start")
        self.schedules_tree.heading("#5", text="Time End")
        self.schedules_tree.pack(fill=tk.BOTH, expand=True)

        student_id = self.id_entry.get()
        if not student_id:
            messagebox.showwarning("Invalid Input", "Please enter a student ID.")
            return

        conn = sqlite3.connect('Database.db')
        cursor = conn.execute("SELECT CourseID FROM Student WHERE StudentID = ?", (student_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            selected_course = data[0]  # Get the CourseID of the verified student
            conn = sqlite3.connect('Database.db')
            cursor = conn.execute("SELECT SubjectName, Year, Semester, TimeStart, TimeEnd FROM Subject WHERE CourseID = ?", (selected_course,))
            data = cursor.fetchall()
            conn.close()

            if data:
                # Clear existing data in the Treeview
                self.schedules_tree.delete(*self.schedules_tree.get_children())

                # Insert data into the Treeview
                for subject in data:
                    subject_name, year, semester, time_start, time_end = subject
                    self.schedules_tree.insert("", "end", values=(subject_name, year, semester, time_start, time_end))

            else:
                messagebox.showinfo("No Data", "No subjects found for the selected course.")
        else:
            messagebox.showinfo("Student Not Found", "Student not found.")
            
    def available_subjects(self):
        self.clear_table()
        self.subjects_frame = tk.Frame(self.window)
        self.subjects_frame.pack(fill=tk.BOTH, expand=True)
        self.subjects_tree = ttk.Treeview(self.subjects_frame, columns=("Subject Name",), show="headings")
        self.subjects_tree.heading("#1", text="Subject Name")
        self.subjects_tree.pack(fill=tk.BOTH, expand=True)

        student_id = self.id_entry.get()
        if not student_id:
            messagebox.showwarning("Invalid Input", "Please enter a student ID.")
            return

        conn = sqlite3.connect('Database.db')
        cursor = conn.execute("SELECT CourseID FROM Student WHERE StudentID = ?", (student_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            selected_course = data[0]  # Get the CourseID of the verified student
            conn = sqlite3.connect('Database.db')
            cursor = conn.execute("SELECT SubjectName FROM Subject WHERE CourseID = ?", (selected_course,))
            data = cursor.fetchall()
            conn.close()

            if data:
                # Clear existing data in the Treeview
                self.subjects_tree.delete(*self.subjects_tree.get_children())

                # Insert data into the Treeview
                for subject in data:
                    subject_name = subject[0]
                    self.subjects_tree.insert("", "end", values=(subject_name,))
            else:
                messagebox.showinfo("No Data", "No subjects found for the selected course.")
        else:
            messagebox.showinfo("Student Not Found", "Student not found.")

    def list_professors(self):
        self.clear_table()
        self.professors_frame = tk.Frame(self.window)
        self.professors_frame.pack(fill=tk.BOTH, expand=True)
        self.professors_tree = ttk.Treeview(self.professors_frame, columns=("Faculty Name", "Subject Name"), show="headings")
        self.professors_tree.heading("#1", text="Faculty Name")
        self.professors_tree.heading("#2", text="Subject Name")
        self.professors_tree.pack(fill=tk.BOTH, expand=True)

        student_id = self.id_entry.get()
        if not student_id:
            messagebox.showwarning("Invalid Input", "Please enter a student ID.")
            return

        conn = sqlite3.connect('Database.db')
        cursor = conn.execute("SELECT CourseID FROM Student WHERE StudentID = ?", (student_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            selected_course_id = data[0]

            conn = sqlite3.connect('Database.db')
            cursor = conn.execute("SELECT Faculty.FacultyFirstName, Faculty.FacultyLastName, Subject.SubjectName "
                                "FROM Faculty INNER JOIN Subject ON Faculty.FacultyID = Subject.FacultyID "
                                "WHERE Subject.CourseID = ?", (selected_course_id,))
            data = cursor.fetchall()
            conn.close()

            if data:
                # Clear existing data in the Treeview
                self.professors_tree.delete(*self.professors_tree.get_children())

                # Insert data into the Treeview
                for professor in data:
                    faculty_first_name, faculty_last_name, subject_name = professor
                    self.professors_tree.insert("", "end", values=(f"{faculty_first_name} {faculty_last_name}", subject_name))

            else:
                messagebox.showinfo("No Data", "No professors found for the selected course.")
        else:
            messagebox.showinfo("Student Not Found", "Student not found.")

    def list_major_subjects(self):
        self.clear_table()
        self.major_frame = tk.Frame(self.window)
        self.major_frame.pack(fill=tk.BOTH, expand=True)
        self.major_subjects_tree = ttk.Treeview(self.major_frame, columns=("Subject Name",), show="headings")
        self.major_subjects_tree.heading("#1", text="Subject Name")
        self.major_subjects_tree.pack(fill=tk.BOTH, expand=True)

        student_id = self.id_entry.get()
        if not student_id:
            messagebox.showwarning("Invalid Input", "Please enter a student ID.")
            return

        conn = sqlite3.connect('Database.db')
        cursor = conn.execute("SELECT CourseID FROM Student WHERE StudentID = ?", (student_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            selected_course_id = data[0]

            conn = sqlite3.connect('Database.db')
            cursor = conn.execute("SELECT SubjectName FROM Subject WHERE CourseID = ? AND SubjectType = 'Major'", (selected_course_id,))
            data = cursor.fetchall()
            conn.close()

            if data:
                # Clear existing data in the Treeview
                self.major_subjects_tree.delete(*self.major_subjects_tree.get_children())

                # Insert data into the Treeview
                for subject in data:
                    self.major_subjects_tree.insert("", "end", values=(subject[0],))

            else:
                messagebox.showinfo("No Data", "No major subjects found for the selected course.")
        else:
            messagebox.showinfo("Student Not Found", "Student not found.")

    def list_minor_subjects(self):
        self.clear_table()
        self.minor_frame = tk.Frame(self.window)
        self.minor_frame.pack(fill=tk.BOTH, expand=True)
        self.minor_subjects_tree = ttk.Treeview(self.minor_frame, columns=("Subject Name",), show="headings")
        self.minor_subjects_tree.heading("#1", text="Subject Name")
        self.minor_subjects_tree.pack(fill=tk.BOTH, expand=True)

        student_id = self.id_entry.get()
        if not student_id:
            messagebox.showwarning("Invalid Input", "Please enter a student ID.")
            return

        conn = sqlite3.connect('Database.db')
        cursor = conn.execute("SELECT CourseID FROM Student WHERE StudentID = ?", (student_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            selected_course_id = data[0]

            conn = sqlite3.connect('Database.db')
            cursor = conn.execute("SELECT SubjectName FROM Subject WHERE CourseID = ? AND SubjectType = 'Minor'", (selected_course_id,))
            data = cursor.fetchall()
            conn.close()

            if data:
                # Clear existing data in the Treeview
                self.minor_subjects_tree.delete(*self.minor_subjects_tree.get_children())

                # Insert data into the Treeview
                for subject in data:
                    self.minor_subjects_tree.insert("", "end", values=(subject[0],))

            else:
                messagebox.showinfo("No Data", "No minor subjects found for the selected course.")
        else:
            messagebox.showinfo("Student Not Found", "Student not found.")

    # Clears the Screen
    def clear_btn(self):
        if self.frame:
            self.frame.pack_forget()
        self.clear_table()
        self.id_entry.delete(0, tk.END)

    
    def clear_table(self):
        if self.container_frame:
            self.container_frame.pack_forget()
        if self.schedules_frame:
            self.schedules_frame.pack_forget()
        if self.subjects_frame:
            self.subjects_frame.pack_forget()
        if self.professors_frame:
            self.professors_frame.pack_forget()
        if self.major_frame:
            self.major_frame.pack_forget()
        if self.minor_frame:
            self.minor_frame.pack_forget()

    def close_and_open_login(self):
        self.window.destroy()
        self.show_login()

    def show_login(self):
        if self.app:
            self.app.destroy()
        self.window.deiconify()

# Run code for testing #
if __name__ == "__main__":
    window = tk.Tk()
    db = ManipulateDB()
    app = QueryForm(window, db)
    window.mainloop()
