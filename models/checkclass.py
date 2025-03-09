import torch
from ultralytics import YOLO

# โหลดโมเดล YOLOv8n
model_path = "D:/SeniorProject/(1)main/project/Senior-Project-Car-Detector-And-Classification/models/yolov8n.pt"
model = torch.load(model_path, map_location="cpu")

# ดึงคลาสที่ใช้เทรน (สำหรับ YOLOv5 และ YOLOv8)
if "names" in model:
    class_names = model["names"]  # YOLOv5
elif "model" in model and hasattr(model["model"], "names"):
    class_names = model["model"].names  # YOLOv8
else:
    raise ValueError("ไม่พบข้อมูล class names ในโมเดล")

# แสดงรายการคลาสทั้งหมด
print("Class names:", class_names)

