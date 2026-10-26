# 🚗 Vehicle Type & Color Recognition System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-KMeans-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

An end-to-end computer vision desktop application designed to automatically detect, classify vehicle types, and extract vehicle colors from video streams. Built with a focus on **memory optimization**, **multi-stage AI pipelines**, and **advanced image processing**, this system is capable of handling long video footage without overwhelming system RAM.

## ✨ Key Strengths & Features

*   **🧠 Multi-Stage Detection Pipeline**: Instead of a simple single-pass detection, the system utilizes a complex pipeline. It first detects the vehicle, crops the bounding box, and then uses secondary custom-trained YOLOv8 models to detect specific sub-features (wheels for side-views, windshields for front-views) to calculate a precise Region of Interest (ROI).
*   **🎨 Advanced Color Extraction**: 
    *   Uses **LAB color space** analysis with Trimmed Mean and **CLAHE** (Contrast Limited Adaptive Histogram Equalization) to dynamically adjust underexposed or dark frames.
    *   Applies **Unsupervised Learning (K-Means Clustering)** in the HSV color space to filter out noise and extract the true dominant color of the vehicle body.
    *   Custom heuristic bins for separating achromatic colors (Black, White, Gray, Silver) from chromatic colors.
*   **⚡ Extreme Memory Optimization**: Integrates `numpy.memmap` to write and read tensor arrays (`.dat` files) directly to/from disk. This prevents Out-Of-Memory (OOM) errors when processing high-framerate or lengthy videos containing hundreds of vehicles.
*   **🖥️ Responsive Asynchronous GUI**: Built with Tkinter, featuring a multithreaded backend. The UI remains fully responsive during heavy model inference, providing real-time logs, progress bars, and data tables.
*   **📊 Comprehensive Data Export**: Filter and export results directly to `.xlsx` (Excel), `.csv`, or save the entire application state via `.pkl` (Pickle) to resume work later.

## 🎯 Project Scope

*   **Supported Vehicle Types**: Sedan, SUV, Pick-Up, Van, Bus, Truck, Motorcycle.
*   **Supported Colors**: Black, Gray, Silver, White, Red, Blue, Yellow, Green, Brown, Pink, Purple.
*   **Input Format**: Standard video files (`.mp4`, `.avi`, `.mov`, `.mkv`).
*   **View Angles**: Optimized for side-view (wheel-based ROI) and front-view (windshield-based ROI) camera angles.

## ⚙️ System Architecture

*   `main_system.py`: The core controller managing video frame extraction, object detection loops, and data aggregation.
*   `detector.py`: Handles model inferences using Ultralytics YOLOv8 (loaded on CUDA if available).
*   `color_manage.py`: Contains all image processing algorithms (Luminance adjustment, Gaussian Blurs, K-Means clustering, HSV classification).
*   `utils.py`: Helper functions for video processing, memory mapping, resizing with padding, and JSON/Pickle serialization.
*   `class_ui.py` & `component.py`: UI layout and event-driven logic handling multithreading and user interactions.

## 🚀 Installation & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/vehicle-recognition-system.git
   cd vehicle-recognition-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have PyTorch installed with CUDA support for optimal inference speed).*

3. **Add Models**:
   Place your custom-trained YOLOv8 models (`yolov8l.pt`, `best_cartype_V1.pt`, `wheel_detectoerV2.pt`, `best_windshield_V1.pt`) into the `models/` directory.

4. **Run the application**:
   ```bash
   python main.py
   ```
   *(Assuming `main.py` is your entry point that calls `main_ui()`)*

## ⚠️ Limitations
*   Detection accuracy is dependent on the quality of the input video (e.g., severe motion blur or extreme low-light conditions without minimum luminance may affect color clustering).
*   Color classification relies on the targeted ROI; if the wheel/windshield detection fails, the system falls back to a null state for that specific vehicle to prevent false color logging.

## 👨‍💻 Author
**[Your Name/Username]** - *Computer Engineering Graduate / AI Developer*