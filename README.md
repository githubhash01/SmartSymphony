# Robotic Piano Accompaniment System

> **📌 Note:** This project was originally developed as a **group project** as part of the **System Design Project** at **Edinburgh University**.  
> The original repository can be found at: [(https://github.com/lukenoonen/SmartSymphonyHardware.git)]  
> This repository highlights my **individual contributions** to the project.

## Overview
This group project was developed as part of the **System Design Project** at University of Edinburgh The aim was to design and implement a robotic system that assists new piano learners by providing real-time accompaniment, visual guidance, and feedback.

The system integrates multiple hardware components and software functionalities to create an interactive learning experience. It includes a robotic piano that plays an octave to accompany learners, an LED strip for note guidance, and a microphone to provide feedback based on the learner's performance. Additionally, a web app allows users to upload sheet music, which is processed into hardware instructions to drive the robotic system.

---

## Features
### 1. **Robotic Accompaniment**
   - A robotic actuator system plays a single octave of the piano.
   - Accompanies learners by playing the correct notes at the right time.

### 2. **Visual Note Guidance**
   - An LED strip placed above the keyboard lights up the next note for the learner to play.
   - Adjusts in real-time based on the learner's progress.

### 3. **Performance Feedback**
   - A microphone detects notes played by the learner.
   - The system adapts the level of assistance based on detected accuracy.

### 4. **Web App Integration**
   - Users can upload sheet music in MIDI format via a web application.
   - The MIDI file is processed into hardware instructions for the actuators and LED strip.

---

## Technologies Used
- **Programming Language**: Python
- **Hardware**:
  - Actuators for robotic accompaniment
  - LED strip for note guidance
  - Microphone for performance detection
- **Software**:
  - MIDI file processing for hardware instructions
  - Controller for orchestrating system components
  - Web application for user interaction (sheet music uploads)

---

## My Contributions
I played a pivotal role in developing the software and hardware integration for this project. My key contributions include:

1. **MIDI File Processor**:
   - Wrote Python code to convert MIDI files into actionable hardware instructions.
   - Parsed musical data to synchronize robotic accompaniment with LED guidance.

2. **LED Strip Controller**:
   - Developed the code to control the LED strip, highlighting the next note to play.
   - Integrated the LED strip's behavior with the MIDI processor and microphone feedback.

3. **Hardware Wiring and Integration**:
   - Wired and tested actuators for the robotic accompaniment.
   - Ensured seamless communication between hardware components.

4. **Controller Class**:
   - Designed and implemented a Python-based controller class to coordinate:
     - Actuator instructions.
     - LED strip signals.
     - Microphone feedback for adaptive learning modes.

---

## How It Works
1. **User Uploads MIDI File**:
   - Sheet music and its associated MIDI file are uploaded via the web app.

2. **MIDI Processing**:
   - The MIDI file is parsed into hardware instructions for:
     - Actuators (robotic accompaniment).
     - LED strip (visual guidance).

3. **Learning Assistance**:
   - The system provides varying levels of assistance:
     - Full accompaniment and LED guidance for beginners.
     - Reduced assistance as the learner improves, based on microphone feedback.

4. **Real-Time Adaptation**:
   - The microphone detects played notes and adjusts the system's behavior accordingly.

---
