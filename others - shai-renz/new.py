import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk


def fetch_ward_info():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    cursor.execute("SELECT ward_id, ward_location, ward_status, ward_beds, ward_type, ward_last_update FROM WARD")
    ward_info = []
    for row in cursor:
        ward_id, ward_location, ward_status, ward_beds, ward_type, ward_last_update = row
        ward_info.append({
            'Ward ID': ward_id,
            'Ward Location': ward_location,
            'Ward Status': ward_status,
            'Ward Beds': ward_beds,
            'Ward Type': ward_type,
            'Last Update': ward_last_update,
            'Beds': []
        })
    conn.close()

    # Sort the ward_info list based on ward_location
    ward_info = sorted(ward_info, key=lambda x: x['Ward Location'])

    return ward_info


def fetch_bed_info(ward_id):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    cursor.execute("SELECT bed_id, bed_location_row, bed_location_column, bed_status, bed_size "
                   "FROM beds WHERE ward_id=?", (ward_id,))
    bed_info = []
    for row in cursor:
        bed_id, bed_location_row, bed_location_column, bed_status, bed_size = row

        # Check if bed_location_row is an empty string or non-integer value
        try:
            bed_location_row = int(bed_location_row)
        except (ValueError, TypeError):
            # Skip this entry if it's not a valid integer
            continue

        bed_info.append({
            'Bed ID': bed_id,
            'Bed Location Row': bed_location_row,
            'Bed Location Column': bed_location_column,
            'Bed Status': bed_status,
            'Bed Size': bed_size,
        })

    conn.close()

    # Sort the bed_info list based on 'Bed Location Row' as integers
    bed_info = sorted(bed_info, key=lambda x: x['Bed Location Row'])
    return bed_info


# Function to check admin credentials in the "admin" table
def check_admin_credentials(username, password):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    # Check if the provided username and password match any admin record
    cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
    admin_record = cursor.fetchone()

    conn.close()
    return admin_record


def insert_new_ward(ward_id, ward_location, ward_status, ward_beds, ward_type, ward_last_update):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Check if the ward ID already exists in the database
    cursor.execute("SELECT ward_id FROM WARD WHERE ward_id=?", (ward_id,))
    existing_ward = cursor.fetchone()
    if existing_ward:
        conn.close()
        raise ValueError("Ward with this ID already exists.")

    # Insert the new ward into the database
    cursor.execute("INSERT INTO WARD (ward_id, ward_location, ward_status, ward_beds, ward_type, ward_last_update) "
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   (ward_id, ward_location, ward_status, ward_beds, ward_type, ward_last_update))

    conn.commit()
    conn.close()


def insert_new_bed(bed_id, ward_id, bed_location_row, bed_location_column, bed_status, bed_size):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Check if the bed ID already exists in the database
    cursor.execute("SELECT bed_id FROM BEDS WHERE bed_id=?", (bed_id,))
    existing_bed = cursor.fetchone()
    if existing_bed:
        conn.close()
        raise ValueError("Bed with this ID already exists.")

    # Insert the new bed into the database
    cursor.execute("INSERT INTO BEDS (bed_id, ward_id, bed_location_row, bed_location_column, bed_status, bed_size) "
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   (bed_id, ward_id, bed_location_row, bed_location_column, bed_status, bed_size))

    conn.commit()
    conn.close()


def update_ward_details(ward_id, ward_type=None, ward_location=None, ward_status=None, ward_beds=None, ward_last_update=None):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Construct the SQL query and parameters based on the provided details
    query = "UPDATE WARD SET "
    updates = []
    if ward_type is not None:
        updates.append("ward_type = ?")
    if ward_location is not None:
        updates.append("ward_location = ?")
    if ward_status is not None:
        updates.append("ward_status = ?")
    if ward_beds is not None:
        updates.append("ward_beds = ?")
    if ward_last_update is not None:
        updates.append("ward_last_update = ?")

    query += ", ".join(updates)
    query += " WHERE ward_id = ?"

    params = []
    if ward_type is not None:
        params.append(ward_type)
    if ward_location is not None:
        params.append(ward_location)
    if ward_status is not None:
        params.append(ward_status)
    if ward_beds is not None:
        params.append(ward_beds)
    if ward_last_update is not None:
        params.append(ward_last_update)

    params.append(ward_id)

    # Execute the SQL query with the constructed parameters
    cursor.execute(query, tuple(params))

    conn.commit()
    conn.close()


def update_bed_details(bed_id, bed_location_row, bed_location_column, bed_status, bed_size):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Update the bed details in the database
    cursor.execute("""
        UPDATE BEDS
        SET bed_location_row = ?, bed_location_column = ?, bed_status = ?, bed_size = ?
        WHERE bed_id = ?
    """, (bed_location_row, bed_location_column, bed_status, bed_size, bed_id))

    conn.commit()
    conn.close()


# For cursor hovering
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() - 10
        y += self.widget.winfo_rooty() + 15

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        tooltip_width = 23
        tooltip_height = 9
        tooltip_font = tkfont.Font(family="Avenir LT Std 65 Medium", size=9)
        label = tk.Label(self.tooltip, text=self.text, fg="#1D509D", bg="#ECF6FF", relief="solid", borderwidth=1,
                         width=tooltip_width, height=tooltip_height, justify="left", font=tooltip_font)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


