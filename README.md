# AI-Based Smart Health Monitoring and Automatic Emergency Response System

## Overview

The Smart Health Monitoring System is an AI-based monitoring application designed to assist in detecting potentially unsafe situations using computer vision and emergency-response software.

The system combines person detection, pose estimation, fall detection, activity detection, emergency management, incident logging, and a Streamlit dashboard.

## Main Features

- Person detection using YOLO
- Human pose estimation using MediaPipe
- Fall detection using pose-based analysis
- Basic activity detection
- Emergency alert management
- Emergency event logging
- SQLite-based incident history
- Streamlit monitoring dashboard
- Webcam-based AI monitoring
- Future support for ESP32-based health sensors

## System Architecture

```text
Camera
   |
   +--> Person Detection
   |
   +--> Pose Detection
   |
   +--> Fall Detection
   |
   +--> Activity Detection
             |
             v
      Emergency Manager
             |
       +-----+------+
       |            |
       v            v
 Emergency Log   SQLite Database
       |            |
       +-----+------+
             |
             v
      Streamlit Dashboard