Smart Health Monitoring System

Overview

The Smart Health Monitoring System is an AI-based monitoring application designed to assist with basic health and safety monitoring using computer vision, pose estimation, voice interaction, and emergency event management.

The system combines multiple AI modules into a single monitoring application controlled through a main Python program.

Main Features

- 🎙️ Voice-based emergency checking
- 👤 AI-based human/person detection
- 🦴 Human pose estimation
- 🚨 Fall detection
- 📞 Emergency event management
- 📝 Emergency event logging
- 📊 Monitoring session logging
- 🖥️ Menu-based main controller

---

System Architecture

                    SMART HEALTH MONITORING
                              |
                              v
                       Main Controller
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
 Voice Assistant       Person Detection      Pose Estimation
        |                     |                     |
        +---------------------+---------------------+
                              |
                              v
                       Fall Detection
                              |
                              v
                      Emergency Manager
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          Emergency Log              Session Log

---

Project Modules

1. Voice Assistant

The voice assistant checks whether the user is okay.

The system:

1. Greets the user.
2. Asks whether the user is okay.
3. Captures the user's voice response.
4. Processes the response.
5. Identifies positive or emergency-related responses.
6. Sends possible emergency situations to the Emergency Manager.

Example:

ASSISTANT: Are you okay? Please say yes or no.
YOU: yes I am ok

STATUS: USER OKAY

---

2. Person Detection

The person detection module uses YOLO to identify humans in the camera frame.

The system displays the number of detected people.

Example:

Person detected - 1
Multiple people detected - 2
No person detected - 0

Only the YOLO "person" class is counted as a person.

---

3. Pose Estimation

The pose estimation module uses MediaPipe Pose to detect important human body landmarks.

The system can identify landmarks such as:

- Nose
- Shoulders
- Hips
- Knees
- Ankles

It also calculates an approximate body angle that can be used as an input for fall analysis.

---

4. Fall Detection

The fall detection module combines:

- YOLO person detection
- MediaPipe pose estimation
- Body position tracking
- Downward movement analysis
- Body angle analysis
- Fall confirmation timing
- Recovery detection

A possible fall is identified using movement and body orientation conditions.

The system uses a confirmation period to reduce immediate false alarms.

When a fall is confirmed, the event can be sent to the Emergency Manager.

---

5. Emergency Manager

The Emergency Manager acts as the central emergency event handler.

It receives emergency events from modules such as:

- Voice Assistant
- Fall Detection

Each event contains information such as:

Source
Reason
Status
Timestamp

Example:

SOURCE: FALL DETECTION
REASON: Fall detected by fall detection system
STATUS: POSSIBLE EMERGENCY DETECTED

---

Project Structure

The project is organized into separate modules for AI processing, pose estimation, emergency handling, and system control.

Main Folders

- ai/
  
  - "person_detection.py" — Detects people using YOLO.
  - "fall_detection.py" — Detects possible falls using computer vision and pose information.

- camera/
  
  - Contains camera-related components.

- emergency/
  
  - "voice_assistant.py" — Handles voice-based emergency checking.
  - "emergency_manager.py" — Processes and records emergency events.

- pose/
  
  - "pose_detection.py" — Performs human pose estimation using MediaPipe.

Main Files

- "main.py" — Main controller and menu system.
- "mic_test.py" — Microphone testing utility.
- "requirements.txt" — Python dependencies.
- "README.md" — Project documentation.
- ".gitignore" — Files excluded from Git tracking.

Local / Generated Files

The following files are intentionally excluded from GitHub:

- "venv/" — Python virtual environment.
- "logs/" — Local monitoring and emergency logs.
- "yolo11n.pt" — YOLO model file.
- "project_structure.txt" — Generated project structure reference.

These files are excluded using ".gitignore".

---

Technologies Used

Technology| Purpose
Python| Main programming language
OpenCV| Camera and image processing
YOLO| Human/person detection
MediaPipe| Human pose estimation
Speech Recognition| Voice input
Text-to-Speech| Voice responses
Git| Version control
GitHub| Source code repository

---

Installation

1. Clone the Repository

git clone https://github.com/harini-0604/SmartHealthMonitoring.git

2. Open the Project

cd SmartHealthMonitoring

3. Create a Virtual Environment

python -m venv venv

4. Activate the Virtual Environment

Windows PowerShell:

venv\Scripts\Activate.ps1

5. Install Dependencies

pip install -r requirements.txt

---

YOLO Model

The project uses a YOLO model for person detection.

The model file is intentionally excluded from GitHub because it is a large generated/model file.

Place the required YOLO model file in the project root before running the AI modules.

---

Running the System

Activate the virtual environment first:

venv\Scripts\Activate.ps1

Then run:

python main.py

The main menu provides options such as:

[1] Run Complete Monitoring
[2] Voice Emergency Check
[3] Fall Detection
[4] View Emergency Log
[5] Exit

---

Example Monitoring Session

SMART HEALTH MONITORING SYSTEM

Starting Voice Assistant...
STATUS: USER OKAY

Starting Person Detection...
Person detected - 1

Starting Pose Estimation...
Pose estimation stopped.

Starting Fall Detection...
Fall detection system started.

MONITORING SESSION SUMMARY

Voice Assistant : USER OKAY
Person Detection: Successful
Pose Estimation : Successful
Fall Detection  : Successful

---

Emergency Logging

Emergency events are recorded by the Emergency Manager.

The system can display previously recorded emergency events through the main menu.

Example:

EMERGENCY EVENT LOG

SOURCE: TEST
REASON: Emergency manager test
STATUS: POSSIBLE EMERGENCY DETECTED

Session activity is also recorded in the local "logs" directory.

---

Testing

The individual modules can be tested independently during development.

The complete system can be tested using:

python main.py

Recommended tests include:

- Voice response test
- Person detection test
- Pose estimation test
- Fall detection test
- Emergency Manager test
- Complete monitoring test
- Emergency log verification

---

Current Status

The following modules have been integrated and tested:

- ✅ Main Controller
- ✅ Voice Assistant
- ✅ Person Detection
- ✅ Pose Estimation
- ✅ Fall Detection
- ✅ Emergency Manager
- ✅ Emergency Logging
- ✅ Session Logging
- ✅ Git/GitHub version control

---

Limitations

This project is intended as an academic/prototype monitoring system and should not be considered a medical diagnostic or emergency response system.

Performance may depend on:

- Camera quality
- Lighting conditions
- Camera position
- Internet/audio configuration
- AI model performance
- Hardware capabilities

---

Future Improvements

Possible future improvements include:

- Real-time health sensor integration
- Heart-rate monitoring
- SpO₂ monitoring
- GPS/location support
- Improved fall detection accuracy
- Mobile application integration
- Cloud-based monitoring
- Real-time notifications
- Database-based health records
- Multi-person tracking
- Improved emergency communication

---

Author

Harini V

Project

Smart Health Monitoring System

Built as an AI-based health and safety monitoring project using Python and computer vision technologies.