# function for the first interface - log in window
def create_login_window():
    global user_window  # Define user_window as a global variable

    # Create the login window
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("1920x1080")

    # LEFT SIDE
    # Create a left frame for the login fields
    left_frame = tk.Frame(login_window, bg="white", width=375)
    left_frame.pack(side="left", fill="both", expand=True)

    # Create a spacer frame to center the contents vertically
    spacer_frame = tk.Frame(left_frame, bg="white")
    spacer_frame.pack(expand=True)

    # Add labels and entry fields for username and password in the spacer frame
    custom_font = tkfont.Font(family="Avenir LT Std 65 Medium", size=14)  # Define the custom font
    username_label = tk.Label(spacer_frame, text="Username:", font=custom_font, fg="#1D509D", bg="white")
    username_label.grid(row=0, column=0, padx=10, pady=(30, 5), sticky="e")

    username_entry = tk.Entry(spacer_frame, bg="#F0F0F0", width=20, font=custom_font)  # Adjust the width as desired
    username_entry.grid(row=0, column=1, padx=10, pady=(30, 5))

    password_label = tk.Label(spacer_frame, text="Password:", font=custom_font, fg="#1D509D", bg="white")
    password_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    password_entry = tk.Entry(spacer_frame, bg="#F0F0F0", width=20, font=custom_font)  # Adjust the width as desired
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    # Add a login button in the spacer frame
    login_button = tk.Button(spacer_frame, text=("Log in"), command=login,
                             font=("Avenir LT Std 65 Medium", 10), fg="#1D509D", bg="white")
    login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 30))

    # Configure the left frame to center its contents vertically
    left_frame.pack_propagate(False)

    # RIGHT SIDE
    # Create a right frame for the design elements
    right_frame = tk.Frame(login_window, bg="#6391D6", width=375)
    right_frame.pack(side="right", fill="both", expand=True)

    # Create a top spacer frame in the right frame to center the contents vertically
    top_spacer_frame = tk.Frame(right_frame, bg="#6391D6")
    top_spacer_frame.pack(expand=True)

    # Add the "CHERRY HOSPITAL" logo image in the right frame
    image_path = "CHOSP.png"
    logo_image = Image.open(image_path)
    logo_image = logo_image.resize((500, 280), Image.BILINEAR)  # Use 'BILINEAR' instead of 'ANTIALIAS'
    logo_image = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(right_frame, image=logo_image, bg="#6391D6")
    logo_label.image = logo_image
    logo_label.pack()

    # Add the "CHERRY HOSPITAL" heading in the right frame
    heading_label = tk.Label(right_frame, text="Cherry Hospital", font=("Proxima Nova Rg", 40, "bold"), fg="white", bg="#6391D6")
    heading_label.pack()
    # Add the subheading label in the right frame
    subheading_label = tk.Label(right_frame, text='A cherry a day keeps Doc J away',
                                font=("Avenir LT Std 65 Medium", 16), fg="#19345D", bg="#6391D6")
    subheading_label.pack(pady=10)

    # Add a view page button in the right frame
    view_page_button = tk.Button(right_frame, text="View Page", command=view_page,
                                 font=("Avenir LT Std 65 Medium", 10), fg="#1D509D")
    view_page_button.pack(pady=(0, 10))  # Adjust the pady value to move the button higher

    # Add a bottom spacer frame in the right frame to center the contents vertically
    bottom_spacer_frame = tk.Frame(right_frame, bg="#6391D6")
    bottom_spacer_frame.pack(expand=True)

    # Configure the right frame to center its contents vertically
    right_frame.pack_propagate(False)

    return login_window, username_entry, password_entry


# user window interface
def view_page():
    global login_window  # Declare login_window as a global variable
    global ward_info
    login_window.withdraw()

    # Create the user window
    user_window = tk.Toplevel(login_window)
    user_window.title("User Window")
    user_window.geometry("1400x800")

    # Set the background color of the user window to white
    user_window.configure(bg="white")

    def go_back():
        user_window.destroy()
        login_window.deiconify()

    # Create a frame for the header
    header_frame = tk.Frame(user_window, bg="white")
    header_frame.pack(side="top", fill="x", pady=(0, 5))  # Adjust the pady value as needed

    # Add the CHOSP logo
    logo_image = Image.open("CHOSP.png")
    logo_image = logo_image.resize((120, 70))
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(header_frame, image=logo_photo, bg="white")
    logo_label.image = logo_photo
    logo_label.pack(side="right")

    # Create a frame for the header labels
    header_labels_frame = tk.Frame(header_frame, bg="white") # left side ng header
    header_labels_frame.pack(side="right", anchor="ne")

    # Add the header label
    header_label = tk.Label(header_labels_frame, text="Cherry Hospital", font=("Proxima Nova Rg", 27, "bold"), fg="#1D509D",
                            bg="white")
    header_label.pack(side="top", anchor="ne")

    # Add the subheading label
    subheader_label = tk.Label(header_labels_frame, text="A Cherry a Day Keeps Doc J Away", font=("Avenir LT Std 65 Medium", 9, "bold"),
                               fg="#1D509D", bg="white")
    subheader_label.pack(side="top", anchor="ne")

    # Add the divider line
    divider_line = tk.Frame(user_window, height=2, bg="#1D509D")
    divider_line.pack(fill="x")

    # Create a frame for the content
    content_frame = tk.Frame(user_window, bg="white")  # below divider line
    content_frame.pack(fill="both", expand=False)

    # Create a frame for the "WARD" label and rectangles
    ward_frame = tk.Frame(content_frame, bg="white")
    ward_frame.pack(side="top", padx=10, pady=(20, 0), anchor="w")

    # Add the "WARD" label
    ward_label = tk.Label(ward_frame, text="WARD", font=("Avenir LT Std 65 Medium", 24, "bold"), fg="#1D509D", bg="white")
    ward_label.pack(side="left", padx=300)

    # Create a frame for rectangles
    rectangle_frame = tk.Frame(content_frame, bg="white")  # outer ng rectangles
    rectangle_frame.pack(side="top", fill="both", padx=(10,0))  # Add padx to center the rectangles

    # Configure grid weights for equal sizing
    rows = 3
    columns = 3

    for row in range(rows):
        rectangle_frame.grid_rowconfigure(row, weight=1, uniform="equal")

    for column in range(columns):
        rectangle_frame.grid_columnconfigure(column, weight=1, uniform="equal")

    # Fetch ward information from the database
    ward_info = fetch_ward_info()

    # Create a frame for the left side
    left_frame = tk.Frame(content_frame, bg="white", width=410)  # Adjust the width as needed
    left_frame.pack(side="left", fill="y")

    # Create a frame for the rectangles and back button
    rectangles_frame = tk.Frame(content_frame, bg="white", width=50)
    rectangles_frame.pack(fill="both", expand=True)

    for row in range(rows):
        for column in range(columns):
            if row * columns + column >= len(ward_info):
                break

            ward = ward_info[row * columns + column]

            rectangle = tk.Label(rectangles_frame, width=20, height=8, bg="#ECF6FF")
            rectangle.grid(row=row, column=column, padx=20, pady=10, sticky="nsew")

            ward_type_label = tk.Label(rectangle, text=ward['Ward Type'].upper(), font=("Avenir LT Std 65 Medium", 12), anchor="w",
                                       fg="#1D509D", bg="#ECF6FF", justify="left")
            ward_type_label.place(relx=0.5, rely=0.3, anchor="center")

            ward_id = ward['Ward ID'].replace("PB", "").replace("PR", "")
            ward_id_label = tk.Label(rectangle, text=ward_id, font=("Avenir LT Std 65 Medium", 12), anchor="w",
                                     fg="#1D509D", bg="#ECF6FF", justify="left")
            ward_id_label.place(relx=0.5, rely=0.5, anchor="center")

            ward_status_label = tk.Label(rectangle, text=ward['Ward Status'], font=("Avenir LT Std 65 Medium", 12), anchor="w",
                                         bg="#ECF6FF", justify="left")
            ward_status_label.place(relx=0.5, rely=0.7, anchor="center")

            # Set the ward status label color based on availability
            if ward['Ward Status'] == "Available":
                ward_status_label.configure(fg="#216B39")
            else:
                ward_status_label.configure(fg="#D33E3D")

            tooltip_text = f"           {ward['Ward ID']}\n\n" \
                           f"Ward Type: {ward['Ward Type']}\n" \
                           f"Location: {ward['Ward Location']}\n" \
                           f"Beds:    {ward['Ward Beds']}\n\n" \
                           f"         {ward['Ward Status']}\n" \
                           f"         {ward.get('Last Update', '-')}"

            ToolTip(rectangle, tooltip_text)

            rectangle.bind("<Button-1>",
                           lambda event, ward_id=ward['Ward ID']: BedInfoWindow(event.widget.master, ward.copy(),
                                                                                ward_id))

    # Add the back button beside the rectangles on the second row
    back_button = tk.Button(rectangles_frame, text="Back", command=go_back, font=("Avenir LT Std 65 Medium", 10), fg='#1D509D')
    back_button.grid(row=1, column=columns, padx=30, pady=10, sticky="se")

    # Create a frame for the footer
    footer_frame = tk.Frame(user_window, bg="white")
    footer_frame.pack(side="bottom")

    # Add the address and telephone number in the footer
    address_frame = tk.Frame(footer_frame, bg="white")
    address_frame.pack(side="left", anchor="ne", padx=10)

    telephone_frame = tk.Frame(footer_frame, bg="white")
    telephone_frame.pack(side="right", anchor="sw", padx=40)

    # Emoji label for address
    emoji_address_label = tk.Label(address_frame, text="📍", font=("Arial", 16), fg='#1D509D', bg="white")
    emoji_address_label.pack(side="left")

    # Text label for address
    address_label = tk.Label(address_frame, text="Commonwealth, Quezon City", font=("Avenir LT Std 65 Medium", 10),
                             fg="#1D509D",
                             bg="white")
    address_label.pack(side="left")

    # Emoji label for telephone
    emoji_telephone_label = tk.Label(telephone_frame, text="📞", font=("Arial", 16), fg='#1D509D', bg="white")
    emoji_telephone_label.pack(side="left")

    # Text label for telephone
    telephone_label = tk.Label(telephone_frame, text="123-456-789", font=("Avenir LT Std 65 Medium", 10), fg="#1D509D",
                               bg="white")
    telephone_label.pack(side="left")

    # Run the user window event loop
    user_window.mainloop()


