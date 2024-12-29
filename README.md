
```markdown
# Attendance System

This project is an automated **Attendance System** that utilizes facial recognition technology to mark and manage attendance records efficiently.

## Features

- **Student Registration**: Capture and store student images for facial recognition.
- **Face Training**: Train the system to recognize registered student faces.
- **Automated Attendance**: Detect and recognize student faces to mark attendance automatically.
- **Attendance Records**: Maintain and export attendance logs in CSV format.

## Technologies Used

- **Programming Language**: Python
- **Libraries**:
  - OpenCV
  - Tkinter
  - Pandas
  - NumPy
- **Haar Cascade Classifier**: Used for face detection (`haarcascade_frontalface_default.xml`).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rupeshgs006/AttendenceSystem.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd AttendenceSystem
   ```
3. **Install the required dependencies**:
   ```bash
   pip install opencv-python-headless tk pandas numpy
   ```
4. **Run the main application**:
   ```bash
   python main_Run.py
   ```

## How to Use

1. **Register Students**:
   - Use the interface to capture multiple images of each student for accurate recognition.
   - Enter the student's ID and name during registration.

2. **Train the System**:
   - After registering students, run the training module to enable the system to recognize the registered faces.

3. **Mark Attendance**:
   - Start the attendance module; the system will detect faces in real-time and mark attendance for recognized students.

4. **View Attendance Records**:
   - Attendance records are saved in `Attendance.csv`.
   - Open this file to view or export attendance logs.

## Project Structure

```
AttendenceSystem/
├── Attendance/                   # Directory to store attendance records
├── StudentDetails/               # Directory to store student images
├── TrainingImageLabel/           # Directory for training data
├── attendance_system.py          # Core logic for attendance system
├── haarcascade_frontalface_default.xml  # Haar Cascade for face detection
├── main_Run.py                   # Main application script
└── Attendance.csv                # CSV file for attendance records
```

## Notes

- Ensure that your system has a functional camera for real-time face detection.
- The accuracy of face recognition improves with the number of images captured per student during registration.
- Regularly update the training data when new students are registered.

## Contributions

Contributions are welcome! Feel free to fork the repository and submit pull requests for improvements or bug fixes.


This README provides a comprehensive overview of your Attendance System project, guiding users on installation, usage, and contribution. 
