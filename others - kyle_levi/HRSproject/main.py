import tkinter as tk
import sqlite3
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta
from time import strftime, localtime
import sys
import re
import io
import subprocess
from tkinter import filedialog
from dateutil.relativedelta import relativedelta
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

login_attempts = 0
def login():
    global login_attempts

    username = entry_username.get()
    password = entry_password.get()

    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Success", "Login successful!")
        conn.close()
        hide_login_form()
    else:
        login_attempts += 1
        if login_attempts >= 3:
            messagebox.showerror("Error", "Invalid username or password. Maximum login attempts exceeded.")
            conn.close()
            sys.exit()  # Close the program
        else:
            remaining_attempts = 3 - login_attempts
            messagebox.showerror("Error", f"Invalid username or password. {remaining_attempts} attempts remaining.")
            login_register_clear_entries()
            conn.close()

def get_admin_password():
    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Fetch the first entry from the users table
    cursor.execute("SELECT password FROM users LIMIT 1")
    admin_password = cursor.fetchone()

    # Close the database connection
    conn.close()

    return admin_password[0] if admin_password else None

def validate_admin_password():
    # Get the entered admin password
    entered_password = entry_admin.get()

    # Get the admin password from the database
    admin_password = get_admin_password()

    if admin_password is None:
        # Call the function to display the pending registrations
        show_registration_form()
        messagebox.showinfo("Success", "Welcome to Registration!")
    elif admin_password is not None and entered_password == admin_password:
        show_registration_form()
        messagebox.showinfo("Success", "Welcome to Registration!")
    else:
        messagebox.showerror("Error", "Invalid admin password")
        login_register_clear_entries()

def calculate_age(birthday_str):
    try:
        birthday_date = datetime.strptime(birthday_str, "%Y-%m-%d")
        current_date = datetime.now()
        age = current_date.year - birthday_date.year - ((current_date.month, current_date.day) < (birthday_date.month, birthday_date.day))
        return age
    except ValueError:
        return None

def calculate_age_from_event(event):
    # Get the birthday from the entry_birthday widget
    birthday = entry_birthday.get()

    # Calculate the age from the birthday
    age = calculate_age(birthday)

    # Update the entry_age widget with the calculated age
    if age is not None:
        entry_age.delete(0, tk.END)
        entry_age.insert(0, age)

