# Smart Health Monitoring System

## Overview

Smart Health Monitoring System is an AI-based monitoring application designed to assist with basic health and safety monitoring using computer vision and voice interaction.

The system combines:

- Voice-based emergency checking
- AI person detection
- Human pose estimation
- Fall detection
- Emergency event management
- Emergency logging
- Monitoring session logging

---

## System Architecture

```text
                    SMART HEALTH MONITORING
                              |
                              v
                         Main Controller
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
       Voice Assistant   Person Detection   Pose Estimation
             |                |                |
             +----------------+----------------+
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