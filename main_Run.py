import cv2
import csv
import datetime
from tkinter import *
from tkinter import messagebox, filedialog
import mysql.connector

# Paths for required resources
STUDENT_DETAILS_PATH = "path/to/student_details"
TRAINING_LABEL_PATH = "path/to/trained_data"
ATTENDANCE_PATH = "path/to/attendance_data"
DB_CONFIG = {'host': 'localhost', 'user': 'root', 'password': '', 'database_auto': 'attendance'}

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System")
        self.root.geometry("600x400")
        
    def automatic_attendance(self):
        """Perform automatic attendance using face recognition"""
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(f"{TRAINING_LABEL_PATH}/Trainer.yml")
            detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            
            cam = cv2.VideoCapture(0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            attendance = []
            
            while True:
                ret, frame = cam.read()
                if not ret:
                    messagebox.showerror("Error", "Unable to access the camera.")
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                    
                    if confidence < 100:
                        student_name = self.get_student_name(id)
                        confidence_text = f"Confidence: {round(100 - confidence)}%"
                        cv2.putText(frame, f"ID: {student_name}", (x, y-10), font, 0.9, (255, 255, 255), 2)
                        cv2.putText(frame, confidence_text, (x, y+h+30), font, 0.9, (255, 255, 255), 2)

                        # Mark Attendance
                        if student_name not in attendance:
                            self.mark_attendance(student_name)
                            attendance.append(student_name)
                    else:
                        cv2.putText(frame, "Unknown", (x, y-10), font, 0.9, (0, 0, 255), 2)
                        
                cv2.imshow("Attendance - Face Recognition", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cam.release()
            cv2.destroyAllWindows()
            
            messagebox.showinfo("Attendance", "Attendance marking complete.")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_student_name(self, enrollment_id):
        """Get student name from enrollment ID"""
        try:
            with open(f"{STUDENT_DETAILS_PATH}/StudentDetails.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == str(enrollment_id):
                        return row[1]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_attendance(self, student_name):
        """Mark attendance in the system"""
        try:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.datetime.now().strftime('%H:%M:%S')

            with open(f"{ATTENDANCE_PATH}/{current_date}_attendance.csv", "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([student_name, current_time])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def manually_fill_attendance(self):
        """Open manual attendance window"""
        manual_window = Toplevel(self.root)
        manual_window.title("Manually Fill Attendance")
        manual_window.geometry('400x400')

        student_list = self.get_student_list()
        
        # Create Listbox to select students
        listbox = Listbox(
            manual_window,
            selectmode=MULTIPLE,
            width=40,
            height=10
        )
        
        for student in student_list:
            listbox.insert(END, student)
        
        listbox.pack(pady=20)

        # Mark Attendance Button
        def mark_manual_attendance():
            selected_students = [listbox.get(i) for i in listbox.curselection()]
            for student in selected_students:
                self.mark_attendance(student)
            messagebox.showinfo("Attendance", "Manual attendance marked successfully.")
            manual_window.destroy()

        mark_button = Button(
            manual_window, 
            text="Mark Attendance", 
            command=mark_manual_attendance,
            width=20, 
            height=2
        )
        mark_button.pack()

    def get_student_list(self):
        """Retrieve list of students"""
        student_list = []
        try:
            with open(f"{STUDENT_DETAILS_PATH}/StudentDetails.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    student_list.append(row[1])
        except Exception as e:
            messagebox.showerror("Error", str(e))
        return student_list

    def view_attendance(self):
        """View past attendance records"""
        try:
            # Open file dialog to select date
            date = filedialog.askopenfilename(
                title="Select Attendance File", 
                filetypes=(("CSV Files", "*.csv"),)
            )
            
            if not date:
                return
            
            with open(date, "r") as file:
                reader = csv.reader(file)
                history_window = Toplevel(self.root)
                history_window.title("Attendance History")
                history_window.geometry('500x500')

                listbox = Listbox(history_window, width=50, height=20)
                for row in reader:
                    listbox.insert(END, f"{row[0]} - {row[1]}")
                listbox.pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def connect_db(self):
        """Establish connection with the MySQL database"""
        try:
            connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database_auto']
            )
            return connection
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return None

    def mark_attendance_db(self, student_name):
        """Mark attendance in the database"""
        connection = self.connect_db()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO attendance (student_name, attendance_time) VALUES (%s, %s)"
            cursor.execute(query, (student_name, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            connection.commit()
            cursor.close()
            connection.close()
            messagebox.showinfo("Success", "Attendance marked successfully.")
