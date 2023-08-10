import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
import sqlite3
from DBManipulation import ManipulateDB


class EditForm:
    def __init__(self, edit, manipulate_db):
        # Constructor
        self.window = edit
        self.db = manipulate_db
        self.window.title("Enrollment Scheduling System")
        self.headingLabel = tk.Label(self.window, text="E D I T  F O R M",
                                     font=("", 13), bg="#3f3f3f", pady=7)
        self.headingLabel.pack(fill=X)
        self.headingLabel.config(fg="white")
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_pos = (screen_width - 750) // 2
        y_pos = (screen_height - 650) // 2
        self.window.geometry(f"750x650+{x_pos}+{y_pos}")

        # Canvases
        self.container_frame = tk.Frame(self.window, bg="#a9a9a9")
        self.container_frame.pack()
        self.frame = tk.Frame(self.window, bg="#bebebe")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Initialize variables
        self.student_number = tk.StringVar()
        self.first_name = tk.StringVar()
        self.last_name = tk.StringVar()
        self.course_id = tk.StringVar()
        self.year = tk.StringVar()
        self.grades = tk.StringVar()
        self.status = tk.StringVar(value=0)

        self.create_widgets()   # Call Widget Creation Method
        self.populate_table()   # Call Populate Table for creation of TableView

    def create_widgets(self):
        # Tabular View of Database Table -- Student 
        self.table_frame = tk.LabelFrame(self.container_frame, text="Student Table", bg="#a9a9a9")
        self.table_frame.pack(padx=20, pady=10, fill=tk.BOTH)

        # Treeview
        self.tree = ttk.Treeview(self.table_frame,
                                 columns=("StudentID", "StudentFirstName", "StudentLastName", "CourseID", 
                                          "YearLevel","Grades", "Status"))
        self.tree.heading("#0", text="Index")
        self.tree.heading("StudentID", text="Student ID")
        self.tree.heading("StudentFirstName", text="First Name")
        self.tree.heading("StudentLastName", text="Last Name")
        self.tree.heading("CourseID", text="Course ID")
        self.tree.heading("YearLevel", text="Year Level")
        self.tree.heading("Grades", text="Grades")
        self.tree.heading("Status", text="Status")

        self.tree_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.pack(side="right", fill="y")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # -- Start of Standard GUI Widgets -- #

        # Buttons # 
        self.button_frame = tk.Frame(self.container_frame, bg="#a9a9a9")
        self.button_frame.pack(padx=20, pady=10, fill=tk.BOTH)

        self.update_button = tk.Button(self.button_frame, width=20, text="Update Row", bg="lightgray", command=self.update_selected_row)
        self.update_button.grid(row=0, column=0, padx=5, pady=10)
        self.remove_button = tk.Button(self.button_frame, width=20, text="Remove Row", bg="lightgray", command=self.remove_row)
        self.remove_button.grid(row=0, column=1, padx=5, pady=10)

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        # Primary Information Entry -- Frame 1

        self.info_frame = tk.LabelFrame(self.frame, text="Student Information Entry", bg="#bebebe")
        self.info_frame.pack(padx=20, pady=10, fill=tk.BOTH)

        # Information
        tk.Label(self.info_frame, text="Student Number:", bg="#bebebe").grid(row=0, column=0)
        tk.Label(self.info_frame, text="First Name:", bg="#bebebe").grid(row=0, column=2)
        tk.Label(self.info_frame, text="Last Name:", bg="#bebebe").grid(row=0, column=4)

        self.stud_num_entry = tk.Entry(self.info_frame, textvariable=self.student_number)
        self.stud_num_entry.grid(row=0, column=1)
        self.firstname_entry = tk.Entry(self.info_frame, textvariable=self.first_name)
        self.firstname_entry.grid(row=0, column=3)
        self.lastname_entry = tk.Entry(self.info_frame, textvariable=self.last_name)
        self.lastname_entry.grid(row=0, column=5)
        
        # Other Student Information Entry -- 2nd Frame
        
        self.info1_frame = tk.LabelFrame(self.frame, text="", bg="#bebebe")
        self.info1_frame.pack(padx=20, pady=10, fill=tk.BOTH)

        # Information #
        tk.Label(self.info1_frame, text="CourseID:", bg="#bebebe").grid(row=0, column=0)
        tk.Label(self.info1_frame, text="Year Level:", bg="#bebebe").grid(row=0, column=2)
        tk.Label(self.info1_frame, text="GPA:", bg="#bebebe").grid(row=0, column=4)

        self.course_combobox = ttk.Combobox(self.info1_frame, values=["BSIT", "BSCS"], textvariable=self.course_id)
        self.course_combobox.grid(row=0, column=1)
        self.yr_level_combobox = ttk.Combobox(self.info1_frame, values=["1", "2", "3", "4"], textvariable=self.year)
        self.yr_level_combobox.grid(row=0, column=3)
        self.grades_entry = tk.Entry(self.info1_frame, textvariable=self.grades)
        self.grades_entry.grid(row=0, column=5)

        # Status #
        tk.Label(self.info1_frame, text="", bg="#bebebe").grid(row=1, column=0)
        tk.Label(self.info1_frame, text="Status:", bg="#bebebe").grid(row=1, column=1)

        reg_status_rb = tk.Radiobutton(self.info1_frame, text="Regular", bg="#bebebe", padx=20, variable=self.status, value=1)
        reg_status_rb.grid(row=1, column=2)
        irregular_status_rb = tk.Radiobutton(self.info1_frame, text="Irregular", bg="#bebebe", padx=20, variable=self.status, value=2)
        irregular_status_rb.grid(row=1, column=3)

        # Buttons #
        button_frame_2 = tk.Frame(self.frame, bg="#bebebe")
        button_frame_2.pack(padx=20, pady=10, fill=tk.BOTH)

        add_button = tk.Button(button_frame_2, width=20, text="Add", bg="lightgray", command=self.add_row)
        add_button.grid(row=0, column=0, padx=5, pady=10)

        clear_button = tk.Button(button_frame_2, width=20, text="Clear", bg="lightgray", command=self.clear_fields)
        clear_button.grid(row=0, column=1, padx=5, pady=10)

        # Center the buttons horizontally
        button_frame_2.columnconfigure(0, weight=1)
        button_frame_2.columnconfigure(1, weight=1)

        # Spacing Widgets #
        for widget in self.info_frame.winfo_children():
            widget.grid_configure(padx=5, pady=10)
        for widget in self.info1_frame.winfo_children():
            widget.grid_configure(padx=5, pady=5)

        self.tree.unbind("<<TreeviewSelect>>")
        self.tree.bind("<<TreeviewSelect>>", lambda event: self.update_row())

    def populate_table(self):
        try:
            conn = sqlite3.connect("Database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Student")
            data = cursor.fetchall()
            self.tree.delete(*self.tree.get_children())

            for index, row in enumerate(data, start=1):
                self.tree.insert("", "end", text=str(index), values=row)
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

            conn.close()
        except Exception as e:
            print("Error while populating table:", e)

    def clear_fields(self):
        self.stud_num_entry.delete(0, tk.END)
        self.firstname_entry.delete(0, tk.END)
        self.lastname_entry.delete(0, tk.END)
        self.course_combobox.delete(0, tk.END)
        self.yr_level_combobox.delete(0, tk.END)
        self.grades_entry.delete(0, tk.END)
        self.status.set(0)
        self.tree.selection_remove(self.tree.selection())

    def add_row(self):
        if not self.check_student_num() or not self.check_names() or not self.check_grades():
            return

        self.selected_status = "Regular" if self.status.get() == "1" else "Irregular"
        self.db.add_to_database(self.student_number.get(), self.first_name.get(), self.last_name.get(),
                                self.course_id.get(), self.year.get(), self.grades.get(), self.selected_status)
        self.populate_table()
        self.clear_fields()
        messagebox.showinfo("", "Successful Data Transfer.")
        print("Successful Data Transfer")

    def remove_row(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a row to remove.")
            return

        result = messagebox.askyesno("Confirm Deletion", "Are you sure you want to remove the selected row(s)?")
        if result:
            for item in selected_items:
                item_id = self.tree.item(item, "text")
                student_id = self.tree.item(item, "values")[0]
                self.db.remove_from_database(student_id)
                self.tree.delete(item)
            messagebox.showinfo("", "Successful Data Removal")
            print("Successful Data Removal")

    def update_row(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a row to update.")
            return

        selected_item = selected_items[0]
        student_data = self.tree.item(selected_item, "values")
        if not student_data:
            messagebox.showwarning("Invalid Selection", "Selected row has no valid Student data.")
            return

        # Populate the entry fields with the data from the selected row
        self.student_number.set(student_data[0])
        self.first_name.set(student_data[1])
        self.last_name.set(student_data[2])
        self.course_id.set(student_data[3])
        self.year.set(student_data[4])
        self.grades.set(student_data[5])
        self.status.set("Regular" if student_data[6] == "Regular" else "Irregular")

    def update_selected_row(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a row to update.")
            return

        selected_item = selected_items[0]
        student_id = self.tree.item(selected_item, "values")[0]
        if not student_id:
            messagebox.showwarning("Invalid Selection", "Selected row has no valid Student ID.")
            return

        # Get the updated values from the input fields
        updated_student_number = self.student_number.get()
        updated_first_name = self.first_name.get()
        updated_last_name = self.last_name.get()
        updated_course = self.course_id.get()
        updated_year = self.year.get()
        updated_grades = self.grades.get()

        # Check if the updated student number already exists in the database
        if updated_student_number != student_id and self.db.is_student_id_exists(updated_student_number):
            messagebox.showerror("Duplicate StudentID", "A student with the same ID already exists.")
            return

        selected_status = "Regular" if self.status.get() == "1" else "Irregular"
        self.db.update_database(student_id, updated_student_number, updated_first_name, updated_last_name,
                                updated_course, updated_year, updated_grades, selected_status)

        # Update the table view
        self.tree.set(selected_item, "StudentID", updated_student_number)
        self.tree.set(selected_item, "StudentFirstName", updated_first_name)
        self.tree.set(selected_item, "StudentLastName", updated_last_name)
        self.tree.set(selected_item, "CourseID", updated_course)
        self.tree.set(selected_item, "YearLevel", updated_year)
        self.tree.set(selected_item, "Grades", updated_grades)
        self.tree.set(selected_item, "Status", selected_status)

        messagebox.showinfo("Success", "Data updated successfully.")
    
    def check_student_num(self):
        student_id = self.student_number.get()
        if not student_id:
            messagebox.showinfo("Student Number: Error!", "Please enter a valid student number.")
            return False
        try:
            int(student_id)
        except ValueError:
            messagebox.showinfo("Student Number: Error!", "Please enter a valid student number (numbers only).")
            return False
        if self.db.is_student_id_exists(student_id):
            messagebox.showerror("Duplicate StudentID", "A student with the same ID already exists.")
            return False
        return True

    def check_names(self):
        if len(self.first_name.get()) > 0 and len(self.last_name.get()) > 0:
            return True
        else:
            messagebox.showinfo("Name Entry: Error!", "Please enter a name (First and Last).")
            return False

    def check_grades(self):
        try:
            gpa = float(self.grades.get())
            if gpa <= 3.00:
                return True
            else:
                messagebox.showwarning("Warning!", "The GPA you have entered does not meet the standards "
                                                   "for enrollment. Please comply with the "
                                                   "office regarding this matter.")
                return False
        except ValueError:
            messagebox.showinfo("GPA: Error!", "Please enter a valid GPA (a number).")
            return False
        
    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        student_data = self.tree.item(selected_item, "values")
        if not student_data:
            return

        # Populate the entry fields with the data from the selected row
        self.student_number.set(student_data[0])
        self.first_name.set(student_data[1])
        self.last_name.set(student_data[2])
        self.course_id.set(student_data[3])
        self.year.set(student_data[4])
        self.grades.set(student_data[5])
        self.status.set("Regular" if student_data[6] == "Regular" else "Irregular")

    def close_and_open_login(self):
        self.window.destroy()
        self.show_login()

    def show_login(self):
        if self.app:
            self.app.destroy()
        self.window.deiconify()

# # Run code for testing
# if __name__ == "__main__":
#     window = tk.Tk()
#     db = ManipulateDB()
#     app = EditForm(window, db)
#     window.mainloop()
