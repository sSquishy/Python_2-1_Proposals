import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from EditForm import EditForm
from QueryForm import QueryForm
from DBManipulation import ManipulateDB
from tkinter import *


class Login:
    def __init__(self, start):
        # Constructor
        self.window = start
        self.window.title("Enrollment Scheduling System -- Log In") 

        self.headingLabel = tk.Label(self.window, text="L O G I N",
                                     font=("", 12), bg="#3f3f3f", pady=7)
        self.headingLabel.pack(fill=X)
        self.headingLabel.config(fg="white")

        self.frame = tk.Frame(self.window, bg="#a9a9a9")
        self.frame.pack(fill="both", expand=True)
        self.window.title("Enrollment Scheduling System")
       
        self.app = None
        self.manipulate_db = None
        self.options = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        # Frame for Login
        self.login_frame = tk.LabelFrame(self.frame, text="", bg="#a9a9a9")
        self.login_frame.grid(row=0, column=0, pady=10)

        # Set the grid row and column weights for the main frame
        self.frame.grid_rowconfigure(0, weight=2)
        self.frame.grid_columnconfigure(0, weight=2)

        tk.Label(self.login_frame, text="User:", bg="#a9a9a9").grid(row=0, column=0)
        self.user_combobox = ttk.Combobox(self.login_frame, width=30,
                                          values=["Faculty", "Student"], textvariable=self.options)
        self.user_combobox.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Username:", bg="#a9a9a9").grid(row=1, column=0)
        self.username_entry = tk.Entry(self.login_frame, width=30, textvariable=self.username)
        self.username_entry.grid(row=1, column=1)

        tk.Label(self.login_frame, text="Password:", bg="#a9a9a9").grid(row=2, column=0)
        self.pass_entry = tk.Entry(self.login_frame, width=30, textvariable=self.password)
        self.pass_entry.grid(row=2, column=1)

        for widget in self.login_frame.winfo_children():
            widget.grid_configure(sticky="news", padx=5, pady=5)

        tk.Button(self.frame, width=20, text="Log In", 
                  command=self.login_command, bg="lightgray").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Button(self.frame, width=20, text="Clear", 
                  command=self.clear_fields, bg="lightgray").grid(row=1, column=0, sticky="e", padx=10, pady=5)

    # Login Method
    def login_command(self):
        try:
            user_type = self.user_combobox.get()
            username = self.username_entry.get()
            password = self.pass_entry.get()
            if not user_type or not username or not password:
                messagebox.showwarning("Error", "Please fill out all fields.")
                return
            if user_type == "Faculty":
                self.run_faculty()
            if user_type == "Student":
                self.run_student()
        except ValueError:
            messagebox.showwarning("Invalid", "There are no inputs. Please try again.")

    # Run Window for Students Only -- Enrollment Scheduling Form
    def run_student(self):
        if self.username_entry.get() == "HelloWorld" and self.pass_entry.get() == "1234567":
            self.window.withdraw()
            self.manipulate_db = ManipulateDB()
            self.app = tk.Toplevel(self.window)
            self.main_form = QueryForm(self.app, self.manipulate_db)
            self.main_form.window.protocol("WM_DELETE_WINDOW", self.close_and_open_login)
            self.window.wait_window(self.app)
        else:
            messagebox.showwarning("Error", "Wrong combination of Username and Password.")

    # Run Window for Faculties Only -- Student Enlistment Form
    def run_faculty(self):
        if self.username_entry.get() == "HelloWorld" and self.pass_entry.get() == "12345":
            self.window.withdraw()
            self.manipulate_db = ManipulateDB()
            self.app = tk.Toplevel(self.window)
            self.edit_form = EditForm(self.app, self.manipulate_db)
            self.edit_form.window.protocol("WM_DELETE_WINDOW", self.close_and_open_login)
            self.window.wait_window(self.app)
        else:
            messagebox.showwarning("Error", "Wrong combination of Username and Password.")

    def close_and_open_login(self):
        self.app.destroy()  # Close the EditForm window
        self.window.deiconify()  # Open the Login window

    def clear_fields(self):
        self.user_combobox.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)

# -- Main() -- #
if __name__ == "__main__":
    window = tk.Tk()
    app = Login(window)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_pos = (screen_width - 400) // 2
    y_pos = (screen_height - 200) // 2
    window.geometry(f"{400}x{200}+{x_pos}+{y_pos}")
    window.mainloop()