# class for bed information
class BedInfoWindow(tk.Toplevel):
    def __init__(self, master, ward_info, ward_id):
        super().__init__(master)
        self.title("Bed Information")
        self.geometry("1920x1080")
        self.configure(bg="white")  # Set the background color of the window to white

        # Fetch bed information from the database using the ward_id
        bed_info = fetch_bed_info(ward_id)

        # Now you can use 'ward_id' instead of 'war' as the variable name
        ward_id = ward_id
        num_beds = len(bed_info)

        # Create a frame for the header
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(side="top", fill="x", pady=(0, 5))  # Adjust the pady value as needed

        # Add the CHOSP logo
        logo_image = Image.open("CHOSP.png")
        logo_image = logo_image.resize((120, 70))
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(header_frame, image=logo_photo, bg="white")
        logo_label.image = logo_photo
        logo_label.pack(side="right")

        # Create a frame for the header labels
        header_labels_frame = tk.Frame(header_frame, bg="white")  # left side ng header
        header_labels_frame.pack(side="right", anchor="ne")

        # Add the header label
        header_label = tk.Label(header_labels_frame, text="Cherry Hospital", font=("Proxima Nova Rg", 27, "bold"),
                                fg="#1D509D", bg="white")
        header_label.pack(side="top", anchor="ne")

        # Add the subheading label
        subheader_label = tk.Label(header_labels_frame, text="A Cherry a Day Keeps Doc Joey Away",
                                   font=("Avenir LT Std 65 Medium", 9, "bold"), fg="#1D509D", bg="white")
        subheader_label.pack(side="top", anchor="ne")

        # Add the divider line
        divider_line = tk.Frame(self, height=2, bg="#1D509D")
        divider_line.pack(side="top", fill="x")

        ward_label = tk.Label(self, text=f"WARD {ward_id}", font=("Avenir LT Std 65 Medium", 12), anchor="s",
                              fg="#1D509D", bg="white")
        ward_label.pack(pady=(25,0), padx=(0, 1200))

        # Create a frame for the content
        content_frame = tk.Frame(self, bg="white")  # outer frame
        content_frame.pack(fill="both", expand=False)

        # Create a frame to hold the canvas and scroll bar
        canvas_frame = tk.Frame(self, bg="#ECF6FF", width=10)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Create a canvas
        canvas = tk.Canvas(canvas_frame, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scroll bar
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scroll bar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Calculate the canvas height based on the number of beds
        canvas_height = min(220, (num_beds // 2 + num_beds % 2) * 70)  # Adjust the height as needed

        # Create a frame inside the canvas to hold the bed information
        bed_frame = tk.Frame(canvas, bg="#ECF6FF")
        bed_frame.pack(padx=20, pady=5, fill="both", expand=True)

        # Create bed rectangles
        for index, bed in enumerate(bed_info):
            bed_id = bed['Bed ID']
            bed_status = bed['Bed Status']
            bed_size = bed['Bed Size']

            row = bed['Bed Location Row']
            column = bed['Bed Location Column']

            bed_info_frame = tk.Frame(bed_frame, bg="#ECF6FF")  # bed emoji
            bed_info_frame.grid(row=row, column=column, padx=20, pady=10, sticky="nsew")

            if bed_status == "Occupied":
                bed_emoji_label = tk.Label(bed_info_frame, text="🛌",
                                           font=("Avenir LT Std 65 Medium", 25), bg="#ECF6FF", fg="#D33E3D")
            elif bed_status == "Sanitize":
                bed_emoji_label = tk.Label(bed_info_frame, text="🛌",
                                           font=("Avenir LT Std 65 Medium", 25), bg="#ECF6FF", fg="#216B39")
            else:
                bed_emoji_label = tk.Label(bed_info_frame, text="🛌",
                                           font=("Avenir LT Std 65 Medium", 25), bg="#ECF6FF", fg="#1D509D")
            bed_emoji_label.pack(side="left", padx=7, pady=10)

            bed_info_text = f"Bed ID: {bed_id}\n" \
                            f"Bed Status: {bed_status}\n" \
                            f"Bed Size: {bed_size}"

            bed_info_label = tk.Label(bed_info_frame, text=bed_info_text,
                                      font=("Avenir LT Std 65 Medium", 10), anchor="w", fg="#19345D",
                                      bg="#ECF6FF", justify="left")
            bed_info_label.pack(side="left", padx=30)

        # Update the canvas scroll region
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))

        # Bind the canvas to the scroll bar
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # Configure the scroll bar to work with the canvas
        scrollbar.configure(command=canvas.yview)

        # Configure the canvas height
        canvas.configure(height=canvas_height)

        # Create a frame for the footer
        footer_frame = tk.Frame(self, bg="white")
        footer_frame.pack(side="bottom")

        # Add the address and telephone number in the footer
        address_frame = tk.Frame(footer_frame, bg="white")
        address_frame.pack(side="left", anchor="ne", padx=10)

        telephone_frame = tk.Frame(footer_frame, bg="white")
        telephone_frame.pack(side="right", anchor="sw", padx=40)

        # Emoji label for address
        emoji_address_label = tk.Label(address_frame, text="📍", font=("Arial", 16), fg='#1D509D', bg="white")
        emoji_address_label.pack(side="left")

        # Text label for address
        address_label = tk.Label(address_frame, text="Commonwealth, Quezon City", font=("Avenir LT Std 65 Medium", 10),
                                 fg="#1D509D", bg="white")
        address_label.pack(side="left")

        # Emoji label for telephone
        emoji_telephone_label = tk.Label(telephone_frame, text="📞", font=("Arial", 16), fg='#1D509D', bg="white")
        emoji_telephone_label.pack(side="left")

        # Text label for telephone
        telephone_label = tk.Label(telephone_frame, text="123-456-789", font=("Avenir LT Std 65 Medium", 10), fg="#1D509D",
                                   bg="white")
        telephone_label.pack(side="left")

        back_button = tk.Button(self, text="Back", command=self.destroy, font=("Avenir LT Std 65 Medium", 10), fg='#1D509D')
        back_button.pack(anchor="se", padx=20, pady=10)


class AdminWindow(tk.Toplevel):
    global login_window  # Declare login_window as a global variable
    global ward_info
    def __init__(self, login_window, admin_record):
        super().__init__(login_window)
        self.login_window = login_window
        self.title("Admin Window")
        self.geometry("1920x1080")
        self.configure(bg="#ECF6FF")
        self.admin_record = admin_record
        self.ward_info = []  # Declare ward_info as a class-level variable
        self.ward_frames = []   # Initialize ward_frames as an empty list
        login_window.withdraw()

        # Create a frame for the header
        self.header_frame = tk.Frame(self, bg="#ECF6FF")
        self.header_frame.pack(side="top", fill="x", pady=(0, 5))  # Adjust the pady value as needed

        # Add the CHOSP logo
        logo_image = Image.open("CHOSP.png")
        logo_image = logo_image.resize((120, 70))
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self.header_frame, image=logo_photo, bg="#ECF6FF")
        logo_label.image = logo_photo
        logo_label.pack(side="right")

        # Create a frame for the header labels (header and subheading)
        header_labels_frame = tk.Frame(self.header_frame, bg="#ECF6FF")
        header_labels_frame.pack(side="right", anchor="ne")

        # Add the header label
        header_label = tk.Label(header_labels_frame, text="Cherry Hospital", font=("Proxima Nova Rg", 27, "bold"),
                                fg="#1D509D", bg="#ECF6FF")
        header_label.pack(side="top", anchor="ne")

        # Add the subheading label
        subheader_label = tk.Label(header_labels_frame, text="A Cherry a Day Keeps Doc J Away",
                                   font=("Avenir LT Std 65 Medium", 9, "bold"),
                                   fg="#1D509D", bg="#ECF6FF")
        subheader_label.pack(side="top", anchor="ne")

        # Create a frame for the logout button
        logout_frame = tk.Frame(self.header_frame, bg="#ECF6FF")
        logout_frame.pack(side="left")

        # Add the logout button
        logout_button = tk.Button(logout_frame, text="Logout", font=("Avenir LT Std 65 Medium", 10, "bold"),
                                  fg="#1D509D", bg="#ECF6FF", command=self.go_back)
        logout_button.pack(side="left", padx=10)

        # Add the divider line
        divider_line = tk.Frame(self, height=2, bg="#1D509D")
        divider_line.pack(fill="x")

        # Create a frame for the content
        self.content_frame = tk.Frame(self, bg="#ECF6FF")
        self.content_frame.pack(fill="both", expand=False)

        # Create a frame for the "WARD" label and rectangles
        ward_frame = tk.Frame(self.content_frame, bg="#ECF6FF")
        ward_frame.pack(side="bottom", anchor="w")

        # Add the "WARD" label
        ward_label = tk.Label(ward_frame, text="WARD", font=("Avenir LT Std 65 Medium", 20, "bold"), fg="#1D509D",
                              bg="#ECF6FF")
        ward_label.pack(side="left", padx=(220,0), pady=10)

        # Add a button to open the "Add New Ward" window
        add_ward_button = tk.Button(ward_frame, text="Add New Ward", font=("Avenir LT Std 65 Medium", 12),
                                    fg="#2D9D49", bg="white", command=self.add_new_ward)
        add_ward_button.pack(side="left", padx=20, pady=10)  # You can adjust padx as needed

        # Create a canvas to hold the rectangles and add a scrollbar
        canvas_frame = tk.Frame(self, bg="#ECF6FF")
        canvas_frame.pack(side="top", fill="both", expand=True, padx=280, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg="#ECF6FF")
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind_all("<MouseWheel>",
                             lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame to hold the rectangles
        self.rectangles_frame = tk.Frame(self.canvas, bg="#ECF6FF")
        self.canvas.create_window((0, 0), window=self.rectangles_frame, anchor="nw")

        # Load ward data when the Admin window is created
        self.load_ward_data()

    def add_new_ward(self):
        def add_ward_to_database():
            ward_id = ward_id_entry.get()
            ward_location = ward_location_entry.get()
            ward_status = ward_status_combobox.get()
            ward_beds = ward_beds_combobox.get()
            ward_type = ward_type_combobox.get()
            ward_last_update = ward_last_update_entry.get()

            # Insert the new ward into the database using the insert_new_ward function
            insert_new_ward(ward_id, ward_location, ward_status, ward_beds, ward_type, ward_last_update)

            # Refresh the view to show the newly added ward
            self.load_ward_data()

            # Close the add_ward_window
            add_ward_window.destroy()

            # Show the "update successfully" message box
            messagebox.showinfo("Success!", "New ward added successfully!")

            # Refresh the view to show the newly added ward
            self.refresh_ward_data()

        # Create a new window for adding a ward
        add_ward_window = tk.Toplevel(self)
        add_ward_window.title("Add New Ward")
        add_ward_window.geometry("370x500")
        add_ward_window.configure(bg="#ECF6FF")

        # Add the CHOSP logo
        logo_image = Image.open("CHOSP.png")
        logo_image = logo_image.resize((220, 125))
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(add_ward_window, image=logo_photo, bg="#ECF6FF")
        logo_label.image = logo_photo
        logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # WARD ID
        ward_id_label = tk.Label(add_ward_window, text="Ward ID:", font=("Avenir LT Std 65 Medium", 12), fg="#1D509D",
                                 bg="#ECF6FF")
        ward_id_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ward_id_entry = tk.Entry(add_ward_window, font=("Avenir LT Std 65 Medium", 12))
        ward_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # WARD LOCATION
        ward_location_label = tk.Label(add_ward_window, text="Ward Location:", font=("Avenir LT Std 65 Medium", 12),
                                       fg="#1D509D", bg="#ECF6FF")
        ward_location_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ward_location_entry = tk.Entry(add_ward_window, font=("Avenir LT Std 65 Medium", 12))
        ward_location_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        # WARD STATUS
        ward_status_label = tk.Label(add_ward_window, text="Ward Status:", font=("Avenir LT Std 65 Medium", 12),
                                     fg="#1D509D", bg="#ECF6FF")
        ward_status_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ward_status_combobox = ttk.Combobox(add_ward_window, font=("Avenir LT Std 65 Medium", 12),
                                            values=["Available", "Unavailable", "Under Maintenance"],
                                            state="readonly")
        ward_status_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="we")

        # BEDS
        ward_beds_label = tk.Label(add_ward_window, text="Beds:", font=("Avenir LT Std 65 Medium", 12),
                                   fg="#1D509D", bg="#ECF6FF")
        ward_beds_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        ward_beds_combobox = ttk.Combobox(add_ward_window, font=("Avenir LT Std 65 Medium", 12),
                                          values=["1", 2, 3, 4, 5, 6, 7, 8, 9],
                                          state="readonly")
        ward_beds_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="we")

        # WARD TYPE
        ward_type_label = tk.Label(add_ward_window, text="Ward Type:", font=("Avenir LT Std 65 Medium", 12),
                                   fg="#1D509D", bg="#ECF6FF")
        ward_type_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        ward_type_combobox = ttk.Combobox(add_ward_window, font=("Avenir LT Std 65 Medium", 12),
                                          values=["Public", "Private"],
                                          state="readonly")
        ward_type_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="we")

        # WARD LAST UPDATE
        ward_last_update_label = tk.Label(add_ward_window, text="Last Update:", font=("Avenir LT Std 65 Medium", 12),
                                          fg="#1D509D", bg="#ECF6FF")
        ward_last_update_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")
        ward_last_update_entry = tk.Entry(add_ward_window, font=("Avenir LT Std 65 Medium", 12))
        ward_last_update_entry.grid(row=6, column=1, padx=5, pady=5, sticky="we")

        # Save button
        save_button = tk.Button(add_ward_window, text="Save", font=("Avenir LT Std 65 Medium", 12),
                                fg="#2D9D49", bg="white",
                                command=add_ward_to_database)
        save_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    def load_ward_data(self):
        for ward_frame in self.ward_frames:
            ward_frame.destroy()
        self.ward_frames = []

        # Create rectangles for each ward
        self.ward_info = fetch_ward_info()
        for row, ward in enumerate(self.ward_info):
            ward_frame = tk.Frame(self.rectangles_frame, bg="white", padx=10, pady=10, relief="solid", bd=1)
            ward_frame.grid(row=row, column=0, padx=50, pady=50, sticky="ew")

            ward_label = tk.Label(ward_frame, text="Ward ID", font=("Avenir LT Std 65 Medium", 12, "bold"),
                                  fg="#1D509D", bg="white")
            ward_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            ward_id_var = tk.StringVar()
            ward_id_var.set(ward.get("Ward ID", ""))
            ward_id_entry = tk.Entry(ward_frame, font=("Avenir LT Std 65 Medium", 12), textvariable=ward_id_var, bd=1,
                                     relief="solid",
                                     width=7)
            ward_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            info_frame = tk.Frame(ward_frame, bg="white")
            info_frame.grid(row=0, column=1, padx=100, pady=5, sticky="nsew")

            ward_type_label = tk.Label(info_frame, text="Ward Type", font=("Avenir LT Std 65 Medium", 12, "bold"),
                                       fg="#1D509D",
                                       bg="white")
            ward_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            ward_type_var = tk.StringVar()
            ward_type_var.set(ward["Ward Type"])
            ward_type_combobox = ttk.Combobox(info_frame, font=("Avenir LT Std 65 Medium", 12),
                                              textvariable=ward_type_var,
                                              state="readonly")
            ward_type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")
            ward_type_combobox['values'] = ["Public", "Private"]

            if "Ward Status" in ward:
                status_label = tk.Label(info_frame, text="Status", font=("Avenir LT Std 65 Medium", 12, "bold"),
                                        fg="#1D509D", bg="white")
                status_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

                status_var = tk.StringVar()
                status_var.set(ward["Ward Status"])
                status_combobox = ttk.Combobox(info_frame, font=("Avenir LT Std 65 Medium", 12),
                                               textvariable=status_var,
                                               state="readonly")
                status_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")
                status_combobox['values'] = ["Available", "Unavailable", "Under Maintenance"]

            beds_label = tk.Label(info_frame, text="Beds", font=("Avenir LT Std 65 Medium", 12, "bold"), fg="#1D509D",
                                  bg="white")
            beds_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

            bed_details_button = tk.Button(info_frame, text="Bed Details", font=("Avenir LT Std 65 Medium", 12),
                                           fg="#2D9D49", bg="white",
                                           command=lambda ward=ward: self.open_bed_details_window(ward))
            bed_details_button.grid(row=2, column=1, padx=5, pady=5, sticky="we")

            # Save button
            save_button = tk.Button(ward_frame, text="Save", font=("Avenir LT Std 65 Medium", 12),
                                    fg="#2D9D49",
                                    bg="white",
                                    command=self.create_save_function(ward, ward_type_combobox, status_combobox))
            save_button.grid(row=3, column=0, columnspan=2, padx=20, pady=10,
                             sticky="e")  # Use grid manager for the save button

            self.ward_frames.append(ward_frame)  # Append the ward frame to the list

            # Delete button
            delete_button = tk.Button(ward_frame, text=" 🗑️", font=("Avenir LT Std 65 Medium", 12),
                                      fg="#D33E3D", bg="white",
                                      command=lambda ward=ward: self.delete_ward(ward))
            delete_button.grid(row=0, column=0, columnspan=2, padx=20, pady=0,
                               sticky="ne")  # Use grid manager for the delete button

        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_save_function(self, ward, ward_type_combobox, status_combobox):
        def save_changes():
            self.update_database_and_refresh_view(
                ward, ward_type_combobox, status_combobox)

            # Show the "update successfully" message box
            messagebox.showinfo("Success", "Update Successfully")

        return save_changes

    def update_ward_frames(self):
        # Clear the list
        self.ward_frames = []

        # Use grid layout instead of pack for the ward frames inside the canvas
        for row, ward_frame in enumerate(self.ward_frames):
            ward_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")

        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def go_back(self):
        self.destroy()
        self.login_window.deiconify()

    def open_bed_details_window(self, ward):
        bed_details_window = BedDetailsWindow(self, ward)
        self.wait_window(bed_details_window)

    def update_database_and_refresh_view(self, ward, ward_type_combobox, status_combobox):
        ward_id = ward.get("Ward ID")
        ward_type = ward_type_combobox.get()
        ward_status = status_combobox.get() if "Ward Status" in ward else None

        # Call the update_ward_details function to update the ward in the database
        update_ward_details(ward_id, ward_type=ward_type, ward_status=ward_status)

    def refresh_ward_data(self):
        # Clear the existing ward frames before reloading the data
        for ward_frame in self.ward_frames:
            ward_frame.destroy()
        self.ward_frames = []

        # Load the ward data again
        self.load_ward_data()

    def delete_ward_from_database(self, ward_id):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM WARD WHERE ward_id = ?", (ward_id,))
        conn.commit()
        conn.close()

    def update_ward_frames_after_deletion(self):
        # Clear the list
        self.ward_frames = []

        # Load the ward data again to reflect the changes
        self.load_ward_data()

        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def delete_ward(self, ward):
        confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to delete this ward?")

        if confirmed:
            ward_id = ward.get("Ward ID")
            # Delete the ward from the database
            self.delete_ward_from_database(ward_id)

            # Update the ward_info list to reflect the changes
            self.ward_info = [w for w in self.ward_info if w.get("Ward ID") != ward_id]

            # Remove the ward frame from the interface
            ward_frame_to_remove = None
            for ward_frame in self.ward_frames:
                if ward_frame.winfo_exists() and ward_frame.winfo_class() == 'Frame':
                    # Check if the frame exists to avoid any exceptions
                    if ward_frame.grid_info():
                        # Check if the frame is still visible in the grid
                        ward_index = ward_frame.grid_info()["row"]
                        if ward_index < len(self.ward_info):
                            # Make sure the index is valid for ward_info
                            if self.ward_info[ward_index].get("Ward ID") == ward_id:
                                # The ward frame to remove is found
                                ward_frame_to_remove = ward_frame
                                break

            if ward_frame_to_remove:
                ward_frame_to_remove.destroy()
                self.ward_frames.remove(ward_frame_to_remove)

            # Show the "update successfully" message box
            messagebox.showinfo("Success", "Deleted Successfully")

            # Update the canvas scroll region after deletion
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            # Refresh the view to reflect the updated data
            self.load_ward_data()


