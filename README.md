# AI-Based Smart Health Monitoring and Automatic Emergency Response System

## Overview

The **Smart Health Monitoring System** is an AI-based health and safety monitoring application designed to assist with detecting potentially unsafe situations and managing emergency-response workflows.

The system combines computer vision, voice interaction, health-sensor simulation, emergency verification, incident logging, SQLite storage, and a Streamlit dashboard into a single monitoring platform.

> **Note:** This project is a software demonstration and is not a medical diagnostic system or a replacement for professional medical care.

---

## Main Features

### AI-Based Monitoring

- Person detection using YOLO
- Human pose estimation using MediaPipe
- Pose-based fall detection
- Basic activity detection
- Webcam-based monitoring

### Emergency Response

- Voice-based emergency check
- Emergency verification after a detected incident
- Emergency event management
- Incident logging
- Emergency status tracking
- Hospital and ambulance interface modules
- Notification interface with optional Twilio integration

### Health Monitoring

- Heart-rate monitoring interface
- SpO2 monitoring interface
- Temperature monitoring interface
- Software-based sensor simulation
- ESP32 integration interface for future physical sensors
- Configurable demonstration health thresholds

### Dashboard

- Streamlit-based monitoring dashboard
- Person detection module
- Pose detection module
- Fall detection module
- Activity detection module
- Live camera monitoring
- Sensor status and simulated readings
- Health status display
- Emergency alerts
- Incident history

### Data Management

- SQLite-based incident storage
- Emergency event history
- Session logging
- Git-based project version control

---

## System Architecture

```text
                         SMART HEALTH MONITORING SYSTEM
                                      |
              +-----------------------+-----------------------+
              |                       |                       |
           Camera                Voice Input            Health Sensors
              |                       |                       |
      +-------+-------+                |              +--------+--------+
      |       |       |                |              |        |        |
   Person   Pose    Activity           |           Heart    SpO2   Temperature
 Detection Detection Detection         |             \       |       /
      |       |       |                |              +------+------+
      +-------+-------+                |                     |
              |                       |                Health Monitor
              |                       |                     |
              +------------+----------+---------------------+
                           |
                    Emergency Manager
                           |
                    Emergency Verification
                           |
              +------------+-------------+
              |            |             |
              v            v             v
        Emergency Log   Notification   External
                           Interface   Services
              |
              v
        SQLite Database
              |
              v
      Streamlit Dashboard