def add_user():
    firstname = entry_firstname.get()
    lastname = entry_lastname.get()
    middlename = entry_middlename.get()
    birthday = entry_birthday.get()
    gender = combo_gender.get()
    address = entry_address.get()
    username = entry_regusername.get()
    password = entry_regpassword.get()
    email = entry_email.get()

    if not firstname or not lastname or not birthday or not gender or not address or not username or not password or not email:
        messagebox.showerror("Error", "Please fill in all fields")
        return
    if not validate_alphanumeric_with_letter(firstname):
        messagebox.showerror("Error", "First name must contain at least one letter and only alphanumeric characters")
        return
    if not validate_alphanumeric_with_letter(lastname):
        messagebox.showerror("Error", "Last name must contain at least one letter and only alphanumeric characters")
        return
    if not validate_nullable_alphanumeric_with_letter(middlename):
        messagebox.showerror("Error", "Middle Name must contain at least one letter and only alphanumeric characters")
        return
    if not is_valid_date(birthday):
        messagebox.showerror("Error", "Invalid Birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    age = calculate_age(birthday)
    if age is None:
        messagebox.showerror("Error", "Invalid Birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    entry_age.delete(0, tk.END)
    entry_age.insert(0, age)

    if not has_letter(address):
        messagebox.showerror("Error", "Address must contain at least one letter")
        return
    if not has_letter(username):
        messagebox.showerror("Error", "Username must contain at least one letter")
        return
    if not has_letter(password):
        messagebox.showerror("Error", "Password must contain at least one letter")
        return
    if not has_letter(email):
        messagebox.showerror("Error", "Email must contain at least one letter")
        return

    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve the current maximum tenant_id from the database
    cursor.execute("SELECT MAX(userID) FROM users")
    max_user_id = cursor.fetchone()[0]

    # If max_house_id is None (no records in the table), set it to 0
    if max_user_id is None:
        max_user_id = 0

    # Calculate the next tenant_id
    next_use_id = max_user_id + 1

    cursor.execute("INSERT INTO users (userID, firstname, lastname, middlename, birthday, age, gender, address, username, password, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (next_use_id, firstname, lastname, middlename, birthday, age, gender, address, username, password, email))
    conn.commit()
    messagebox.showinfo("Success", "Registration successful!")

    login_register_clear_entries()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_user.delete(*tree_user.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for user in users:
        user_with_zeros = ("{:04d}".format(user[0]),) + user[1:]
        tree_user.insert("", tk.END, values=user_with_zeros)

    conn.close()

def populate_entry_user_fields(event):
    # Get the selected item from the Treeview
    user_selected_item = tree_user.selection()
    if user_selected_item:
        # Extract data from the selected item
        _, firstname, lastname, middlename, birthday, age, gender, address, username, password, email = tree_user.item(user_selected_item, "values")

        # Populate the entry fields with the selected record's data
        entry_firstname.delete(0, tk.END)
        entry_firstname.insert(0, firstname)
        entry_lastname.delete(0, tk.END)
        entry_lastname.insert(0, lastname)
        entry_middlename.delete(0, tk.END)
        entry_middlename.insert(0, middlename)
        entry_birthday.delete(0, tk.END)
        entry_birthday.insert(0, birthday)
        entry_age.delete(0, tk.END)
        entry_age.insert(0, age)
        combo_gender.set(gender)
        entry_address.delete(0, tk.END)
        entry_address.insert(0, address)
        entry_regusername.delete(0, tk.END)
        entry_regusername.insert(0, username)
        entry_regpassword.delete(0, tk.END)
        entry_regpassword.insert(0, password)
        entry_email.delete(0, tk.END)
        entry_email.insert(0, email)

def update_user():
    # Retrieve input values
    firstname = entry_firstname.get()
    lastname = entry_lastname.get()
    middlename = entry_middlename.get()
    birthday = entry_birthday.get()
    address = entry_address.get()
    username = entry_regusername.get()
    password = entry_regpassword.get()
    email = entry_email.get()

    # Get the selected item from the Treeview
    user_selected_item = tree_user.selection()

    if not user_selected_item:
        messagebox.showerror("Error", "Please select a tenant to update")
        return

    age = calculate_age(birthday)
    if age is None:
        messagebox.showerror("Error", "Invalid Birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    entry_age.delete(0, tk.END)
    entry_age.insert(0, age)

    if not validate_alphanumeric_with_letter(firstname):
        messagebox.showerror("Error", "First name must contain at least one letter and only alphanumeric characters")
        return
    if not validate_alphanumeric_with_letter(lastname):
        messagebox.showerror("Error", "Last name must contain at least one letter and only alphanumeric characters")
        return
    if not validate_nullable_alphanumeric_with_letter(middlename):
        messagebox.showerror("Error", "Middle Name must contain at least one letter and only alphanumeric characters")
        return
    if not is_valid_date(birthday):
        messagebox.showerror("Error", "Invalid Birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return
    if not validate_alphanumeric_with_letter(username):
        messagebox.showerror("Error", "Username must contain at least one letter and only alphanumeric characters")
        return
    if not validate_alphanumeric_with_letter(password):
        messagebox.showerror("Error", "Password must contain at least one letter and only alphanumeric characters")
        return
    if not has_letter(address):
        messagebox.showerror("Error", "Address must contain at least one letter")
        return
    if not has_letter(email):
        messagebox.showerror("Error", "Email must contain at least one letter")
        return

    # Retrieve the new values from the entry fields
    firstname = entry_firstname.get()
    lastname = entry_lastname.get()
    middlename = entry_middlename.get()
    birthday = entry_birthday.get()
    gender = combo_gender.get()
    address = entry_address.get()
    username = entry_regusername.get()
    password = entry_regpassword.get()
    email = entry_email.get()

    # Validate input fields
    if not firstname or not lastname or not middlename or not birthday or not age or not gender or not address or not username or not password or not email:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    user_id = tree_user.item(user_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Update the tenant information in the database
    cursor.execute("UPDATE users SET firstname=?, lastname=?, middlename=?, birthday=?, age=?, gender=?, address=?, username=?, password=?, email=? WHERE userID=?",
                   (firstname, lastname, middlename, birthday, age, gender, address, username, password, email, user_id))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "User updated successfully!")

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_user.delete(*tree_user.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for user in users:
        user_with_zeros = ("{:04d}".format(user[0]),) + user[1:]
        tree_user.insert("", tk.END, values=user_with_zeros)

    # Close the database connection
    conn.close()

    login_register_clear_entries()

def delete_user():
    # Get the selected item from the Treeview
    user_selected_item = tree_user.selection()
    if not user_selected_item:
        messagebox.showerror("Error", "Please select a user to delete")
        return

    # Confirm with the user before deleting
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected user?")
    if not confirmation:
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    user_id = tree_user.item(user_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Delete the tenant from the database
    cursor.execute("DELETE FROM userS WHERE userID=?", (user_id,))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "User deleted successfully!")

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_user.delete(*tree_user.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for user in users:
        user_with_zeros = ("{:04d}".format(user[0]),) + user[1:]
        tree_user.insert("", tk.END, values=user_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    login_register_clear_entries()

def search_user():
    # Get the search entry value
    search_value = entry_search_user.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve tenants from the database based on the search_value
    cursor.execute("SELECT * FROM users WHERE firstname LIKE ? OR lastname LIKE ? OR middlename LIKE ? OR birthday LIKE ? OR age LIKE ? OR gender = ? OR address LIKE ? OR username = ? OR password = ? OR email LIKE ? OR userID=?",
                   ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', search_value, '%' + search_value + '%', search_value, search_value, '%' + search_value + '%',  search_value))

    search_result = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_user.delete(*tree_user.get_children())

    # Populate the Treeview with the search result data, adding leading zeros to tenant_id
    for user in search_result:
        user_with_zeros = ("{:04d}".format(user[0]),) + user[1:]
        tree_user.insert("", tk.END, values=user_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    login_register_clear_entries()

def validate_alphanumeric_with_letter(value):
    # Validation function for alphanumeric values with at least one letter
    return bool(re.match("^(?=.*[a-zA-Z])[a-zA-Z0-9 ]*$", value))

def validate_nullable_alphanumeric_with_letter(value):
    if value is None or value.strip() == "":
        return True  # Allow null values
    return bool(re.match("^(?=.*[a-zA-Z])[a-zA-Z0-9 ]*$", value))

def has_letter(value):
    # Check if the value contains at least one letter
    return bool(re.search("[a-zA-Z]", value))

def has_number(value):
    # Check if the input contains only numeric characters
    return value.isdigit()

def is_valid_date(value):
    return bool(re.match("^\d{4}-\d{2}-\d{2}$", value))

def on_validate_input(char):
    # Prevent entry of space character
    if char == " ":
        messagebox.showerror("Error", "Spaces are not allowed in this field.")
        return False
    return True

def populate_treeview():

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()

    cursor.execute("SELECT * FROM house")
    houses = cursor.fetchall()

    cursor.execute("SELECT * FROM lease")
    leases = cursor.fetchall()

    cursor.execute("SELECT * FROM payment")
    payments = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_user.delete(*tree_user.get_children())
    tree_tenant.delete(*tree_tenant.get_children())
    tree_house.delete(*tree_house.get_children())
    tree_lease.delete(*tree_lease.get_children())
    tree_payment.delete(*tree_payment.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for user in users:
        user_with_zeros = ("{:04d}".format(user[0]),) + user[1:]
        tree_user.insert("", tk.END, values=user_with_zeros)

    for tenant in tenants:
        tenant_with_zeros = ("{:04d}".format(tenant[0]),) + tenant[1:]
        tree_tenant.insert("", tk.END, values=tenant_with_zeros)

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for house in houses:
        house_with_zeros = ("{:04d}".format(house[0]),) + house[1:]
        tree_house.insert("", tk.END, values=house_with_zeros)

    for lease in leases:
        lease_with_zeros = ("{:04d}".format(lease[0]), "{:04d}".format(lease[1]), "{:04d}".format(lease[2])) + lease[3:]
        tree_lease.insert("", tk.END, values=lease_with_zeros)

    for payment in payments:
        payment_with_zeros = ("{:04d}".format(payment[0]), "{:04d}".format(payment[1]), "{:04d}".format(payment[2])) + payment[3:]
        tree_payment.insert("", tk.END, values=payment_with_zeros)


    # Close the database connection
    conn.close()

# Clear the entry fields
def login_register_clear_entries():
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_admin.delete(0, tk.END)

    entry_search_user.delete(0, tk.END)
    entry_firstname.delete(0, tk.END)
    entry_lastname.delete(0, tk.END)
    entry_middlename.delete(0, tk.END)
    entry_birthday.delete(0, tk.END)
    combo_gender.set("")
    entry_age.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_regusername.delete(0, tk.END)
    entry_regpassword.delete(0, tk.END)
    entry_email.delete(0, tk.END)

def tenant_clear_entries():
    entry_search.delete(0, tk.END)
    entry_tenant_name.delete(0, tk.END)
    entry_tenant_occupation.delete(0, tk.END)
    entry_tenant_birthday.delete(0, tk.END)
    entry_tenant_age.delete(0, tk.END)
    combo_tenant_gender.set("")
    entry_tenant_email.delete(0, tk.END)
    entry_tenant_phone.delete(0, tk.END)

def house_clear_entries():
    entry_search_house.delete(0, tk.END)
    entry_house_name.delete(0, tk.END)
    entry_house_location.delete(0, tk.END)
    entry_house_rent.delete(0, tk.END)
    combo_house_occupants.set("")
    combo_house_availability.set("")
    text_house_description.delete("1.0", tk.END)

def lease_clear_entries():
    entry_search_lease.delete(0, tk.END)
    combo_house_id.set("")
    combo_tenant_id.set("")
    entry_lease_duration.delete(0, tk.END)
    entry_lease_start_date.delete(0, tk.END)
    entry_lease_end_date.delete(0, tk.END)
    combo_lease_period.set("")
    entry_lease_amount.delete(0, tk.END)
    entry_lease_deposit.delete(0, tk.END)

def payment_clear_entries():
    entry_search_payment.delete(0, tk.END)
    combo_house_payment_id.set("")
    combo_tenant_payment_id.set("")
    entry_payment_amount.delete(0, tk.END)
    combo_payment_method.set("")

def calculate_tenant_age_from_event(event):
    # Get the birthday from the entry_tenant_birthday widget
    birthday = entry_tenant_birthday.get()

    # Calculate the age from the birthday
    age = calculate_age(birthday)

    # Update the entry_tenant_age widget with the calculated age
    if age is not None:
        entry_tenant_age.delete(0, tk.END)
        entry_tenant_age.insert(0, age)

def add_tenant():
    # Retrieve input values
    tenant_name = entry_tenant_name.get()
    occupation = entry_tenant_occupation.get()
    birthday = entry_tenant_birthday.get()
    gender = combo_tenant_gender.get()
    email = entry_tenant_email.get()
    phone_number = entry_tenant_phone.get()

    # Validate input fields
    if not tenant_name or not occupation or not birthday or not gender or not email or not phone_number:
        messagebox.showerror("Error", "Please fill in all fields")
        return
    # Validate tenant name, occupation, and email using the validation function
    if not validate_alphanumeric_with_letter(tenant_name):
        messagebox.showerror("Error", "Tenant name must contain at least one letter and only alphanumeric characters")
        return
    if not validate_alphanumeric_with_letter(occupation):
        messagebox.showerror("Error", "Occupation must contain at least one letter and only alphanumeric characters")
        return
    if not is_valid_date(birthday):
        messagebox.showerror("Error", "Invalid birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return
    if not has_letter(email):
        messagebox.showerror("Error", "Email must contain at least one letter and only alphanumeric characters")
        return
    # Validate phone number using the validation function
    if not has_number(phone_number):
        messagebox.showerror("Error", "Phone number must contain only numeric characters")
        return

    # Calculate the tenant's age
    tenant_age = calculate_age(birthday)

    if tenant_age is None:
        messagebox.showerror("Error", "Invalid Birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve the current maximum tenant_id from the database
    cursor.execute("SELECT MAX(tenantID) FROM tenant")
    max_tenant_id = cursor.fetchone()[0]

    # If max_house_id is None (no records in the table), set it to 0
    if max_tenant_id is None:
        max_tenant_id = 0

    # Calculate the next tenant_id
    next_tenant_id = max_tenant_id + 1

    # Insert new tenant into the database
    cursor.execute("INSERT INTO tenant (tenantID, tenantName, occupation, birthday, age, gender, email, phoneNumber) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (next_tenant_id, tenant_name, occupation, birthday, tenant_age, gender, email, phone_number))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "Tenant added successfully!")

    # Update combo boxes with new data
    update_tenant_combo_box()
    update_tenant_payment_combo_box()

    tenant_clear_entries()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_tenant.delete(*tree_tenant.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for tenant in tenants:
        tenant_with_zeros = ("{:04d}".format(tenant[0]),) + tenant[1:]
        tree_tenant.insert("", tk.END, values=tenant_with_zeros)

    # Close the database connection
    conn.close()

def populate_entry_tenant_fields(event):
    # Get the selected item from the Treeview
    tenant_selected_item = tree_tenant.selection()
    if tenant_selected_item:
        # Extract data from the selected item
        _, tenant_name, occupation, birthday, tenant_age, gender, email, phone_number = tree_tenant.item(tenant_selected_item, "values")

        # Populate the entry fields with the selected record's data
        entry_tenant_name.delete(0, tk.END)
        entry_tenant_name.insert(0, tenant_name)
        entry_tenant_occupation.delete(0, tk.END)
        entry_tenant_occupation.insert(0, occupation)
        entry_tenant_birthday.delete(0, tk.END)
        entry_tenant_birthday.insert(0, birthday)
        entry_tenant_age.delete(0, tk.END)
        entry_tenant_age.insert(0, tenant_age)
        combo_tenant_gender.set(gender)
        entry_tenant_email.delete(0, tk.END)
        entry_tenant_email.insert(0, email)
        entry_tenant_phone.delete(0, tk.END)
        entry_tenant_phone.insert(0, phone_number)

def update_tenant():
    # Retrieve input values
    tenant_name = entry_tenant_name.get()
    occupation = entry_tenant_occupation.get()
    birthday = entry_tenant_birthday.get()
    tenant_age = entry_tenant_age.get()
    email = entry_tenant_email.get()
    phone_number = entry_tenant_phone.get()

    # Get the selected item from the Treeview
    tenant_selected_item = tree_tenant.selection()

    if not tenant_selected_item:
        messagebox.showerror("Error", "Please select a tenant to update")
        return

    # Validate tenant name, occupation, and email using the validation function
    if not validate_alphanumeric_with_letter(tenant_name):
        messagebox.showerror("Error", "Tenant name must contain at least one letter and only alphanumeric characters")
        return

    if not has_letter(occupation):
        messagebox.showerror("Error", "Occupation must contain only alphanumeric characters")
        return

    if not has_letter(email):
        messagebox.showerror("Error", "Email must contain only alphanumeric characters")
        return

    if not is_valid_date(birthday):
        messagebox.showerror("Error", "Invalid birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return
    if tenant_age is None:
        messagebox.showerror("Error", "Invalid Birthday. Please enter a date in the format 'YYYY-MM-DD'.")
        return
    # Validate phone number using the validation function
    if not has_number(phone_number):
        messagebox.showerror("Error", "Phone number must contain only numeric characters")
        return

    # Retrieve the new values from the entry fields
    tenant_name = entry_tenant_name.get()
    occupation = entry_tenant_occupation.get()
    birthday = entry_tenant_birthday.get()
    tenant_age = entry_tenant_age.get()
    gender = combo_tenant_gender.get()
    email = entry_tenant_email.get()
    phone_number = entry_tenant_phone.get()

    # Validate input fields
    if not tenant_name or not occupation or not birthday or not tenant_age or not gender or not email or not phone_number:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    tenant_id = tree_tenant.item(tenant_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Update the tenant information in the database
    cursor.execute("UPDATE tenant SET tenantName=?, occupation=?, birthday=?, age=?, gender=?, email=?, phoneNumber=? WHERE tenantID=?",
                   (tenant_name, occupation, birthday, tenant_age, gender, email, phone_number, tenant_id))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "Tenant updated successfully!")

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_tenant.delete(*tree_tenant.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for tenant in tenants:
        tenant_with_zeros = ("{:04d}".format(tenant[0]),) + tenant[1:]
        tree_tenant.insert("", tk.END, values=tenant_with_zeros)

    # Close the database connection
    conn.close()

    tenant_clear_entries()

def delete_tenant():
    # Get the selected item from the Treeview
    tenant_selected_item = tree_tenant.selection()
    if not tenant_selected_item:
        messagebox.showerror("Error", "Please select a tenant to delete")
        return

    # Confirm with the user before deleting
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected tenant?")
    if not confirmation:
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    tenant_id = tree_tenant.item(tenant_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Delete the tenant from the database
    cursor.execute("DELETE FROM tenant WHERE tenantID=?", (tenant_id,))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "Tenant deleted successfully!")

    # Update combo boxes with new data
    update_tenant_combo_box()
    update_tenant_payment_combo_box()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_tenant.delete(*tree_tenant.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for tenant in tenants:
        tenant_with_zeros = ("{:04d}".format(tenant[0]),) + tenant[1:]
        tree_tenant.insert("", tk.END, values=tenant_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    tenant_clear_entries()

def search_tenant():
    # Get the search entry value
    search_value = entry_search.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve tenants from the database based on the search_value
    cursor.execute("SELECT * FROM tenant WHERE tenantName LIKE ? OR occupation LIKE ? OR birthday=? OR age=? OR gender =? OR email=? OR phoneNumber=? OR tenantID=?",
                   ('%' + search_value + '%', '%' + search_value + '%', search_value, search_value, search_value, search_value, search_value, search_value))

    search_result = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_tenant.delete(*tree_tenant.get_children())

    # Populate the Treeview with the search result data, adding leading zeros to tenant_id
    for tenant in search_result:
        tenant_with_zeros = ("{:04d}".format(tenant[0]),) + tenant[1:]
        tree_tenant.insert("", tk.END, values=tenant_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    tenant_clear_entries()

def add_house():
    # Retrieve input values
    house_name = entry_house_name.get()
    location = entry_house_location.get()
    rent_amount = entry_house_rent.get()
    availability = combo_house_availability.get()
    occupant = combo_house_occupants.get()
    description = text_house_description.get("1.0", tk.END)

    # Validate input fields
    if not house_name or not location or not rent_amount or not availability or not occupant or not description:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    if not validate_alphanumeric_with_letter(house_name):
        messagebox.showerror("Error", "House Name must contain at least one letter and only alphanumeric characters")
        return

    if not has_letter(location):
        messagebox.showerror("Error", "Location must contain at least one letter and only alphanumeric characters")
        return

    if not has_number(rent_amount):
        messagebox.showerror("Error", "Rent Amount must contain only numeric characters")
        return

    if not has_letter(description):
        messagebox.showerror("Error", "Description must contain at least one letter and only alphanumeric characters")
        return

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve the current maximum houses_id from the database
    cursor.execute("SELECT MAX(houseID) FROM house")
    max_house_id = cursor.fetchone()[0]

    # If max_house_id is None (no records in the table), set it to 0
    if max_house_id is None:
        max_house_id = 0

    # Calculate the next houses_id
    next_house_id = max_house_id + 1

    # Insert new tenant into the database
    cursor.execute("INSERT INTO house (houseID, houseName, availability, rentAmount, occupant, location, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (next_house_id, house_name, availability, rent_amount, occupant, location, description))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "House added successfully!")

    # Update combo boxes with new data
    update_house_combo_box()
    update_tenant_combo_box()
    update_house_payment_combo_box()
    update_tenant_payment_combo_box()

    house_clear_entries()

    # Retrieve all houses from the database
    cursor.execute("SELECT * FROM house")
    houses = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_house.delete(*tree_house.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to house_id
    for house in houses:
        house_with_zeros = ("{:04d}".format(house[0]),) + house[1:]
        tree_house.insert("", tk.END, values=house_with_zeros)

    # Close the database connection
    conn.close()

def populate_entry_house_fields(event):
    # Get the selected item from the Treeview
    house_selected_item = tree_house.selection()
    if house_selected_item:
        # Extract data from the selected item
        _, house_name, availability, rent_amount, occupant, location, description = tree_house.item(house_selected_item, "values")

        # Populate the entry fields with the selected record's data
        entry_house_name.delete(0, tk.END)
        entry_house_name.insert(0, house_name)
        combo_house_availability.set(availability)
        entry_house_rent.delete(0, tk.END)
        entry_house_rent.insert(0, rent_amount)
        combo_house_occupants.set(occupant)
        entry_house_location.delete(0, tk.END)
        entry_house_location.insert(0, location)
        text_house_description.delete("1.0", tk.END)
        text_house_description.insert("1.0", description)

def update_house():
    # Retrieve input values
    house_name = entry_house_name.get()
    location = entry_house_location.get()
    rent_amount = entry_house_rent.get()
    description = text_house_description.get("1.0", tk.END)

    # Get the selected item from the Treeview
    house_selected_item = tree_house.selection()

    if not house_selected_item:
        messagebox.showerror("Error", "Please select a house to update")
        return

    if not validate_alphanumeric_with_letter(house_name):
        messagebox.showerror("Error", "House Name must contain at least one letter and only alphanumeric characters")
        return
    if not has_letter(location):
        messagebox.showerror("Error", "Location must contain at least one letter and only alphanumeric characters")
        return

    if not has_number(rent_amount):
        messagebox.showerror("Error", "Rent Amount must contain only numeric characters")
        return

    if not has_letter(description):
        messagebox.showerror("Error", "Description must contain at least one letter and only alphanumeric characters")
        return

    # Retrieve the new values from the entry fields
    house_name = entry_house_name.get()
    location = entry_house_location.get()
    rent_amount = entry_house_rent.get()
    availability = combo_house_availability.get()
    occupant = combo_house_occupants.get()
    description = text_house_description.get("1.0", tk.END)

    # Validate input fields
    if not house_name or not availability or not rent_amount or not occupant or not location or not description:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    house_id = tree_house.item(house_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Update the tenant information in the database
    cursor.execute("UPDATE house SET houseName=?, availability=?, rentAmount=?, occupant=?, location=?, description=? WHERE houseID=?",
                   (house_name, availability, rent_amount, occupant, location, description, house_id))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "House updated successfully!")

    update_house_combo_box()
    update_tenant_combo_box()
    update_house_payment_combo_box()
    update_tenant_payment_combo_box()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM house")
    houses = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_house.delete(*tree_house.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for house in houses:
        house_with_zeros = ("{:04d}".format(house[0]),) + house[1:]
        tree_house.insert("", tk.END, values=house_with_zeros)

    # Close the database connection
    conn.close()

    house_clear_entries()

def delete_house():
    # Get the selected item from the Treeview
    house_selected_item = tree_house.selection()
    if not house_selected_item:
        messagebox.showerror("Error", "Please select a house to delete")
        return

    # Confirm with the user before deleting
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected house?")
    if not confirmation:
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    house_id = tree_house.item(house_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Delete the tenant from the database
    cursor.execute("DELETE FROM house WHERE houseID=?", (house_id,))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "House deleted successfully!")

    # Update combo boxes with new data
    update_house_combo_box()
    update_tenant_combo_box()
    update_house_payment_combo_box()
    update_tenant_payment_combo_box()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM house")
    houses = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_house.delete(*tree_house.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for house in houses:
        house_with_zeros = ("{:04d}".format(house[0]),) + house[1:]
        tree_house.insert("", tk.END, values=house_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    house_clear_entries()

def search_house():
    # Get the search entry value
    search_value = entry_search_house.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Search for the occupant, houseName, availability, and rentAmount fields using partial match (LIKE)
    cursor.execute("SELECT * FROM house WHERE houseName LIKE ? OR availability LIKE ? OR occupant LIKE ? OR rentAmount LIKE ? OR houseID=?",
        ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', search_value))

    search_result = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_house.delete(*tree_house.get_children())

    # Populate the Treeview with the search result data, adding leading zeros to tenant_id
    for house in search_result:
        house_with_zeros = ("{:04d}".format(house[0]),) + house[1:]
        tree_house.insert("", tk.END, values=house_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    house_clear_entries()

def get_house_ids():
    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Fetch the house names from the database where availability is 'Available'
    cursor.execute("SELECT houseID FROM house WHERE availability = 'Available'")
    available_houses = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()

    # Format the tenant IDs as four-digit numbers with leading zeros
    formatted_house_ids = ["{:04d}".format(tid) for tid in available_houses]

    return formatted_house_ids

def update_house_combo_box():
    # Get the house IDs from the database
    house_ids = get_house_ids()

    # Clear the current values in the ComboBox
    combo_house_id['values'] = ()

    # Set the values of the ComboBox to the fetched house IDs
    combo_house_id['values'] = house_ids

def get_house_occupied_ids():
    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Fetch the house names from the database where availability is 'Occupied'
    cursor.execute("SELECT houseID FROM house WHERE availability = 'Occupied'")
    occupied_houses = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()

    # Format the tenant IDs as four-digit numbers with leading zeros
    formatted_house_ids = ["{:04d}".format(tid) for tid in occupied_houses]

    return formatted_house_ids

def update_house_payment_combo_box():
    # Get the house IDs from the database
    house_ids = get_house_occupied_ids()

    # Clear the current values in the ComboBox
    combo_house_payment_id['values'] = ()

    # Set the values of the ComboBox to the fetched house IDs
    combo_house_payment_id['values'] = house_ids

def get_tenant_ids():
    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Fetch the tenant IDs from the database
    cursor.execute("SELECT tenantID FROM tenant")
    tenant_ids = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()

    # Format the tenant IDs as four-digit numbers with leading zeros
    formatted_tenant_ids = ["{:04d}".format(tid) for tid in tenant_ids]

    return formatted_tenant_ids

def update_tenant_combo_box():
    # Get the tenant IDs from the database
    tenant_ids = get_tenant_ids()

    # Clear the current values in the ComboBox
    combo_tenant_id['values'] = ()

    # Set the values of the ComboBox to the fetched tenant IDs
    combo_tenant_id['values'] = tenant_ids

def get_tenants_for_payment(house_id):
    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Fetch the tenant IDs associated with the given house ID from the database
    cursor.execute("SELECT DISTINCT tenantID FROM lease WHERE houseID=?", (house_id,))
    tenant_ids = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()

    # Format the tenant IDs as four-digit numbers with leading zeros
    formatted_tenant_ids = ["{:04d}".format(tid) for tid in tenant_ids]

    return formatted_tenant_ids

def update_tenant_payment_combo_box(*args):
    # Get the selected house ID from the combo box
    house_id = combo_house_payment_id.get()

    # Fetch the tenant IDs associated with the selected house ID
    tenant_ids = get_tenants_for_payment(house_id)

    # Clear the current values in the ComboBox
    combo_tenant_payment_id['values'] = ()

    # Set the values of the ComboBox to the fetched tenant IDs
    combo_tenant_payment_id['values'] = tenant_ids

def update_lease_amount(event):
    # Get the selected houseID from the combo box
    house_id = combo_house_id.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve the rent amount based on the selected houseID from the database
    cursor.execute("SELECT rentAmount FROM house WHERE houseID = ?", (house_id,))
    rent_amount = cursor.fetchone()[0]

    # Update the lease_amount entry with the rent amount
    entry_lease_amount.delete(0, tk.END)
    entry_lease_amount.insert(0, rent_amount)

    # Close the database connection
    conn.close()

def calculate_end_date(start_date, lease_duration):
    try:
        # Convert the start_date string to a datetime object
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")

        # Split the lease_duration string into its numeric value and unit (e.g., "1 year" => ["1", "year"])
        duration_parts = lease_duration.strip().split()

        # Get the numeric value and unit from the duration_parts
        duration_value = int(duration_parts[0])
        duration_unit = duration_parts[1].lower()

        # Calculate the end date based on the lease duration
        if duration_unit == "year" or duration_unit == "years":
            end_date = start_date_obj + timedelta(days=duration_value * 365)
        elif duration_unit == "month" or duration_unit == "months":
            end_date = start_date_obj + timedelta(days=duration_value * 30)  # Approximation: 30 days per month
        else:
            raise ValueError("Invalid lease duration unit")

        # Format the end date as a string in the format 'YYYY-MM-DD'
        end_date_str = end_date.strftime("%Y-%m-%d")

        return end_date_str

    except (ValueError, IndexError):
        return None

def update_end_date(event):
    start_date = entry_lease_start_date.get()
    lease_duration = entry_lease_duration.get()

    # Calculate the end date based on the lease duration and start date
    end_date = calculate_end_date(start_date, lease_duration)

    # If the end_date is not valid, show an error message and return
    if end_date is not None:
        # Set the end date in the entry widget
        entry_lease_end_date.delete(0, tk.END)
        entry_lease_end_date.insert(0, end_date)

def add_lease():
    # Retrieve input values
    house_id = combo_house_id.get()
    tenant_id = combo_tenant_id.get()
    lease_duration = entry_lease_duration.get()
    start_date = entry_lease_start_date.get()
    lease_period = combo_lease_period.get()
    lease_amount = entry_lease_amount.get()
    lease_deposit = entry_lease_deposit.get()


    # Validate input fields
    if not house_id or not tenant_id or not lease_duration or not start_date or not lease_amount or not lease_deposit:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    if not validate_alphanumeric_with_letter(lease_duration):
        messagebox.showerror("Error", "lease Duration Name must contain at least one letter and only alphanumeric characters Ex: 1 year, 6 Months")
        return

    if not is_valid_date(start_date):
        messagebox.showerror("Error", "Invalid Start Date. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    # Calculate the end date based on the lease duration and start date
    end_date = calculate_end_date(start_date, lease_duration)
    # If the end_date is not valid, show an error message and return
    if end_date is None:
        messagebox.showerror("Error", "Invalid lease duration or start date.")
        return

    if not has_number(lease_amount):
        messagebox.showerror("Error", "Lease Amount must contain only numeric characters")
        return

    if not has_number(lease_deposit):
        messagebox.showerror("Error", "Lease Deposit must contain only numeric characters")
        return

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Check if the selected house is already marked as "Occupied"
    cursor.execute("SELECT availability FROM house WHERE houseID=?", (house_id,))
    house_availability = cursor.fetchone()

    if house_availability and house_availability[0] == "Occupied":
        # Close the database connection
        conn.close()

        # Show error message
        messagebox.showerror("Error", "Selected house is already occupied. Please choose an available house.")
        return

    # Retrieve the current maximum lease_id from the database
    cursor.execute("SELECT MAX(leaseID) FROM lease")
    max_lease_id = cursor.fetchone()[0]

    # If max_lease_id is None (no records in the table), set it to 0
    if max_lease_id is None:
        max_lease_id = 0

    # Calculate the next lease_id, house_id, and tenant_id with leading zeros
    next_lease_id = max_lease_id + 1

    # Insert new lease into the database
    cursor.execute("INSERT INTO lease (leaseID, houseID, tenantID, leaseDuration, startDate, endDate, leasePeriod, leaseAmount, leaseDeposit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (next_lease_id, house_id, tenant_id, lease_duration, start_date, end_date, lease_period, lease_amount, lease_deposit))
    conn.commit()

    # Update the availability of the selected house to "Occupied"
    cursor.execute("UPDATE house SET availability = 'Occupied' WHERE houseID = ?", (house_id,))
    conn.commit()

    update_house_combo_box()
    update_tenant_combo_box()
    update_house_payment_combo_box()
    update_tenant_payment_combo_box()

    # Show success message
    messagebox.showinfo("Success", "Lease added successfully!")

    lease_clear_entries()

    # Retrieve all leases from the database
    cursor.execute("SELECT * FROM lease")
    leases = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_lease.delete(*tree_lease.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to lease_id
    for lease in leases:
        lease_with_zeros = ("{:04d}".format(lease[0]), "{:04d}".format(lease[1]), "{:04d}".format(lease[2])) + lease[3:]
        tree_lease.insert("", tk.END, values=lease_with_zeros)

    # Close the database connection
    conn.close()

def populate_entry_lease_fields(event):
    # Get the selected item from the Treeview
    lease_selected_item = tree_lease.selection()
    if lease_selected_item:
        # Extract data from the selected item
        _, house_id, tenant_id, lease_duration, start_date, end_date, lease_period, lease_amount, lease_deposit = tree_lease.item(lease_selected_item, "values")

        # Populate the entry fields with the selected record's data
        combo_house_id.set(house_id)
        combo_tenant_id.set(tenant_id)
        entry_lease_duration.delete(0, tk.END)
        entry_lease_duration.insert(0, lease_duration)
        entry_lease_start_date.delete(0, tk.END)
        entry_lease_start_date.insert(0, start_date)
        entry_lease_end_date.delete(0, tk.END)
        entry_lease_end_date.insert(0, end_date)
        combo_lease_period.set(lease_period)
        entry_lease_amount.delete(0, tk.END)
        entry_lease_amount.insert(0, lease_amount)
        entry_lease_deposit.delete(0, tk.END)
        entry_lease_deposit.insert(0, lease_deposit)

def update_lease():
    # Retrieve input values
    lease_duration = entry_lease_duration.get()
    start_date = entry_lease_start_date.get()
    end_date = entry_lease_end_date.get()
    lease_amount = entry_lease_amount.get()
    lease_deposit = entry_lease_deposit.get()

    # Get the selected item from the Treeview
    lease_selected_item = tree_lease.selection()

    if not lease_selected_item:
        messagebox.showerror("Error", "Please select a lease to update")
        return

    # Get the previous house ID from the selected item (second element in the tuple)
    previous_house_id = tree_lease.item(lease_selected_item)['values'][1]
    new_house_id = combo_house_id.get()

    if not validate_alphanumeric_with_letter(lease_duration):
        messagebox.showerror("Error", "lease Duration Name must contain at least one letter and only alphanumeric characters")
        return

    if not is_valid_date(start_date):
        messagebox.showerror("Error", "Invalid Start Date. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    if not is_valid_date(end_date):
        messagebox.showerror("Error", "Invalid End Date. Please enter a date in the format 'YYYY-MM-DD'.")
        return

    if not has_number(lease_amount):
        messagebox.showerror("Error", "Lease Amount must contain only numeric characters")
        return

    if not has_number(lease_deposit):
        messagebox.showerror("Error", "Lease Deposit must contain only numeric characters")
        return

    # Retrieve the new values from the entry fields
    house_id = combo_house_id.get()
    tenant_id = combo_tenant_id.get()
    lease_duration = entry_lease_duration.get()
    start_date = entry_lease_start_date.get()
    end_date = entry_lease_end_date.get()
    lease_period = combo_lease_period.get()
    lease_amount = entry_lease_amount.get()
    lease_deposit = entry_lease_deposit.get()

    # Validate input fields
    if not house_id or not tenant_id or not lease_duration or not start_date or not end_date or not lease_period or not lease_amount or not lease_deposit:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    lease_id = tree_lease.item(lease_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Update the tenant information in the database
    cursor.execute("UPDATE lease SET houseID=?, tenantID=?, leaseDuration=?, startDate=?, endDate=?, leasePeriod=?, leaseAmount=?, leaseDeposit=? WHERE leaseID=?",
                   (house_id, tenant_id, lease_duration, start_date, end_date, lease_period, lease_amount, lease_deposit, lease_id))
    conn.commit()

    # Check if the houseID is different from the previous houseID
    if house_id != previous_house_id:
        # Mark the previous house as "Available" in the house table
        cursor.execute("UPDATE house SET availability=? WHERE houseID=?", ("Available", previous_house_id))
        # Mark the new house as "Occupied" in the house table
        cursor.execute("UPDATE house SET availability=? WHERE houseID=?", ("Occupied", new_house_id))

    # Commit the changes to the database
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "Lease updated successfully!")

    update_house_combo_box()
    update_tenant_combo_box()
    update_house_payment_combo_box()
    update_tenant_payment_combo_box()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM lease")
    leases = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_lease.delete(*tree_lease.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for lease in leases:
        lease_with_zeros = ("{:04d}".format(lease[0]), "{:04d}".format(lease[1]), "{:04d}".format(lease[2])) + lease[3:]
        tree_lease.insert("", tk.END, values=lease_with_zeros)

    # Close the database connection
    conn.close()

    lease_clear_entries()

def delete_lease():
    # Get the selected item from the Treeview
    house_id = combo_house_id.get()
    lease_selected_item = tree_lease.selection()
    if not lease_selected_item:
        messagebox.showerror("Error", "Please select a lease to delete")
        return

    # Confirm with the user before deleting
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected lease?")
    if not confirmation:
        return

    # Get the tenant ID from the selected item (first element in the tuple)
    lease_id = tree_lease.item(lease_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Delete the tenant from the database
    cursor.execute("DELETE FROM lease WHERE leaseID=?", (lease_id,))
    conn.commit()

    # Update the availability of the selected house to "Occupied"
    cursor.execute("UPDATE house SET availability = 'Available' WHERE houseID = ?", (house_id,))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "Lease deleted successfully!")

    update_house_combo_box()
    update_tenant_combo_box()
    update_house_payment_combo_box()
    update_tenant_payment_combo_box()

    # Retrieve all tenants from the database
    cursor.execute("SELECT * FROM lease")
    leases = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_lease.delete(*tree_lease.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to tenant_id
    for lease in leases:
        lease_with_zeros = ("{:04d}".format(lease[0]), "{:04d}".format(lease[1]), "{:04d}".format(lease[2])) + lease[3:]
        tree_lease.insert("", tk.END, values=lease_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    lease_clear_entries()

def search_lease():
    # Get the search entry value
    search_value = entry_search_lease.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve tenants from the database based on the search_value
    cursor.execute("SELECT * FROM lease WHERE leaseDuration LIKE ? OR startDate LIKE ? OR endDate LIKE ? OR leasePeriod LIKE ? OR leaseAmount=? OR leaseID=?",
                   ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', search_value, search_value))

    search_result = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_lease.delete(*tree_lease.get_children())

    # Populate the Treeview with the search result data, adding leading zeros to tenant_id
    for lease in search_result:
        lease_with_zeros = ("{:04d}".format(lease[0]), "{:04d}".format(lease[1]), "{:04d}".format(lease[2])) + lease[3:]
        tree_lease.insert("", tk.END, values=lease_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    lease_clear_entries()

def generate_receipt_number(house_id, tenant_id):
    # Get the current date and time
    current_datetime = datetime.now()

    # Format the receipt number as TENANTID_YYYYMMDDHHMMSS
    receipt_number = f"{house_id}_{tenant_id}_{current_datetime.strftime('%Y%m%d')}"

    return receipt_number

def update_payment_amount(event):
    # Get the selected houseID from the combo box
    payment_amount = combo_house_payment_id.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    cursor.execute("SELECT rentAmount FROM house WHERE houseID = ?", (payment_amount,))
    payment_amount = cursor.fetchone()[0]

    entry_payment_amount.delete(0, tk.END)
    entry_payment_amount.insert(0, payment_amount)

    # Close the database connection
    conn.close()

def convert_to_months(lease_duration):
    try:
        duration = lease_duration.lower().strip()
        if "year" in duration:
            years = int(duration.split()[0])
            return years * 12
        elif "month" in duration:
            months = int(duration.split()[0])
            return months
        else:
            raise ValueError("Invalid lease duration format")
    except (ValueError, TypeError):
        return None

def calculate_payments(lease_duration, payment_period):
    # Assume you have a function that converts lease duration into months
    lease_duration_in_months = convert_to_months(lease_duration)

    # Define a dictionary to map payment periods to months in a year
    months_in_year = {
        "Monthly": 1,
        "Yearly": 12,
        "Weekly": 52,  # Approximation: 52 weeks in a year
    }

    try:
        lease_duration_in_months = int(lease_duration_in_months)

        # Get the corresponding number of months in a year based on the payment_period
        months_in_period = months_in_year.get(payment_period.lower(), 1)

        # Calculate the total number of payments based on the lease duration and payment period
        if payment_period.lower() == "yearly":
            total_payments = lease_duration_in_months // 12
        elif payment_period.lower() == "weekly":
            total_payments = (lease_duration_in_months * 52) // 12
        else:
            total_payments = (lease_duration_in_months + months_in_period - 1) // months_in_period

        return total_payments
    except (ValueError, TypeError):
        return None

def calculate_payment_due(start_date, payment_period, num_payments):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if payment_period == "Monthly":
            # Calculate the next payment due date by adding the number of months specified in payment_due
            next_payment_due_date = start_date + relativedelta(months=num_payments)
        elif payment_period == "Weekly":
            # Calculate the next payment due date by adding the number of weeks specified in payment_due
            next_payment_due_date = start_date + timedelta(weeks=num_payments)
        else:
            raise ValueError("Invalid payment period")

        # Format the next payment due date as a string in the format 'YYYY-MM-DD'
        next_payment_due_str = next_payment_due_date.strftime("%Y-%m-%d")
        return next_payment_due_str

    except (ValueError, TypeError):
        return None

def add_payment():
    # Retrieve input values
    payment_house_id = combo_house_payment_id.get()
    payment_tenant_id = combo_tenant_payment_id.get()
    payment_amount = entry_payment_amount.get()
    payment_method = combo_payment_method.get()

    # Validate input fields
    if not payment_house_id or not payment_tenant_id or not payment_amount or not payment_method:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    if not has_number(payment_amount):
        messagebox.showerror("Error", "Payment Amount must contain only numeric characters")
        return

    # Generate the receipt number
    receipt_number = generate_receipt_number(payment_house_id, payment_tenant_id)

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Get the lease duration and payment period for the selected house
    cursor.execute("SELECT leaseDuration, leasePeriod, startDate FROM lease WHERE houseID=?", (payment_house_id,))
    house_data = cursor.fetchone()
    if not house_data:
        messagebox.showerror("Error", "House not found")
        conn.close()
        return

    lease_duration, payment_period, start_date = house_data

    # Get the number of payments made by the tenant for the current house
    cursor.execute("SELECT COUNT(*) FROM payment WHERE tenantID=? AND houseID=?", (payment_tenant_id, payment_house_id))
    num_payments = cursor.fetchone()[0]

    # Calculate the total number of payments based on the lease duration and payment period
    total_payments = calculate_payments(lease_duration, payment_period)

    # Calculate the starting payment number
    start_payment_number = num_payments + 1

    # Calculate the ending payment number
    end_payment_number = min(start_payment_number + total_payments - 1, total_payments)

    # Format the payment total
    payment_total = f"{start_payment_number} - {end_payment_number}"

    # Check if it's the last payment
    if start_payment_number > end_payment_number:
        messagebox.showerror("Error", "All payments have already been made. No more payments can be added.")
        return

    # Calculate the payment_due based on the lease start date and payment period
    payment_due = calculate_payment_due(start_date, payment_period, num_payments)

    if payment_due is None:
        # If payment_due is None, show an error message and prevent inserting the payment record
        messagebox.showerror("Error", "Failed to calculate the next payment due date.")
        return

    # Check if it's the last payment
    if start_payment_number == end_payment_number:
        # Format the last payment as "X payments in total - completed"
        next_due_payment_date = f"{total_payments} payments in total - completed"
    else:
        # Calculate the next due payment date (e.g., "2023-07-31 - 2023-08-31")
        next_due_payment_date = f"{payment_due} - {calculate_payment_due(start_date, payment_period, num_payments+1)}"

    # Insert new payment into the database
    cursor.execute("INSERT INTO payment (houseID, tenantID, receiptNumber, paymentAmount, paymentTotal, paymentDue, paymentMethod) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (payment_house_id, payment_tenant_id, receipt_number, payment_amount, payment_total,next_due_payment_date , payment_method))
    conn.commit()

    # Get the payment_id of the last inserted row
    payment_id = cursor.lastrowid

    # Check if it's the last payment
    if start_payment_number == end_payment_number:
        messagebox.showinfo("All Payments Done", "Congratulations! You have made all the payments for this lease.")

    # Show success message with the payment number
    else:
        messagebox.showinfo("Success", f"Payment added successfully!\nPayment Number: {payment_total}")

    # Show a message box to ask the tenant if they want to print the receipt
    print_receipt_option = messagebox.askyesno("Print Receipt", "Do you want to print the receipt?")

    # Call the print_receipt function to generate and save the receipt if the tenant chooses to print
    if print_receipt_option:
        print_receipt(payment_id, payment_due, payment_amount, payment_total)

    payment_clear_entries()

    # Retrieve all leases from the database
    cursor.execute("SELECT * FROM payment")
    payments = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_payment.delete(*tree_payment.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to lease_id
    for payment in payments:
        payment_with_zeros = ("{:04d}".format(payment[0]), "{:04d}".format(payment[1]), "{:04d}".format(payment[2])) + payment[3:]
        tree_payment.insert("", tk.END, values=payment_with_zeros)

    # Close the database connection
    conn.close()

def generate_receipt(payment_id, payment_date, payment_amount, payment_total):
    # Create a virtual file in memory
    buffer = io.BytesIO()

    # Create a new PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the content for the receipt
    receipt_content = []

    # Add the receipt header
    styles = getSampleStyleSheet()
    receipt_content.append(Paragraph(f"<b>Receipt for Payment ID: {payment_id}</b>", styles['Heading1']))
    receipt_content.append(Spacer(1, 12))

    # Add the payment details
    receipt_content.append(Paragraph(f"<b>Payment Date:</b> {payment_date}", styles['Normal']))
    receipt_content.append(Paragraph(f"<b>Payment Amount:</b> {payment_amount}", styles['Normal']))
    receipt_content.append(Paragraph(f"<b>Payment Total:</b> {payment_total}", styles['Normal']))

    # Build the PDF document with the receipt content
    doc.build(receipt_content)

    # Move the buffer pointer to the beginning
    buffer.seek(0)

    # Return the PDF content as bytes
    return buffer.getvalue()

def print_receipt(payment_id, payment_date, payment_amount, payment_total):
    # Generate the receipt content
    receipt_content = generate_receipt(payment_id, payment_date, payment_amount, payment_total)

    # Show the file dialog to select the location to save the receipt
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

    # Check if the user canceled the file dialog
    if not file_path:
        return

    # Save the receipt as a PDF file
    with open(file_path, "wb") as file:
        file.write(receipt_content)

    # Open the saved receipt file using the default PDF reader
    subprocess.Popen([file_path], shell=True)

def populate_entry_payment_fields(event):
    # Get the selected item from the Treeview
    payment_selected_item = tree_payment.selection()
    if payment_selected_item:
        # Extract data from the selected item
        _, payment_house_id, payment_tenant_id, _, payment_amount, _, _, payment_method = tree_payment.item(payment_selected_item, "values")

        # Populate the entry fields with the selected record's data
        combo_house_payment_id.set(payment_house_id)
        combo_tenant_payment_id.set(payment_tenant_id)
        entry_payment_amount.delete(0, tk.END)
        entry_payment_amount.insert(0, payment_amount)
        combo_payment_method.set(payment_method)

def update_payment():
    # Get the selected item from the Treeview
    payment_selected_item = tree_payment.selection()

    if not payment_selected_item:
        messagebox.showerror("Error", "Please select a lease to update")
        return

    # Retrieve the new values from the entry fields

    payment_method = combo_payment_method.get()

    # Validate input fields
    if not payment_method:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    # Get the payment ID from the selected item (first element in the tuple)
    payment_id = tree_payment.item(payment_selected_item)['values'][0]

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Update the tenant information in the database
    cursor.execute("UPDATE payment SET paymentMethod=? WHERE paymentID=?",
                   (payment_method, payment_id))
    conn.commit()

    # Show success message
    messagebox.showinfo("Success", "Payment updated successfully!")

    # Retrieve all payments from the database
    cursor.execute("SELECT * FROM payment")
    payments = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_payment.delete(*tree_payment.get_children())

    # Populate the Treeview with the updated data, adding leading zeros to payment_id
    for payment in payments:
        payment_with_zeros = ("{:04d}".format(payment[0]), "{:04d}".format(payment[1]), "{:04d}".format(payment[2])) + payment[3:]
        tree_payment.insert("", tk.END, values=payment_with_zeros)

    # Close the database connection
    conn.close()

    payment_clear_entries()

def delete_payment():
    # Get the selected item from the Treeview
    payment_selected_item = tree_payment.selection()

    # Check if any payment is selected
    if payment_selected_item:
        # If a specific payment item is selected, proceed with the deletion
        # Confirm with the user before deleting
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected payment?")
        if not confirmation:
            return

        # Get the payment ID from the selected item (first element in the tuple)
        payment_id = tree_payment.item(payment_selected_item)['values'][0]

        # Connect to the database
        conn = sqlite3.connect("Rental.db")
        cursor = conn.cursor()

        # Delete the payment from the database
        cursor.execute("DELETE FROM payment WHERE paymentID=?", (payment_id,))
        conn.commit()

        # Show success message
        messagebox.showinfo("Success", "Payment deleted successfully!")

        # Retrieve all payments from the database
        cursor.execute("SELECT * FROM payment")
        payments = cursor.fetchall()

        # Clear existing data in the Treeview
        tree_payment.delete(*tree_payment.get_children())

        # Populate the Treeview with the updated data, adding leading zeros to tenant_id
        for payment in payments:
            payment_with_zeros = ("{:04d}".format(payment[0]), "{:04d}".format(payment[1]), "{:04d}".format(payment[2])) + payment[3:]
            tree_payment.insert("", tk.END, values=payment_with_zeros)

        # Close the database connection
        conn.close()

        # Clear the entry fields
        payment_clear_entries()
    else:
        # If no payment is selected, ask for a double confirmation to delete all payments
        second_confirmation = messagebox.askyesno("Double Confirmation", "WARNING: This action will delete all payments. Are you sure you want to proceed?")
        if not second_confirmation:
            return

        confirmation = messagebox.askyesno("Triple Confirmation", "Are you absolutely sure you want to delete all payments?")
        if not confirmation:
            return

        # Connect to the database
        conn = sqlite3.connect("Rental.db")
        cursor = conn.cursor()

        # Delete all payments from the database
        cursor.execute("DELETE FROM payment")
        conn.commit()

        # Show success message
        messagebox.showinfo("Success", "All payments deleted successfully!")

        # Clear existing data in the Treeview
        tree_payment.delete(*tree_payment.get_children())

        # Close the database connection
        conn.close()

        # Clear the entry fields
        payment_clear_entries()

def search_payment():
    # Get the search entry value
    search_value = entry_search_payment.get()

    # Connect to the database
    conn = sqlite3.connect("Rental.db")
    cursor = conn.cursor()

    # Retrieve tenants from the database based on the search_value
    cursor.execute("SELECT * FROM payment WHERE receiptNumber LIKE ?  OR paymentAmount LIKE ? OR paymentMethod LIKE ? OR paymentID=? OR houseID=? OR tenantID=?",
                   ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', search_value, search_value, search_value))

    search_result = cursor.fetchall()

    # Clear existing data in the Treeview
    tree_payment.delete(*tree_payment.get_children())

    # Populate the Treeview with the search result data, adding leading zeros to tenant_id
    for payment in search_result:
        payment_with_zeros = ("{:04d}".format(payment[0]), "{:04d}".format(payment[1]), "{:04d}".format(payment[2])) + payment[3:]
        tree_payment.insert("", tk.END, values=payment_with_zeros)

    # Close the database connection
    conn.close()

    # Clear the entry fields
    payment_clear_entries()

def show_login_form():
    response = messagebox.askyesno("Confirmation", "Are you sure you want to LOGOUT?")
    if response:
        login_register_clear_entries()
        registration_frame.pack_forget()
        userpassframe.pack()
        main_frame.pack_forget()
        adminConfirmation.pack_forget()

def hide_login_form():
    login_register_clear_entries()
    userpassframe.pack_forget()
    main_frame.pack(fill=tk.BOTH, expand=True)  # Show the main_frame
    adminConfirmation.pack_forget()

def show_admin_confirmation():
    adminConfirmation.pack()

def show_registration_form():
    registration_frame.pack()
    userpassframe.pack_forget()
    adminConfirmation.pack_forget()
    main_frame.pack_forget()  # Hide the main_frame

    # Call the function to populate the Treeview with existing data
    populate_treeview()

def show_tenant_frame():
    main_frame.pack_forget()
    tenant_frame.pack()

    # Call the function to populate the Treeview with existing data
    populate_treeview()

def show_house_frame():
    main_frame.pack_forget()
    house_frame.pack()

    # Call the function to populate the Treeview with existing data
    populate_treeview()

def show_lease_frame():
    main_frame.pack_forget()
    lease_frame.pack()

    # Call the function to populate the Treeview with existing data
    populate_treeview()

def show_payment_frame():
    main_frame.pack_forget()
    payment_frame.pack()

    # Call the function to populate the Treeview with existing data
    populate_treeview()

def show_report_frame():
    main_frame.pack_forget()
    report_main_frame.pack()

def show_main_frame():
    main_frame.pack(fill=tk.BOTH, expand=True)
    hide_entity_frame()

def go_back():
    hide_entity_frame()
    show_main_frame()

    # Clear the entry fields
    tenant_clear_entries()
    house_clear_entries()
    lease_clear_entries()
    payment_clear_entries()

def hide_entity_frame():
    tenant_frame.pack_forget()
    house_frame.pack_forget()
    lease_frame.pack_forget()
    payment_frame.pack_forget()
    report_main_frame.pack_forget()

# Function to get data from the tenant table
def get_tenant_data():
    # Connect to the database (replace 'your_database_file.db' with the actual database file name)
    conn = sqlite3.connect('Rental.db')
    cursor = conn.cursor()

    # Fetch data from the tenant table
    cursor.execute("SELECT * FROM tenant")
    tenant_data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the data as a list of dictionaries
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in tenant_data]

def get_house_data():
    # Connect to the database (replace 'your_database_file.db' with the actual database file name)
    conn = sqlite3.connect('Rental.db')
    cursor = conn.cursor()

    # Fetch data from the tenant table
    cursor.execute("SELECT * FROM house")
    house_data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the data as a list of dictionaries
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in house_data]

def get_lease_data():
    # Connect to the database (replace 'your_database_file.db' with the actual database file name)
    conn = sqlite3.connect('Rental.db')
    cursor = conn.cursor()

    # Fetch data from the tenant table
    cursor.execute("SELECT * FROM lease")
    lease_data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the data as a list of dictionaries
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in lease_data]

def get_payment_data():
    # Connect to the database (replace 'your_database_file.db' with the actual database file name)
    conn = sqlite3.connect('Rental.db')
    cursor = conn.cursor()

    # Fetch data from the tenant table
    cursor.execute("SELECT * FROM payment")
    payment_data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the data as a list of dictionaries
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in payment_data]

# Function to create a PDF report for a given data and table name
def create_pdf_report(data, table_name, file_path):
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
    elements = []

    # Add a title to the report
    styles = getSampleStyleSheet()
    title = Paragraph(f"<b>{table_name} Report</b>", styles['Title'])
    elements.append(title)

    # Table data and table style
    table_data = [list(data[0].keys())] + [[str(value) for value in item.values()] for item in data]
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Create the table and add it to the elements
    table = Table(table_data)
    table.setStyle(table_style)
    elements.append(table)

    # Build the PDF document
    doc.build(elements)

def generate_tenant_report():
    tenant_report_option = messagebox.askyesno("Print Report", "Do you want to print the Tenant Table?")
    if tenant_report_option:
        tenant_data = get_tenant_data()
        # Show the file dialog to select the location to save the report
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

        # Check if the user canceled the file dialog
        if not file_path:
            return
        try:
            create_pdf_report(tenant_data, "Tenant", file_path)
            messagebox.showinfo("Success", f"Tenant report successfully created!\nFile saved at: {file_path}")
            # Open the saved receipt file using the default PDF reader
            subprocess.Popen([file_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the tenant report:\n{str(e)}")

def generate_house_report():
    house_report_option = messagebox.askyesno("Print Report", "Do you want to print the House Table?")
    if house_report_option:
        house_data = get_house_data()  # Assuming you have a function to get data from the house table

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

        if not file_path:
            return
        try:
            create_pdf_report(house_data, "House", file_path)
            messagebox.showinfo("Success", f"House report successfully created!\nFile saved at: {file_path}")
            # Open the saved receipt file using the default PDF reader
            subprocess.Popen([file_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the house report:\n{str(e)}")

def generate_lease_report():
    lease_report_option = messagebox.askyesno("Print Report", "Do you want to print the Lease Table?")
    if lease_report_option:
        lease_data = get_lease_data()  # Assuming you have a function to get data from the lease table
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

        if not file_path:
            return
        try:
            create_pdf_report(lease_data, "Lease", file_path)
            messagebox.showinfo("Success", f"Lease report successfully created!\nFile saved at: {file_path}")
            # Open the saved receipt file using the default PDF reader
            subprocess.Popen([file_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the lease report:\n{str(e)}")

def generate_payment_report():
    lease_report_option = messagebox.askyesno("Print Report", "Do you want to print the Payment Table?")
    if lease_report_option:
        payment_data = get_payment_data()  # Assuming you have a function to get data from the payment table
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

        if not file_path:
            return
        try:
            create_pdf_report(payment_data, "Payment", file_path)
            messagebox.showinfo("Success", f"Payment report successfully created!\nFile saved at: {file_path}")
            # Open the saved receipt file using the default PDF reader
            subprocess.Popen([file_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the payment report:\n{str(e)}")

def display_image():
    # Load the image from a specific directory
    img = tk.PhotoImage(file="E:/Programs/Python/others - kyle/HRSproject/athome.png")

    # Create a Label to display the image
    label_image = tk.Label(main_frame, image=img, bg="#338BA8")
    label_image.image = img  # Save a reference to prevent the image from being garbage collected

    # Place the Label in the desired position
    label_image.grid(row=2, column=2, padx=150, pady=100)

def time():
    string = strftime('%H:%M:%S %p - %b %d, %Y', localtime())
    main_time.config(text=string)
    main_time.after(1000, time)

# Function to change the background color of the buttons on mouse hover
def on_enter(e):
    e.widget['bg'] = '#67B7D1'  # Light blue on hover

def on_leave(e):
    e.widget['bg'] = 'white'  # White on normal state


root = tk.Tk()
root.title("Rental House System")
root.geometry("600x600")
root.state('zoomed')
root.configure(bg="#338BA8")

# Custom font for the heading
custom_font = ("Proforma", 30, "bold")
custom_font3 = ("Broadway", 30, "bold")

title_heading = tk.Label(root, text="RENTAL HOUSE SYSTEM", width=100, height=2,
                          font=custom_font3, bg="#F0F0F0", fg="#333333")
title_heading.pack(side=tk.TOP, pady=30)

userpassframe = tk.Frame(root, bg="#1E5162", pady=35, padx=50)

label_titlelogin = tk.Label(userpassframe, text="LOG IN", font=custom_font3)
label_username = tk.Label(userpassframe, text="Username: ", font=("Helvetica", 12))
label_password = tk.Label(userpassframe, text="Password: ", font=("Helvetica", 12))

validate_input = userpassframe.register(on_validate_input)
entry_username = tk.Entry(userpassframe, validate="key", validatecommand=(validate_input, "%S"))
entry_password = tk.Entry(userpassframe, show="*", validate="key", validatecommand=(validate_input, "%S"))

label_titlelogin.pack(pady=10)
label_username.pack(pady=5)
entry_username.pack()
label_password.pack(pady=8)
entry_password.pack()

button_login = tk.Button(userpassframe, text="LOGIN", command=login, width=10, height=0,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
label_question = tk.Label(userpassframe, text="Create new Account?", font=("Helvetica", 12))
register_button = tk.Button(userpassframe, text="REGISTER", command=show_admin_confirmation, width=10, height=0,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))

button_login.bind("<Return>", lambda event: login())
button_login.pack(pady=10)
label_question.pack(pady=5)
register_button.pack(pady=8)
register_button.bind("<Return>", lambda event: show_admin_confirmation())

userpassframe.pack()

adminConfirmation = tk.Frame(root, bg="#1E5162", padx=50)

label_admin = tk.Label(adminConfirmation, text="   Admin password:    ", font=("Helvetica", 12))
label_admin.pack(pady=5)
validate_input = adminConfirmation.register(on_validate_input)
entry_admin = tk.Entry(adminConfirmation, show="*", validate="key", validatecommand=(validate_input, "%S"))
entry_admin.pack(pady=5)

button_admin = tk.Button(adminConfirmation, text="SUBMIT", command=validate_admin_password, width=10, height=0,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
button_admin.pack(pady=5)
button_admin.bind("<Return>", lambda event: validate_admin_password())

# Binding the mouse hover events to the buttons
button_login.bind("<Enter>", on_enter)
button_login.bind("<Leave>", on_leave)
register_button.bind("<Enter>", on_enter)
register_button.bind("<Leave>", on_leave)
button_admin.bind("<Enter>", on_enter)
button_admin.bind("<Leave>", on_leave)

                            # REGISTRATION FRAME

registration_frame = tk.Frame(root, bg="#ADD8E6")

label_registration_frame = tk.Frame(registration_frame,bg="#338BA8", padx=15, pady=10)
label_registration_frame.grid(row=0, column=4, pady=20)

label_registration = tk.Label(label_registration_frame, text="USER TABLE", font=custom_font3, bg="#F0F0F0", fg="#333333")
label_registration.pack()

button_search_user = tk.Button(registration_frame, text="SEARCH", command=search_user, width=15, height=1,
                           bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_add_user = tk.Button(registration_frame, text="ADD", command=add_user, width=15, height=1,
                           bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_update_user = tk.Button(registration_frame, text="UPDATE", command=update_user, width=15, height=1,
                           bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_delete_user = tk.Button(registration_frame, text="DELETE", command=delete_user, width=15, height=1,
                           bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_back_user = tk.Button(registration_frame, text="BACK", command=show_login_form, width=15, height=1,
                           bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))

button_search_user.bind("<Enter>", on_enter)
button_search_user.bind("<Leave>", on_leave)
button_add_user.bind("<Enter>", on_enter)
button_add_user.bind("<Leave>", on_leave)
button_update_user.bind("<Enter>", on_enter)
button_update_user.bind("<Leave>", on_leave)
button_delete_user.bind("<Enter>", on_enter)
button_delete_user.bind("<Leave>", on_leave)
button_back_user.bind("<Enter>", on_enter)
button_back_user.bind("<Leave>", on_leave)

button_search_user.grid(row=1, column=1, pady=5, padx=10)
button_add_user.grid(row=2, column=1, pady=5, padx=10)
button_update_user.grid(row=3, column=1, pady=5, padx=10)
button_delete_user.grid(row=4, column=1, pady=5, padx=10)
button_back_user.grid(row=5, column=1, pady=5, padx=10)

button_search_user.bind("<Return>", lambda event: search_user())
button_add_user.bind("<Return>", lambda event: add_user())
button_update_user.bind("<Return>", lambda event: update_user())
button_delete_user.bind("<Return>", lambda event: delete_user())
button_back_user.bind("<Return>", lambda event: show_login_form())

label_search_user = tk.Label(registration_frame, text="Search: ", font=("Helvetica", 12))
label_firstname = tk.Label(registration_frame, text="First Name:", font=("Helvetica", 12))
label_lastname = tk.Label(registration_frame, text="Last Name:", font=("Helvetica", 12))
label_middlename = tk.Label(registration_frame, text="Middle Name: ", font=("Helvetica", 12))
label_birthday = tk.Label(registration_frame, text="Birthday: ", font=("Helvetica", 12))
label_age = tk.Label(registration_frame, text="Age: ", font=("Helvetica", 12))
label_gender = tk.Label(registration_frame, text="Gender: ", font=("Helvetica", 12))
label_address = tk.Label(registration_frame, text="Address: ", font=("Helvetica", 12))
label_regusername = tk.Label(registration_frame, text="Username: ", font=("Helvetica", 12))
label_regpassword = tk.Label(registration_frame, text="Password: ", font=("Helvetica", 12))
label_email = tk.Label(registration_frame, text="Email: ", font=("Helvetica", 12))

label_search_user.grid(row=1, column=2)
label_firstname.grid(row=2, column=2)
label_lastname.grid(row=3, column=2)
label_middlename.grid(row=4, column=2)
label_birthday.grid(row=5, column=2)
label_age.grid(row=6, column=2, pady=5)
label_gender.grid(row=7, column=2, pady=5)
label_address.grid(row=8, column=2, pady=5)
label_regusername.grid(row=9, column=2, pady=5)
label_regpassword.grid(row=10, column=2, pady=5)
label_email.grid(row=11, column=2, pady=5)

validate_input = registration_frame.register(on_validate_input)
entry_search_user = tk.Entry(registration_frame)
entry_firstname = tk.Entry(registration_frame)
entry_lastname = tk.Entry(registration_frame)
entry_middlename = tk.Entry(registration_frame)
entry_birthday = tk.Entry(registration_frame, validate="key", validatecommand=(validate_input, "%S"))
entry_age = tk.Entry(registration_frame, validate="key", validatecommand=(validate_input, "%S"))
combo_gender = ttk.Combobox(registration_frame, values=["Male", "Female"], state="readonly")
entry_address = tk.Entry(registration_frame)
entry_regusername = tk.Entry(registration_frame, validate="key", validatecommand=(validate_input, "%S"))
entry_regpassword = tk.Entry(registration_frame, show="*", validate="key", validatecommand=(validate_input, "%S"))
entry_email = tk.Entry(registration_frame, validate="key", validatecommand=(validate_input, "%S"))

entry_search_user.grid(row=1, column=3)
entry_firstname.grid(row=2, column=3)
entry_lastname.grid(row=3, column=3)
entry_middlename.grid(row=4, column=3)
entry_birthday.grid(row=5, column=3)
entry_birthday.bind("<FocusOut>", calculate_age_from_event)
entry_age.grid(row=6, column=3)
combo_gender.grid(row=7, column=3)
entry_address.grid(row=8, column=3)
entry_regusername.grid(row=9, column=3)
entry_regpassword.grid(row=10, column=3)
entry_email.grid(row=11, column=3)

# Create the Treeview widget
tree_user = ttk.Treeview(registration_frame, columns=("User ID", "First Name", "Last Name", "Middle Name", "Birthday", "Age", "Gender", "Address", "Username", "Password", "Email"),
                           show="headings", selectmode="browse")
# Define the column headers
tree_user.heading("User ID", text="User ID")
tree_user.heading("First Name", text="First Name")
tree_user.heading("Last Name", text="Last Name")
tree_user.heading("Middle Name", text="Middle Name")
tree_user.heading("Birthday", text="Birthday")
tree_user.heading("Age", text="Age")
tree_user.heading("Gender", text="Gender")
tree_user.heading("Address", text="Address")
tree_user.heading("Username", text="Username")
tree_user.heading("Password", text="Password")
tree_user.heading("Email", text="Email")

# Set default size for the column headings
tree_user.column("User ID", minwidth=70)
tree_user.column("First Name", minwidth=100)
tree_user.column("Last Name", minwidth=100)
tree_user.column("Middle Name", minwidth=100)
tree_user.column("Birthday", minwidth=80)
tree_user.column("Age", minwidth=30)
tree_user.column("Gender", minwidth=50)
tree_user.column("Address", minwidth=200)
tree_user.column("Username", minwidth=100)
tree_user.column("Password", minwidth=100)
tree_user.column("Email", minwidth=160)

# Create the vertical scrollbar
vsb = ttk.Scrollbar(registration_frame, orient="vertical", command=tree_user.yview)
tree_user.configure(yscrollcommand=vsb.set)
vsb.grid(row=1, column=7, rowspan=6, sticky="ns")

# Create the horizontal scrollbar
hsb = ttk.Scrollbar(registration_frame, orient="horizontal", command=tree_user.xview)
tree_user.configure(xscrollcommand=hsb.set)
hsb.grid(row=7, column=4, columnspan=3, sticky="ew")

# Specify the position of the Treeview within the frame
tree_user.grid(row=1, column=4, rowspan=6, columnspan=3, padx=5, pady=5, sticky="nsew")  # Updated columnspan to 3

# Configure the column widths to fit the content
for col in ("User ID", "First Name", "Last Name", "Middle Name", "Birthday", "Age", "Gender", "Username", "Password", "Email"):
    tree_user.column(col, width=35, anchor="center")

# Bind the function to the Treeview selection event
tree_user.bind("<<TreeviewSelect>>", populate_entry_user_fields)

                                # MAIN FRAME

main_frame = tk.Frame(root, bg="#338BA8", padx=250, pady=50)

main_time_frame = tk.Frame(main_frame, bg="#ADD8E6", padx=15, pady=10)
main_time_frame.grid(row=1, column=2)

main_time = tk.Label(main_time_frame, font=('Proforma', 20, 'bold'), background='white', foreground='black')
main_time.pack()
time()  # Start the digital clock

display_image()
dashboard_frame = tk.Frame(main_frame, bg="#ADD8E6", padx=15, pady=10)
dashboard_frame.grid(row=1, column=1)

label_dashboard = tk.Label(dashboard_frame, text="DASHBOARD", font=custom_font3)
label_dashboard.pack()

button_frame = tk.Frame(main_frame, bg="#ADD8E6", padx=15, pady=10)
button_frame.grid(row=2, column=1)

button_tenant = tk.Button(button_frame, text="TENANT", command=show_tenant_frame, width=30, height=2,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
button_house = tk.Button(button_frame, text="HOUSE", command=show_house_frame, width=30, height=2,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
button_lease = tk.Button(button_frame, text="LEASE", command=show_lease_frame, width=30, height=2,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
button_payment = tk.Button(button_frame, text="PAYMENT", command=show_payment_frame, width=30, height=2,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
button_report = tk.Button(button_frame, text="REPORT", command=show_report_frame, width=30, height=2,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))
button_logout = tk.Button(button_frame, text="LOG OUT", command=show_login_form, width=30, height=2,
                          bg='white', activebackground="#B0B0B0", font=("Helvetica", 16, 'bold'))

# Binding the mouse hover events to the buttons
button_tenant.bind("<Enter>", on_enter)
button_tenant.bind("<Leave>", on_leave)
button_house.bind("<Enter>", on_enter)
button_house.bind("<Leave>", on_leave)
button_lease.bind("<Enter>", on_enter)
button_lease.bind("<Leave>", on_leave)
button_payment.bind("<Enter>", on_enter)
button_payment.bind("<Leave>", on_leave)
button_report.bind("<Enter>", on_enter)
button_report.bind("<Leave>", on_leave)
button_logout.bind("<Enter>", on_enter)
button_logout.bind("<Leave>", on_leave)

button_tenant.pack()
button_house.pack()
button_lease.pack()
button_payment.pack()
button_report.pack()
button_logout.pack()

                        # REPORT FRAME

report_main_frame = tk.Frame(root, bg="#338BA8")

create_report_frame = tk.Frame(report_main_frame, bg="#ADD8E6", padx=330, pady=10)
create_report_frame.grid(row=1, column=1)

report_heading = tk.Label(create_report_frame, text="CREATE REPORT", font=custom_font3)
report_heading.pack()

button_report_frame = tk.Frame(report_main_frame, bg="#ADD8E6", padx=15, pady=10)
button_report_frame.grid(row=2, column=1)

button_report_tenant= tk.Button(button_report_frame, text="TENANT", width=20, height=3, command=generate_tenant_report,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_report_house = tk.Button(button_report_frame, text="HOUSE", width=20, height=3, command=generate_house_report,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_report_lease = tk.Button(button_report_frame, text="LEASE", width=20, height=3, command=generate_lease_report,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_report_payment = tk.Button(button_report_frame, text="PAYMENT", width=20, height=3, command=generate_payment_report,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_report_back = tk.Button(button_report_frame, text="BACK", width=20, height=3, command=go_back,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))

# Binding the mouse hover events to the buttons
button_report_tenant.bind("<Enter>", on_enter)
button_report_tenant.bind("<Leave>", on_leave)
button_report_house.bind("<Enter>", on_enter)
button_report_house.bind("<Leave>", on_leave)
button_report_lease.bind("<Enter>", on_enter)
button_report_lease.bind("<Leave>", on_leave)
button_report_payment.bind("<Enter>", on_enter)
button_report_payment.bind("<Leave>", on_leave)
button_report_back.bind("<Enter>", on_enter)
button_report_back.bind("<Leave>", on_leave)

button_report_tenant.pack()
button_report_house.pack()
button_report_lease.pack()
button_report_payment.pack()
button_report_back.pack()

                                    # TENANT FRAME
tenant_frame = tk.Frame(root, bg="#ADD8E6")

tenant_heading_frame = tk.Frame(tenant_frame, bg="#338BA8", padx=250, pady=10)
tenant_heading_frame.grid(row=0, column=4, pady=20)

tenant_heading = tk.Label(tenant_heading_frame, text="TENANT TABLE", font=custom_font3, bg="#F0F0F0", fg="#333333")
tenant_heading.pack()

button_search_tenant = tk.Button(tenant_frame, text="SEARCH", width=15, height=2, command=search_tenant,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_add_tenant = tk.Button(tenant_frame, text="ADD", width=15, height=2, command=add_tenant,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_update_tenant = tk.Button(tenant_frame, text="UPDATE", width=15, height=2, command=update_tenant,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_delete_tenant = tk.Button(tenant_frame, text="DELETE", width=15, height=2, command=delete_tenant,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_back_tenant = tk.Button(tenant_frame, text="BACK", width=15, height=2, command=go_back,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))

# Binding the mouse hover events to the buttons
button_search_tenant.bind("<Enter>", on_enter)
button_search_tenant.bind("<Leave>", on_leave)
button_add_tenant.bind("<Enter>", on_enter)
button_add_tenant.bind("<Leave>", on_leave)
button_update_tenant.bind("<Enter>", on_enter)
button_update_tenant.bind("<Leave>", on_leave)
button_delete_tenant.bind("<Enter>", on_enter)
button_delete_tenant.bind("<Leave>", on_leave)
button_back_tenant.bind("<Enter>", on_enter)
button_back_tenant.bind("<Leave>", on_leave)

button_search_tenant.grid(row=1, column=1, pady=5, padx=10)
button_add_tenant.grid(row=2, column=1, pady=5, padx=10)
button_update_tenant.grid(row=3, column=1, pady=5, padx=10)
button_delete_tenant.grid(row=4, column=1, pady=5, padx=10)
button_back_tenant.grid(row=5, column=1, pady=5, padx=10)

label_search = tk.Label(tenant_frame, text="Search: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_name = tk.Label(tenant_frame, text="Tenant Name: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_occupation = tk.Label(tenant_frame, text="Occupation: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_birthday = tk.Label(tenant_frame, text="Birthday: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_age = tk.Label(tenant_frame, text="Age: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_gender = tk.Label(tenant_frame, text="Gender: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_email = tk.Label(tenant_frame, text="Email: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_phone = tk.Label(tenant_frame, text="Phone Number: ", bg="#F0F0F0", font=("Helvetica", 12))

label_search.grid(row=1, column=2)
label_tenant_name.grid(row=2, column=2)
label_tenant_occupation.grid(row=3, column=2)
label_tenant_birthday.grid(row=4, column=2)
label_tenant_age.grid(row=5, column=2)
label_tenant_gender.grid(row=6, column=2, pady=10, padx=5)
label_tenant_email.grid(row=7, column=2)
label_tenant_phone.grid(row=8, column=2, pady=20)

validate_input = tenant_frame.register(on_validate_input)
entry_search = tk.Entry(tenant_frame)
entry_tenant_name = tk.Entry(tenant_frame)
entry_tenant_occupation = tk.Entry(tenant_frame)
entry_tenant_birthday = tk.Entry(tenant_frame, validate="key", validatecommand=(validate_input, "%S"))
entry_tenant_birthday.bind("<FocusOut>", calculate_tenant_age_from_event)
entry_tenant_age = tk.Entry(tenant_frame, validate="key", validatecommand=(validate_input, "%S"))
combo_tenant_gender = ttk.Combobox(tenant_frame, values=["Male", "Female"], state="readonly")
entry_tenant_email = tk.Entry(tenant_frame, validate="key", validatecommand=(validate_input, "%S"))
entry_tenant_phone = tk.Entry(tenant_frame, validate="key", validatecommand=(validate_input, "%S"))

entry_search.grid(row=1, column=3)
entry_tenant_name.grid(row=2, column=3)
entry_tenant_occupation.grid(row=3, column=3)
entry_tenant_birthday.grid(row=4, column=3)
entry_tenant_age.grid(row=5, column=3)
combo_tenant_gender.grid(row=6, column=3)
entry_tenant_email.grid(row=7, column=3)
entry_tenant_phone.grid(row=8, column=3)

# Create the Treeview widget
tree_tenant = ttk.Treeview(tenant_frame, columns=("Tenant ID", "Tenant Name", "Occupation", "Birthday", "Age", "Gender", "Email", "Phone Number"),
                           show="headings", selectmode="browse")
# Define the column headers
tree_tenant.heading("Tenant ID", text="Tenant ID")
tree_tenant.heading("Tenant Name", text="Tenant Name")
tree_tenant.heading("Occupation", text="Occupation")
tree_tenant.heading("Birthday", text="Birthday")
tree_tenant.heading("Age", text="Age")
tree_tenant.heading("Gender", text="Gender")
tree_tenant.heading("Email", text="Email")
tree_tenant.heading("Phone Number", text="Phone Number")

# Set default size for the column headings
tree_tenant.column("Tenant ID", minwidth=70)
tree_tenant.column("Tenant Name", minwidth=120)
tree_tenant.column("Occupation", minwidth=120)
tree_tenant.column("Birthday", minwidth=80)
tree_tenant.column("Age", minwidth=70)
tree_tenant.column("Gender", minwidth=90)
tree_tenant.column("Email", minwidth=150)
tree_tenant.column("Phone Number", minwidth=120)

# Create the vertical scrollbar
vsb = ttk.Scrollbar(tenant_frame, orient="vertical", command=tree_tenant.yview)
tree_tenant.configure(yscrollcommand=vsb.set)
vsb.grid(row=1, column=7, rowspan=6, sticky="ns", padx=10)

# Create the horizontal scrollbar
hsb = ttk.Scrollbar(tenant_frame, orient="horizontal", command=tree_tenant.xview)
tree_tenant.configure(xscrollcommand=hsb.set)
hsb.grid(row=7, column=4, columnspan=3, sticky="ew", pady=10)

# Specify the position of the Treeview within the frame
tree_tenant.grid(row=1, column=4, rowspan=6, columnspan=3, padx=5, pady=5, sticky="nsew")  # Updated columnspan to 3

# Configure the column widths to fit the content
for col in ("Tenant ID", "Tenant Name", "Occupation", "Birthday", "Age", "Gender", "Email", "Phone Number"):
    tree_tenant.column(col, width=64, anchor="center")

# Bind the function to the Treeview selection event
tree_tenant.bind("<<TreeviewSelect>>", populate_entry_tenant_fields)

                                # HOUSE FRAME
house_frame = tk.Frame(root, bg="#ADD8E6")

house_heading_frame = tk.Frame(house_frame,bg="#338BA8", padx=270, pady=10)
house_heading_frame.grid(row=0, column=4, pady=20)

house_heading = tk.Label(house_heading_frame, text="HOUSE TABLE", font=custom_font3, bg="#F0F0F0", fg="#333333")
house_heading.pack()

button_search_house = tk.Button(house_frame, text="SEARCH", width=15, height=2, command=search_house,
                             bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_add_house = tk.Button(house_frame, text="ADD", width=15, height=2, command=add_house,
                             bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_update_house = tk.Button(house_frame, text="UPDATE", width=15, height=2, command=update_house,
                             bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_delete_house = tk.Button(house_frame, text="DELETE", width=15, height=2, command=delete_house,
                             bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_back_house = tk.Button(house_frame, text="BACK", width=15, height=2, command=go_back,
                             bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))

# Binding the mouse hover events to the buttons
button_search_house.bind("<Enter>", on_enter)
button_search_house.bind("<Leave>", on_leave)
button_add_house.bind("<Enter>", on_enter)
button_add_house.bind("<Leave>", on_leave)
button_update_house.bind("<Enter>", on_enter)
button_update_house.bind("<Leave>", on_leave)
button_delete_house.bind("<Enter>", on_enter)
button_delete_house.bind("<Leave>", on_leave)
button_back_house.bind("<Enter>", on_enter)
button_back_house.bind("<Leave>", on_leave)

button_search_house.grid(row=1, column=1, pady=5, padx=10)
button_add_house.grid(row=2, column=1, pady=5, padx=10)
button_update_house.grid(row=3, column=1, pady=5, padx=10)
button_delete_house.grid(row=4, column=1, pady=5, padx=10)
button_back_house.grid(row=5, column=1, pady=5, padx=10)

label_search_house = tk.Label(house_frame, text="Search: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_name = tk.Label(house_frame, text="House Name: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_availability = tk.Label(house_frame, text="Availability: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_rent = tk.Label(house_frame, text="Rent Amount: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_occupants = tk.Label(house_frame, text="Occupants: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_location = tk.Label(house_frame, text="Location: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_description = tk.Label(house_frame, text="Description: ", bg="#F0F0F0", font=("Helvetica", 12))

label_search_house.grid(row=1, column=2, pady=10)
label_house_name.grid(row=2, column=2, pady=10)
label_house_availability.grid(row=3, column=2, pady=10)
label_house_rent.grid(row=4, column=2, pady=10)
label_house_occupants.grid(row=5, column=2, pady=10)
label_house_location.grid(row=6, column=2, pady=10)
label_house_description.grid(row=8, column=2, pady=10)

validate_input = house_frame.register(on_validate_input)
entry_search_house = tk.Entry(house_frame)
entry_house_name = tk.Entry(house_frame)
combo_house_availability = ttk.Combobox(house_frame, values=["Available", "Occupied"], state="readonly")
entry_house_rent = tk.Entry(house_frame, validate="key", validatecommand=(validate_input, "%S"))
combo_house_occupants = ttk.Combobox(house_frame, values=["one","two","three","four","five","six","seven","eight","nine"], state="readonly")
entry_house_location = tk.Entry(house_frame)
text_house_description = tk.Text(house_frame, height=4, wrap=tk.WORD)

entry_search_house.grid(row=1, column=3)
entry_house_name.grid(row=2, column=3)
combo_house_availability.grid(row=3, column=3)
entry_house_rent.grid(row=4, column=3)
combo_house_occupants.grid(row=5, column=3)
entry_house_location.grid(row=6, column=3)
text_house_description.grid(row=8, column=3, columnspan=2, padx=5, pady=10, sticky="nsew")

# Create the Treeview widget
tree_house = ttk.Treeview(house_frame, columns=("House ID", "House Name", "Availability", "Rent Amount", "Occupant", "Location", "Description"),
                          show="headings", selectmode="browse")

# Define the column headers
tree_house.heading("House ID", text="House ID")
tree_house.heading("House Name", text="House Name")
tree_house.heading("Availability", text="Availability")
tree_house.heading("Rent Amount", text="Rent Amount")
tree_house.heading("Occupant", text="Occupant")
tree_house.heading("Location", text="Location")
tree_house.heading("Description", text="Description")

# Set default size for the column headings in tree_house
tree_house.column("House ID", minwidth=70)
tree_house.column("House Name", minwidth=150)
tree_house.column("Availability", minwidth=100)
tree_house.column("Rent Amount", minwidth=100)
tree_house.column("Occupant", minwidth=70)
tree_house.column("Location", minwidth=150)
tree_house.column("Description", minwidth=150)

# Create the vertical scrollbar
vsb = ttk.Scrollbar(house_frame, orient="vertical", command=tree_house.yview)
tree_house.configure(yscrollcommand=vsb.set)
vsb.grid(row=1, column=7, rowspan=6, sticky="ns", padx=10)

# Create the horizontal scrollbar
hsb = ttk.Scrollbar(house_frame, orient="horizontal", command=tree_house.xview)
tree_house.configure(xscrollcommand=hsb.set)
hsb.grid(row=7, column=4, columnspan=2, sticky="ew", pady=10)

# Specify the position of the Treeview within the frame
tree_house.grid(row=1, column=4, rowspan=6, columnspan=2, padx=5, pady=5, sticky="nsew")  # Updated columnspan to 3

# Configure the column widths to fit the content
for col in ("House ID", "House Name", "Availability", "Rent Amount", "Occupant", "Location", "Description"):
    tree_house.column(col, width=75, anchor="center")

# Bind the function to the Treeview selection event
tree_house.bind("<<TreeviewSelect>>", populate_entry_house_fields)


                                # LEASE FRAME
lease_frame = tk.Frame(root, bg="#B1D4E0")

lease_heading_frame = tk.Frame(lease_frame,bg="#338BA8", padx=270, pady=10)
lease_heading_frame.grid(row=0, column=4, pady=20)

label_lease_heading = tk.Label(lease_heading_frame, text="LEASE TABLE", font=custom_font3, bg="#F0F0F0", fg="#333333")
label_lease_heading.pack()

button_search_lease = tk.Button(lease_frame, text="SEARCH", width=15, height=2, command=search_lease,
                                bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_add_lease = tk.Button(lease_frame, text="ADD", width=15, height=2, command=add_lease,
                                bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_update_lease = tk.Button(lease_frame, text="UPDATE", width=15, height=2, command=update_lease,
                                bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_delete_lease = tk.Button(lease_frame, text="DELETE", width=15, height=2, command=delete_lease,
                                bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_back_lease = tk.Button(lease_frame, text="BACK", width=15, height=2, command=go_back,
                                bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))

# Binding the mouse hover events to the buttons
button_search_lease.bind("<Enter>", on_enter)
button_search_lease.bind("<Leave>", on_leave)
button_add_lease.bind("<Enter>", on_enter)
button_add_lease.bind("<Leave>", on_leave)
button_update_lease.bind("<Enter>", on_enter)
button_update_lease.bind("<Leave>", on_leave)
button_delete_lease.bind("<Enter>", on_enter)
button_delete_lease.bind("<Leave>", on_leave)
button_back_lease.bind("<Enter>", on_enter)
button_back_lease.bind("<Leave>", on_leave)

button_search_lease.grid(row=1, column=1, pady=5, padx=10)
button_add_lease.grid(row=2, column=1, pady=5, padx=10)
button_update_lease.grid(row=3, column=1, pady=5, padx=10)
button_delete_lease.grid(row=4, column=1, pady=5, padx=10)
button_back_lease.grid(row=5, column=1, pady=5, padx=10)

label_search_lease = tk.Label(lease_frame, text="Search: ", bg="#F0F0F0", font=("Helvetica", 12))
label_house_ID = tk.Label(lease_frame, text="House ID: ", bg="#F0F0F0", font=("Helvetica", 12))
label_tenant_ID = tk.Label(lease_frame, text="Tenant ID: ", bg="#F0F0F0", font=("Helvetica", 12))
label_lease_duration = tk.Label(lease_frame, text="Lease Duration: ", bg="#F0F0F0", font=("Helvetica", 12))
label_lease_start_date = tk.Label(lease_frame, text="Start Date: ", bg="#F0F0F0", font=("Helvetica", 12))
label_lease_end_date = tk.Label(lease_frame, text="End Date: ", bg="#F0F0F0", font=("Helvetica", 12))
label_lease_period = tk.Label(lease_frame, text="Lease Period: ", bg="#F0F0F0", font=("Helvetica", 12))
label_lease_amount = tk.Label(lease_frame, text="Lease Amount: ", bg="#F0F0F0", font=("Helvetica", 12))
label_lease_deposit = tk.Label(lease_frame, text="Lease Deposit: ", bg="#F0F0F0", font=("Helvetica", 12))

label_search_lease.grid(row=1, column=2)
label_house_ID.grid(row=2, column=2)
label_tenant_ID.grid(row=3, column=2)
label_lease_duration.grid(row=4, column=2)
label_lease_start_date.grid(row=5, column=2)
label_lease_end_date.grid(row=6, column=2, pady=5, padx=5)
label_lease_period.grid(row=7, column=2, pady=5, padx=5)
label_lease_amount.grid(row=8, column=2, pady=5, padx=5)
label_lease_deposit.grid(row=9, column=2, pady=15, padx=5)

validate_input = lease_frame.register(on_validate_input)
entry_search_lease = tk.Entry(lease_frame)
combo_house_id = ttk.Combobox(lease_frame, values=(), state="readonly")
update_house_combo_box()

# Bind the update_lease_amount function to the <<ComboboxSelected>> event of combo_house_id
combo_house_id.bind("<<ComboboxSelected>>", update_lease_amount)

combo_tenant_id = ttk.Combobox(lease_frame, values=(), state="readonly")
update_tenant_combo_box()

entry_lease_duration = tk.Entry(lease_frame)
entry_lease_duration.bind("<FocusOut>", update_end_date)
entry_lease_start_date = tk.Entry(lease_frame, validate="key", validatecommand=(validate_input, "%S"))
entry_lease_start_date.bind("<FocusOut>", update_end_date)

entry_lease_end_date = tk.Entry(lease_frame, validate="key", validatecommand=(validate_input, "%S"))
combo_lease_period = ttk.Combobox(lease_frame, values=["Weekly", "Monthly", "Yearly"], state="readonly")
entry_lease_amount = tk.Entry(lease_frame, validate="key", validatecommand=(validate_input, "%S"))
entry_lease_deposit = tk.Entry(lease_frame, validate="key", validatecommand=(validate_input, "%S"))

entry_search_lease.grid(row=1, column=3, pady=5, padx=5)
combo_house_id.grid(row=2, column=3, pady=5, padx=5)
combo_tenant_id.grid(row=3, column=3, pady=5, padx=5)
entry_lease_duration.grid(row=4, column=3, pady=5, padx=5)
entry_lease_start_date.grid(row=5, column=3, pady=5, padx=5)
entry_lease_end_date.grid(row=6, column=3, pady=5, padx=5)
combo_lease_period.grid(row=7, column=3, pady=5, padx=5)
entry_lease_amount.grid(row=8, column=3, pady=5, padx=5)
entry_lease_deposit.grid(row=9, column=3, pady=5, padx=5)

# Create the Treeview widget
tree_lease = ttk.Treeview(lease_frame, columns=("Lease ID", "House ID", "Tenant ID", "Duration", "Start Date", "End Date", "Period", "Amount", "Deposit"),
                          show="headings", selectmode="browse")

# Define the column headers
tree_lease.heading("Lease ID", text="Lease ID")
tree_lease.heading("House ID", text="House ID")
tree_lease.heading("Tenant ID", text="Tenant ID")
tree_lease.heading("Duration", text="Duration")
tree_lease.heading("Start Date", text="Start Date")
tree_lease.heading("End Date", text="End Date")
tree_lease.heading("Period", text="Period")
tree_lease.heading("Amount", text="Amount")
tree_lease.heading("Deposit", text="Deposit")

# Set default size for the column headings in tree_lease
tree_lease.column("Lease ID", minwidth=60)
tree_lease.column("House ID", minwidth=60)
tree_lease.column("Tenant ID", minwidth=60)
tree_lease.column("Duration", minwidth=60)
tree_lease.column("Start Date", minwidth=80)
tree_lease.column("End Date", minwidth=80)
tree_lease.column("Period", minwidth=70)
tree_lease.column("Amount", minwidth=70)
tree_lease.column("Deposit", minwidth=70)

# Create the vertical scrollbar
vsb = ttk.Scrollbar(lease_frame, orient="vertical", command=tree_lease.yview)
tree_lease.configure(yscrollcommand=vsb.set)
vsb.grid(row=1, column=7, rowspan=6, sticky="ns", padx=9)

# Create the horizontal scrollbar
hsb = ttk.Scrollbar(lease_frame, orient="horizontal", command=tree_lease.xview)
tree_lease.configure(xscrollcommand=hsb.set)
hsb.grid(row=7, column=4, columnspan=3, sticky="ew", pady=10)

# Specify the position of the Treeview within the frame
tree_lease.grid(row=1, column=4, rowspan=6, columnspan=3, padx=10, pady=5, sticky="nsew")  # Updated columnspan to 3

# Configure the column widths to fit the content
for col in ("Lease ID", "House ID", "Tenant ID", "Duration", "Start Date", "End Date", "Period", "Amount", "Deposit"):
    tree_lease.column(col, width=54, anchor="center")

# Bind the function to the Treeview selection event
tree_lease.bind("<<TreeviewSelect>>", populate_entry_lease_fields)

                                # PAYMENT FRAME
payment_frame = tk.Frame(root, bg="#B1D4E0")

payment_heading_frame = tk.Frame(payment_frame,bg="#338BA8", padx=230, pady=10)
payment_heading_frame.grid(row=0, column=4, pady=20)

payment_heading = tk.Label(payment_heading_frame, text="PAYMENT TABLE", font=custom_font3, bg="#F0F0F0", fg="#333333")
payment_heading.pack()

button_search_payment = tk.Button(payment_frame, text="SEARCH", width=15, height=2, command=search_payment,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_add_payment = tk.Button(payment_frame, text="ADD", width=15, height=2, command=add_payment,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_update_payment = tk.Button(payment_frame, text="UPDATE", width=15, height=2, command=update_payment,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_delete_payment= tk.Button(payment_frame, text="DELETE", width=15, height=2, command=delete_payment,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))
button_back_payment = tk.Button(payment_frame, text="BACK", width=15, height=2, command=go_back,
                                 bg='white', activebackground="#B0B0B0", font=("Helvetica", 12, 'bold'))

# Binding the mouse hover events to the buttons
button_search_payment.bind("<Enter>", on_enter)
button_search_payment.bind("<Leave>", on_leave)
button_add_payment.bind("<Enter>", on_enter)
button_add_payment.bind("<Leave>", on_leave)
button_update_payment.bind("<Enter>", on_enter)
button_update_payment.bind("<Leave>", on_leave)
button_delete_payment.bind("<Enter>", on_enter)
button_delete_payment.bind("<Leave>", on_leave)
button_back_payment.bind("<Enter>", on_enter)
button_back_payment.bind("<Leave>", on_leave)

button_search_payment.grid(row=1, column=1, pady=5, padx=10)
button_add_payment.grid(row=2, column=1, pady=5, padx=10)
button_update_payment.grid(row=3, column=1, pady=5, padx=10)
button_delete_payment.grid(row=4, column=1, pady=5, padx=10)
button_back_payment.grid(row=5, column=1, pady=5, padx=10)

label_search_payment = tk.Label(payment_frame, text="Search: ", bg="#F0F0F0", font=("Helvetica", 12))
label_payment_house_ID = tk.Label(payment_frame, text="House ID: ", bg="#F0F0F0", font=("Helvetica", 12))
label_payment_tenant_ID = tk.Label(payment_frame, text="Tenant ID: ", bg="#F0F0F0", font=("Helvetica", 12))
label_payment_amount = tk.Label(payment_frame, text="Payment Amount: ", bg="#F0F0F0", font=("Helvetica", 12))
label_payment_method = tk.Label(payment_frame, text="Payment Method: ", bg="#F0F0F0", font=("Helvetica", 12))

label_search_payment.grid(row=1, column=2, pady=10)
label_payment_house_ID.grid(row=2, column=2, pady=10)
label_payment_tenant_ID.grid(row=3, column=2, pady=10)
label_payment_amount.grid(row=4, column=2, pady=10)
label_payment_method.grid(row=5, column=2, pady=10, padx=5)

validate_input = payment_frame.register(on_validate_input)
entry_search_payment = tk.Entry(payment_frame)
combo_house_payment_id = ttk.Combobox(payment_frame, values=(), state="readonly")
update_house_payment_combo_box()
combo_house_payment_id.bind("<<ComboboxSelected>>", update_tenant_payment_combo_box)
combo_tenant_payment_id = ttk.Combobox(payment_frame, values=(), state="readonly")
update_tenant_payment_combo_box()
combo_tenant_payment_id.bind("<<ComboboxSelected>>", update_payment_amount)
entry_payment_amount = tk.Entry(payment_frame, validate="key", validatecommand=(validate_input, "%S"))
combo_payment_method = ttk.Combobox(payment_frame, values=["Cash", "Online", "Cheque", "Credit Card"], state="readonly")

entry_search_payment.grid(row=1, column=3)
combo_house_payment_id.grid(row=2, column=3)
combo_tenant_payment_id.grid(row=3, column=3)
entry_payment_amount.grid(row=4, column=3)
combo_payment_method.grid(row=5, column=3)

# Create the Treeview widget
tree_payment = ttk.Treeview(payment_frame, columns=("Payment ID", "House ID", "Tenant ID", "Receipt Number", "Amount", "Total", "Due", "Method"),
                            show="headings", selectmode="browse")

# Define the column headers
tree_payment.heading("Payment ID", text="Payment ID")
tree_payment.heading("House ID", text="House ID")
tree_payment.heading("Tenant ID", text="Tenant ID")
tree_payment.heading("Receipt Number", text="Receipt Number")
tree_payment.heading("Amount", text="Amount")
tree_payment.heading("Total", text="Total")
tree_payment.heading("Due", text="Due")
tree_payment.heading("Method", text="Method")

# Set default size for the column headings in tree_lease
tree_payment.column("Payment ID", minwidth=70)
tree_payment.column("House ID", minwidth=70)
tree_payment.column("Tenant ID", minwidth=70)
tree_payment.column("Receipt Number", minwidth=130)
tree_payment.column("Amount", minwidth=55)
tree_payment.column("Total", minwidth=60)
tree_payment.column("Due", minwidth=140)
tree_payment.column("Method", minwidth=80)

# Create the vertical scrollbar
vsb = ttk.Scrollbar(payment_frame, orient="vertical", command=tree_payment.yview)
tree_payment.configure(yscrollcommand=vsb.set)
vsb.grid(row=1, column=7, rowspan=6, sticky="ns", padx=10)

# Create the horizontal scrollbar
hsb = ttk.Scrollbar(payment_frame, orient="horizontal", command=tree_payment.xview)
tree_payment.configure(xscrollcommand=hsb.set)
hsb.grid(row=7, column=4, columnspan=3, sticky="ew", pady=10)

# Specify the position of the Treeview within the frame
tree_payment.grid(row=1, column=4, rowspan=6, columnspan=3, padx=5, pady=5, sticky="nsew")  # Updated columnspan to 3

# Configure the column widths to fit the content
for col in ("Payment ID", "House ID", "Tenant ID", "Receipt Number", "Amount", "Total", "Due", "Method"):
    tree_payment.column(col, width=61, anchor="center")

# Bind the function to the Treeview selection event
tree_payment.bind("<<TreeviewSelect>>", populate_entry_payment_fields)

root.mainloop()
