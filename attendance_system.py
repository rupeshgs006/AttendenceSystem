import tkinter as tk
from tkinter import Label, Button, Entry, messagebox
import cv2
import os
import datetime
import csv
import numpy as np
from PIL import Image

# Path Configuration
TRAINING_IMAGE_PATH = "TrainingImage"
TRAINING_LABEL_PATH = "TrainingImageLabel"
STUDENT_DETAILS_PATH = "StudentDetails"
ATTENDANCE_FILE_PATH = "Attendance.csv"

# Ensure directories exist
for path in [TRAINING_IMAGE_PATH, TRAINING_LABEL_PATH, STUDENT_DETAILS_PATH]:
    os.makedirs(path, exist_ok=True)

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System")
        self.root.geometry('1280x720')

        # Header
        self.header = self.create_label(self.root, "Attendance Management System", 80, 20, width=50, height=3)

        # Enrollment Input Section
        self.create_label(self.root, "Enter Enrollment: ", 200, 200)
        self.enrollment_entry = self.create_entry(self.root, 550, 210)

        # Name Input Section
        self.create_label(self.root, "Enter Name: ", 200, 300)
        self.name_entry = self.create_entry(self.root, 550, 310)

        # Buttons
        button_configs = [
            ("Clear Enrollment", self.clear_enrollment, 950, 210),
            ("Clear Name", self.clear_name, 950, 310),
            ("Take Images", self.take_images, 90, 500),
            ("Train Images", self.train_images, 390, 500),
            ("Start Automatic Attendance", self.start_automatic_attendance, 690, 500),
            ("Close App", self.close_app, 950, 600)
        ]

        # Create Buttons
        for text, command, x, y in button_configs:
            self.create_button(self.root, text, command, x, y)

    def create_label(self, parent, text, x, y, width=20, height=2):
        lbl = Label(parent, text=text, width=width, height=height, fg="black", bg="grey", font=('times', 15, 'bold'))
        lbl.place(x=x, y=y)
        return lbl

    def create_entry(self, parent, x, y, width=20):
        entry = Entry(parent, width=width, font=('times', 25))
        entry.place(x=x, y=y)
        return entry

    def create_button(self, parent, text, command, x, y):
        btn = Button(parent, text=text, command=command, fg="black", bg="SkyBlue1", width=20, height=3, font=('times', 15, 'bold'))
        btn.place(x=x, y=y)
        return btn

    def clear_enrollment(self):
        self.enrollment_entry.delete(0, 'end')

    def clear_name(self):
        self.name_entry.delete(0, 'end')

    def take_images(self):
        enrollment = self.enrollment_entry.get()
        name = self.name_entry.get()

        if not enrollment or not name:
            messagebox.showerror("Error", "Enrollment and Name fields cannot be empty.")
            return

        try:
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            
            sample_count = 0
            while True:
                ret, frame = cam.read()
                if not ret:
                    messagebox.showerror("Error", "Unable to access the camera.")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    sample_count += 1
                    cv2.imwrite(f"{TRAINING_IMAGE_PATH}/{name}.{enrollment}.{sample_count}.jpg", gray[y:y+h, x:x+w])
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                cv2.imshow("Capturing Images", frame)
                if cv2.waitKey(1) & 0xFF == ord('q') or sample_count >= 70:
                    break

            cam.release()
            cv2.destroyAllWindows()

            # Save student details
            with open(f"{STUDENT_DETAILS_PATH}/StudentDetails.csv", "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([enrollment, name, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

            messagebox.showinfo("Success", f"Images for {name} captured successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def train_images(self):
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

            faces, ids = self.get_images_and_labels(TRAINING_IMAGE_PATH)
            recognizer.train(faces, np.array(ids))
            
            os.makedirs(TRAINING_LABEL_PATH, exist_ok=True)
            recognizer.save(f"{TRAINING_LABEL_PATH}/Trainer.yml")
            
            messagebox.showinfo("Success", "Model trained successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_images_and_labels(self, path):
        image_paths = [os.path.join(path, f) for f in os.listdir(path)]
        face_samples, ids = [], []

        for image_path in image_paths:
            gray_image = Image.open(image_path).convert('L')
            np_image = np.array(gray_image, 'uint8')
            enrollment_id = int(os.path.split(image_path)[-1].split('.')[1])
            faces = cv2.CascadeClassifier('haarcascade_frontalface_default.xml').detectMultiScale(np_image)

            for (x, y, w, h) in faces:
                face_samples.append(np_image[y:y+h, x:x+w])
                ids.append(enrollment_id)

        return face_samples, ids

    def start_automatic_attendance(self):
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(f"{TRAINING_LABEL_PATH}/Trainer.yml")
            detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

            cam = cv2.VideoCapture(0)
            while True:
                ret, frame = cam.read()
                if not ret:
                    messagebox.showerror("Error", "Unable to access the camera.")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    id_, confidence = recognizer.predict(gray[y:y+h, x:x+w])

                    # Record attendance for the detected student
                    if confidence < 100:
                        enrollment, name = self.get_student_by_id(id_)
                        self.mark_attendance(enrollment, name)
                        cv2.putText(frame, f"Attendance marked for {name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                cv2.imshow("Automatic Attendance", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cam.release()
            cv2.destroyAllWindows()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_student_by_id(self, student_id):
        try:
            with open(f"{STUDENT_DETAILS_PATH}/StudentDetails.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if int(row[0]) == student_id:
                        return row[0], row[1]
        except FileNotFoundError:
            messagebox.showerror("Error", "Student details not found.")
            return None, None

    def mark_attendance(self, enrollment, name):
        try:
            with open(ATTENDANCE_FILE_PATH, "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([enrollment, name, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

            messagebox.showinfo("Success", f"Attendance marked for {name}")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def close_app(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()


def main():
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
