import sqlite3
from tkinter import messagebox


class ManipulateDB:
    def add_to_database(self, student_id, first_name, last_name, course_id, year_level, grades, status):
        try:
            conn = sqlite3.connect("Database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Student (StudentID, StudentFirstName, StudentLastName, \
                           CourseID, YearLevel, Grades, Status) \
                           VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (student_id, first_name, last_name, course_id, year_level, grades, status))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error while adding to database:", e)

    def is_student_id_exists(self, student_id):
        try:
            conn = sqlite3.connect("Database.db")
            cursor = conn.cursor()

            # Execute the query to check if the student ID exists
            cursor.execute("SELECT EXISTS(SELECT 1 FROM Student WHERE StudentID = ?)", (student_id,))
            result = cursor.fetchone()[0]

            conn.close()

            return result == 1  # Convert the result to a boolean value (True if exists, False if not)

        except Exception as e:
            print("Error while checking if student ID exists:", e)
            return False  # In case of any error, assume student ID does not exist

    def get_student_status(self, student_id):
        try:
            conn = sqlite3.connect("Database.db")
            cursor = conn.cursor()

            # Execute the query to fetch the student status
            cursor.execute("SELECT Status FROM Student WHERE StudentID = ?", (student_id,))
            result = cursor.fetchone()

            conn.close()

            if result is not None:
                return result[0]
            else:
                return None

        except Exception as e:
            print("Error while fetching student status:", e)
            return None

    def update_database(self, student_id, updated_student_number, updated_first_name, updated_last_name,
                        updated_course, updated_year, updated_grades, updated_status):
        self.conn = sqlite3.connect('Database.db')
        self.strSQL = "UPDATE Student SET StudentID=?, StudentFirstName=?, StudentLastName=?, " \
                      "CourseID=?, YearLevel=?, Grades=?, Status=? WHERE StudentID=?"
        self.cursor = self.conn.execute(self.strSQL, (updated_student_number, updated_first_name,
                                                      updated_last_name, updated_course, updated_year,
                                                      updated_grades, updated_status, student_id))
        self.conn.commit()
        self.cursor.close()

    def remove_from_database(self, student_id):
        self.conn = sqlite3.connect('Database.db')
        self.strSQL = "DELETE FROM Student WHERE StudentID = ?"
        self.cursor = self.conn.execute(self.strSQL, (student_id,))
        self.conn.commit()
        self.cursor.close()
        messagebox.Message("Successfully removed from the database.")

    def create_table(self):
        try:
            conn = sqlite3.connect("Database.db")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Student (
                    StudentID INTEGER PRIMARY KEY,
                    StudentFirstName TEXT NOT NULL,
                    StudentLastName TEXT NOT NULL,
                    CourseID TEXT NOT NULL,
                    YearLevel TEXT NOT NULL,
                    Grades REAL NOT NULL,
                    Status TEXT NOT NULL  -- Add the "Status" column here
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error creating table:", e)