def login():
    username = username_entry.get()
    password = password_entry.get()

    # Check if the username and password are correct
    admin_record = check_admin_credentials(username, password)

    if admin_record:
        admin_window = AdminWindow(login_window, admin_record)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


class BedDetailsWindow(tk.Toplevel):
    global login_window  # Declare login_window as a global variable
    global ward_info
    def __init__(self, admin_window, ward):
        super().__init__(admin_window)
        self.admin_window = admin_window
        self.ward = ward
        self.title("Bed Details")
        self.geometry("1920x1080")
        self.configure(bg="#ECF6FF")
        self.bed_info = []
        self.bed_frames = []

        # Create a frame for the header
        self.header_frame = tk.Frame(self, bg="#ECF6FF")
        self.header_frame.pack(side="top", fill="x", pady=(0, 5))  # Adjust the pady value as needed

        # Add the CHOSP logo
        logo_image = Image.open("CHOSP.png")
        logo_image = logo_image.resize((120, 70))
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self.header_frame, image=logo_photo, bg="#ECF6FF")
        logo_label.image = logo_photo
        logo_label.pack(side="right")

        # Create a frame for the header labels (header and subheading)
        header_labels_frame = tk.Frame(self.header_frame, bg="#ECF6FF")
        header_labels_frame.pack(side="right", anchor="ne")

        # Add the header label
        header_label = tk.Label(header_labels_frame, text="Cherry Hospital", font=("Proxima Nova Rg", 27, "bold"),
                                fg="#1D509D", bg="#ECF6FF")
        header_label.pack(side="top", anchor="ne")

        # Add the subheading label
        subheader_label = tk.Label(header_labels_frame, text="A Cherry a Day Keeps Doc J Away",
                                   font=("Avenir LT Std 65 Medium", 9, "bold"),
                                   fg="#1D509D", bg="#ECF6FF")
        subheader_label.pack(side="top", anchor="ne")

        # Create a frame for the back button
        back_frame = tk.Frame(self.header_frame, bg="#ECF6FF")
        back_frame.pack(side="left")

        # Add the back button
        back_button = tk.Button(back_frame, text="Back", font=("Avenir LT Std 65 Medium", 10),
                                  fg="#1D509D", bg="#ECF6FF", command=self.go_back)
        back_button.pack(side="left", padx=10)

        # Add the divider line
        divider_line = tk.Frame(self, height=2, bg="#1D509D")
        divider_line.pack(fill="x")

        # Create a frame for the content
        self.content_frame = tk.Frame(self, bg="#ECF6FF")
        self.content_frame.pack(fill="both", expand=False)
        # Create a frame for the "BED" label and rectangles
        bed_frame = tk.Frame(self.content_frame, bg="#ECF6FF")
        bed_frame.pack(side="bottom", anchor="w")

        # Add the "BEDS (Ward ID)" label
        beds_label = tk.Label(bed_frame, text=f"BEDS ({self.ward['Ward ID']})",
                              font=("Avenir LT Std 65 Medium", 20, "bold"),
                              fg="#1D509D", bg="#ECF6FF")
        beds_label.pack(side="left", padx=(20,0), pady=10)

        # Add a button to open the "Add New Bed" window
        add_bed_button = tk.Button(bed_frame, text="Add New Bed", font=("Avenir LT Std 65 Medium", 10),
                                   fg="#2D9D49", bg="white", command=self.add_new_bed)
        add_bed_button.pack(side="left", padx=20, pady=2)  # You can adjust padx as needed

        # Create a canvas to hold the rectangles and add a scrollbar
        canvas_frame = tk.Frame(self, bg="#ECF6FF")
        canvas_frame.pack(side="top", fill="both", expand=True, padx=0, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg="#ECF6FF")
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind_all("<MouseWheel>",
                             lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame to hold the rectangles
        self.rectangles_frame = tk.Frame(self.canvas, bg="#ECF6FF")
        self.canvas.create_window((0, 0), window=self.rectangles_frame, anchor="nw")

        # Load ward data when the Admin window is created
        self.load_bed_data()

    def save_bed_to_database(self, bed_id, location_row, location_column, status, size):
        # Insert the new bed into the database using the insert_new_bed function
        insert_new_bed(bed_id, self.ward["Ward ID"], location_row, location_column, status, size)

        # Refresh the view to show the newly added bed
        self.refresh_bed_data()

    def add_new_bed(self):
        def save_bed():
            bed_id = bed_id_entry.get()
            location_row = location_row_entry.get()
            location_column = location_column_entry.get()
            status = status_combobox.get()
            size = size_combobox.get()

            # Insert the new bed into the database using the insert_new_bed function
            insert_new_bed(bed_id, self.ward["Ward ID"], location_row, location_column, status, size)

            # Refresh the view to show the newly added bed
            self.refresh_bed_data()

            # Show the "update successfully" message box
            messagebox.showinfo("Success", "New Bed Added Successfully!")

            # Close the add_bed_window
            add_bed_window.destroy()

        add_bed_window = tk.Toplevel(self)
        add_bed_window.title("Add New Bed")
        add_bed_window.geometry("370x400")
        add_bed_window.configure(bg="#ECF6FF")

        # Add the CHOSP logo
        logo_image = Image.open("CHOSP.png")
        logo_image = logo_image.resize((225, 125))
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(add_bed_window, image=logo_photo, bg="#ECF6FF")
        logo_label.image = logo_photo
        logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # BED ID
        bed_id_label = tk.Label(add_bed_window, text="Bed ID:", font=("Avenir LT Std 65 Medium", 12), fg="#1D509D", bg="#ECF6FF")
        bed_id_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        bed_id_entry = tk.Entry(add_bed_window, font=("Avenir LT Std 65 Medium", 12))
        bed_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # BED LOCATION ROW
        location_row_label = tk.Label(add_bed_window, text="Location Row:", font=("Avenir LT Std 65 Medium", 12), fg="#1D509D", bg="#ECF6FF")
        location_row_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        location_row_entry = tk.Entry(add_bed_window, font=("Avenir LT Std 65 Medium", 12))
        location_row_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        # BED LOCATION COLUMN
        location_column_label = tk.Label(add_bed_window, text="Location Column:", font=("Avenir LT Std 65 Medium", 12), fg="#1D509D", bg="#ECF6FF")
        location_column_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        location_column_entry = tk.Entry(add_bed_window, font=("Avenir LT Std 65 Medium", 12))
        location_column_entry.grid(row=3, column=1, padx=5, pady=5, sticky="we")

        # BED STATUS
        status_label = tk.Label(add_bed_window, text="Status:", font=("Avenir LT Std 65 Medium", 12), fg="#1D509D", bg="#ECF6FF")
        status_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        status_combobox = ttk.Combobox(add_bed_window, font=("Avenir LT Std 65 Medium", 12),
                                       values=["Available", "Occupied"], state="readonly")
        status_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="we")

        # BED SIZE
        size_label = tk.Label(add_bed_window, text="Size:", font=("Avenir LT Std 65 Medium", 12), fg="#1D509D", bg="#ECF6FF")
        size_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        size_combobox = ttk.Combobox(add_bed_window, font=("Avenir LT Std 65 Medium", 12),
                                     values=["Full", "Fully-Electric", "Queen"], state="readonly")
        size_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="we")

        # Save button sa add new ward
        save_button = tk.Button(add_bed_window, text="Save", font=("Avenir LT Std 65 Medium", 12), fg="#2D9D49",
                                bg="white", command=save_bed)
        save_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    def load_bed_data(self):
        for bed_frame in self.bed_frames:
            bed_frame.destroy()
        self.bed_frames = []

        # Fetch the bed information from the database for the selected ward
        bed_info = fetch_bed_info(self.ward["Ward ID"])

        for bed_index, bed in enumerate(bed_info):
            bed_frame = tk.Frame(self.rectangles_frame, bg="white", padx=0, pady=10, relief="solid", bd=1)
            bed_frame.grid(row=bed_index, column=0, padx=0, pady=15, sticky="ew")

            bed_id_label = tk.Label(bed_frame, text="Bed ID", font=("Avenir LT Std 65 Medium", 12, "bold"),
                                    fg="#1D509D",
                                    bg="white")
            bed_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            bed_id_var = tk.StringVar()
            bed_id_var.set(bed.get("Bed ID", ""))
            bed_id_entry = tk.Entry(bed_frame, font=("Avenir LT Std 65 Medium", 12), textvariable=bed_id_var, bd=1,
                                    relief="solid",
                                    width=7)
            bed_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            location_row_label = tk.Label(bed_frame, text="Location Row", font=("Avenir LT Std 65 Medium", 12, "bold"),
                                          fg="#1D509D", bg="white")
            location_row_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

            location_row_var = tk.StringVar()
            location_row_var.set(bed.get("Location Row", ""))
            location_row_entry = tk.Entry(bed_frame, font=("Avenir LT Std 65 Medium", 12),
                                          textvariable=location_row_var, bd=1,
                                          relief="solid", width=7)
            location_row_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

            location_column_label = tk.Label(bed_frame, text="Location Column",
                                             font=("Avenir LT Std 65 Medium", 12, "bold"),
                                             fg="#1D509D", bg="white")
            location_column_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")

            location_column_var = tk.StringVar()
            location_column_var.set(bed.get("Location Column", ""))
            location_column_entry = tk.Entry(bed_frame, font=("Avenir LT Std 65 Medium", 12),
                                             textvariable=location_column_var,
                                             bd=1, relief="solid", width=7)
            location_column_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

            status_label = tk.Label(bed_frame, text="Status", font=("Avenir LT Std 65 Medium", 12, "bold"),
                                    fg="#1D509D",
                                    bg="white")
            status_label.grid(row=0, column=6, padx=5, pady=5, sticky="w")
            status_var = tk.StringVar()
            status_var.set(bed.get("Status", ""))
            status_combobox = ttk.Combobox(bed_frame, font=("Avenir LT Std 65 Medium", 12), textvariable=status_var,
                                           state="readonly")
            status_combobox.grid(row=0, column=7, padx=5, pady=5, sticky="we")
            status_combobox['values'] = ["Available", "Occupied", "Sanitize"]

            size_label = tk.Label(bed_frame, text="Size", font=("Avenir LT Std 65 Medium", 12, "bold"), fg="#1D509D",
                                  bg="white")
            size_label.grid(row=0, column=8, padx=5, pady=5, sticky="w")

            size_var = tk.StringVar()
            size_var.set(bed.get("Size", ""))
            size_combobox = ttk.Combobox(bed_frame, font=("Avenir LT Std 65 Medium", 12), textvariable=size_var,
                                         state="readonly")
            size_combobox.grid(row=0, column=9, padx=5, pady=5, sticky="we")
            size_combobox['values'] = ["Full", "Fully-Electric", "Queen"]

            # Save button sa edit ward
            save_button = tk.Button(bed_frame, text="Save", font=("Avenir LT Std 65 Medium", 12), fg="#2D9D49",
                                    bg="white",
                                    command=lambda b=bed, bed_id_entry=bed_id_entry,
                                                   location_row_entry=location_row_entry,
                                                   location_column_entry=location_column_entry,
                                                   status_combobox=status_combobox,
                                                   size_combobox=size_combobox: self.create_save_function_for_bed(
                                        b, bed_id_entry, location_row_entry, location_column_entry,
                                        status_combobox, size_combobox)())
            save_button.grid(row=0, column=10, padx=20, pady=10, sticky="e")  # Use grid manager for the save button

            self.bed_frames.append(bed_frame)  # Append the bed frame to the list

            # Delete button
            delete_button = tk.Button(bed_frame, text="   🗑️", font=("Avenir LT Std 65 Medium", 12), fg="#D33E3D",
                                      bg="white",
                                      command=lambda b=bed: self.delete_bed(b))
            delete_button.grid(row=0, column=11, padx=10, pady=10, sticky="ne")  # Use grid manager for the delete button

        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_save_function_for_bed(self, bed, bed_id_entry, location_row_entry,
                                     location_column_entry, status_combobox, size_combobox):
        def save_changes(b=bed):  # Use a default argument to capture the current bed
            bed_id = bed_id_entry.get()
            location_row = location_row_entry.get()
            location_column = location_column_entry.get()
            status = status_combobox.get()
            size = size_combobox.get()

            # Update the bed information in the database using the update_bed_details function
            update_bed_details(bed_id, location_row, location_column, status, size)

            # Refresh the view to show the updated bed details
            self.refresh_bed_data()

        return save_changes

    def update_bed_frames(self):
        # Clear the list
        self.bed_frames = []

        # Load bed data when updating bed frames
        self.load_bed_data()

    def go_back(self):
        self.destroy()
        self.login_window.deiconify()

    def update_database_and_refresh_view(self, bed, status_combobox, size_combobox):
        bed_id = bed.get("Bed ID")
        location_row = bed.get("Location Row")
        location_column = bed.get("Location Column")
        status = status_combobox.get()
        size = size_combobox.get()

        # Call the update_bed_details function to update the bed in the database
        update_bed_details(bed_id, location_row, location_column, status, size)

        # Optionally, refresh the bed data to show the updated information immediately
        self.refresh_bed_data()

    def refresh_bed_data(self):
        for bed_frame in self.bed_frames:
            bed_frame.destroy()
        self.bed_frames = []

        # Load the ward data again
        self.load_bed_data()

    def delete_bed_from_database(self, bed_id):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM BEDS WHERE bed_id = ?", (bed_id,))
        conn.commit()
        conn.close()

    def update_ward_frames_after_deletion(self):
        # Clear the list
        self.bed_frames = []

        # Load the ward data again to reflect the changes
        self.load_bed_data()

        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def delete_bed(self, bed):
        confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to delete this bed?")
        if confirmed:
            bed_id = bed["Bed ID"]

            # Delete the bed from the database
            self.delete_bed_from_database(bed_id)

            # Remove the bed from the bed_info list
            self.bed_info = [b for b in self.bed_info if b["Bed ID"] != bed_id]

            # Remove the bed frame from the interface
            bed_frame_to_remove = None
            for bed_frame in self.bed_frames:
                if bed_frame.winfo_exists() and bed_frame.winfo_class() == 'Frame':
                    # Check if the frame exists to avoid any exceptions
                    if bed_frame.grid_info():
                        # Check if the frame is still visible in the grid
                        bed_index = bed_frame.grid_info()["row"]
                        if bed_index < len(self.bed_info):
                            # Make sure the index is valid for bed_info
                            if self.bed_info[bed_index]["Bed ID"] == bed_id:
                                # The bed frame to remove is found
                                bed_frame_to_remove = bed_frame
                                break

            if bed_frame_to_remove:
                bed_frame_to_remove.destroy()
                self.bed_frames.remove(bed_frame_to_remove)

            # Update the canvas scroll region after deletion
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            # Show the "update successfully" message box
            messagebox.showinfo("Success", "Bed deleted successfully")

            # Refresh the view to reflect the updated data
            self.load_bed_data()

    def on_canvas_configure(self, event):
        # Update the canvas scroll region when the canvas is resized
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_save_bed_details(self, bed):
        # Get the updated information from the entry fields or comboboxes
        updated_bed_id = bed['Bed ID']
        updated_location_row = bed['Location Row']
        updated_location_column = bed['Location Column']
        updated_status = bed['Status']
        updated_size = bed['Size']

        # Update the database using the update_bed_details function
        update_bed_details(updated_bed_id, updated_location_row, updated_location_column,
                           updated_status, updated_size)

        # Optionally, refresh the bed data to show the updated information immediately
        self.refresh_bed_data()

# Create the login window
login_window, username_entry, password_entry = create_login_window()

# Run the login window event loop
login_window.mainloop()