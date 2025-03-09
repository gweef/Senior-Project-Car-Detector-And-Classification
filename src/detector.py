import os
import numpy as np
import cv2 as cv

from ultralytics import YOLO

from src.color_manage import luminance_edit


# หาตำแหน่งโฟลเดอร์ปัจจุบันที่ไฟล์ detector.py อยู่
current_dir = os.path.dirname(os.path.abspath(__file__))
# สร้างพาร์ทที่สัมพันธ์กับโฟลเดอร์ models
car_model_path = os.path.join(current_dir, '..', 'models', 'yolov8l.pt')
cartype_model_path = os.path.join(current_dir, '..', 'models', 'best_cartype_V1.pt')
wheel_model_path = os.path.join(current_dir, '..', 'models', 'wheel_detectoerV2.pt')
windshield_model_path = os.path.join(current_dir, '..', 'models', 'best_windshield_V1.pt')

# โหลดโมเดล YOLOv8 สำหรับตรวจจับรถ
car_model = YOLO(car_model_path)
car_model.to('cuda')
coco_classes = car_model.names

# โหลดโมเดล YOLOv8 สำหรับตรวจจับล้อรถ
wheel_model = YOLO(wheel_model_path)
wheel_model.to('cuda')

# โหลดโมเดล YOLOv8 สำหรับตรวจกระจกหน้ารถ
windshield_model = YOLO(windshield_model_path)
windshield_model.to('cuda')

cartype_model = YOLO(cartype_model_path)
cartype_model.to('cuda')

import numpy as np

def wheel_detector(image):
    wheel_results = wheel_model(image)
    wheels = []
    
    for wheel_result in wheel_results:
        for wheel_box in wheel_result.boxes:
            wx1, wy1, wx2, wy2 = map(int, wheel_box.xyxy[0])
            w_confidence = wheel_box.conf[0]
            if w_confidence > 0.5:
                wheels.append((wx1, wy1, wx2, wy2))
    
    if len(wheels) >= 2:
        # จัดเรียงล้อจากซ้ายไปขวา
        wheels.sort(key=lambda w: w[0])
        
        # เลือกล้อที่อยู่ซ้ายสุดเป็นล้อหน้า และขวาสุดเป็นล้อหลัง
        front_wheel = wheels[0]
        rear_wheel = wheels[-1]
        
        # คำนวณขอบเขตระหว่างล้อ
        roi_x1 = front_wheel[2]  # ขอบขวาของล้อหน้า
        roi_x2 = rear_wheel[0]    # ขอบซ้ายของล้อหลัง
        roi_y1 = min(front_wheel[1], rear_wheel[1])  # จุดบนสุดของล้อที่ต่ำที่สุด
        roi_y2 = max(front_wheel[3], rear_wheel[3])  # จุดล่างสุดของล้อที่สูงที่สุด

        # ป้องกันกรณีที่ x1 > x2 หรือ y1 > y2
        roi_x1, roi_x2 = sorted([roi_x1, roi_x2])
        roi_y1, roi_y2 = sorted([roi_y1, roi_y2])

        # ขยายขอบเขตแนวตั้งให้ครอบคลุมพื้นที่ตัวรถ
        roi_y1 = max(0, roi_y1 - int(0.4 * (roi_y2 - roi_y1)))  # ขยายขึ้นบน 30%
        roi_y2 = min(image.shape[0], roi_y2 - int(0.2 * (roi_y2 - roi_y1)))  # ลดลงล่าง 20%

        # ตรวจสอบว่า ROI ไม่ว่าง
        if roi_x2 > roi_x1 and roi_y2 > roi_y1:
            wheel_croped = image[roi_y1:roi_y2, roi_x1:roi_x2]
            print(f"roi_y1: {roi_y1}, roi_y2: {roi_y2}, roi_x1: {roi_x1}, roi_x2: {roi_x2}, shape: {wheel_croped.shape}")
        else:
            print("Error: Invalid ROI dimensions")
            wheel_croped = None
    else:
        print("Error: Not enough wheels detected")
        wheel_croped = None  # คืนค่า None ถ้าพบล้อไม่ครบ 2 ล้อ
    
    return wheel_croped if isinstance(wheel_croped, np.ndarray) and wheel_croped.size > 0 else None


def windshield_detector(image):
    #windshield_croped = np.zeros((30,30))
    """
    Detects the windshield of a car, crops the hood area, and returns the cropped image.
    
    Parameters:
        image (numpy.ndarray): Input image (cropped car image).
        windshield_model_path (str): Path to the YOLO model for detecting the windshield.
    
    Returns:
        numpy.ndarray: Cropped hood image.
    """
    
    # Detect objects using YOLO
    results = windshield_model.predict(image)
    
    # Assume the windshield is the first detected object (adjust as needed)
    if len(results[0].boxes) > 0:
        # Extract bounding box coordinates of the windshield
        box = results[0].boxes[0].xyxy[0].cpu().numpy()  # (x_min, y_min, x_max, y_max)
        x_min, y_min, x_max, y_max = map(int, box)
        
        # Crop the windshield area
        windshield_width = x_max - x_min
        windshield_height = y_max - y_min
        
        # Define the hood area below the windshield
        hood_height = int(windshield_height * 0.55)
        hood_y_min = y_max
        hood_y_max = y_max + hood_height
        
        # Ensure the hood area is within image bounds
        hood_y_max = min(hood_y_max, image.shape[0])
        
        # Crop the hood area
        hood_image = image[hood_y_min:hood_y_max, x_min:x_max]
        
        return hood_image
    else:
        raise ValueError("No windshield detected in the image.")

def car_detector(frame):
    cars_croped = []
    x1s,x2s,y1s,y2s = [],[],[],[]
    cars_type = []
    confs = []
    
    # แปลงภาพจาก BGRA เป็น BGR (หรือ RGB)
    frame = luminance_edit(frame)
    frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
    # ตรวจจับรถ
    car_results = car_model(frame)
    
    # คร็อปรถทุกคันในภาพ
    for car_result in car_results[0].boxes.data.tolist():
        x1, y1, x2, y2, conf, class_id = car_result
        
        ## 2: 'car' 3: 'motorcycle' 5: 'bus' 7: 'truck'
        if class_id in {2, 3, 5, 7} and conf > 0.4: # class_id 2 = Car, 7 = Truck ใน COCO Dataset
            # คร็อปรถออกจากภาพ
            car_croped = frame[int(y1):int(y2), int(x1):int(x2)]
            # เพิ่มภาพที่คร็อปลงในรายการ
            cars_croped.append(car_croped)
            print(f"{coco_classes[class_id]}")
            car_type = classifytype(car_croped,coco_classes[class_id])
            #เพิ่มตำแหน่งของรถ
            x1s.append(x1)
            x2s.append(x2)
            y1s.append(y1)
            y2s.append(y2)
            cars_type.append(car_type)
            confs.append(conf*100)
            
    '''
    cars_croped = [np.zeros((10,10)), np.zeros((10,10)), np.zeros((10,10))]
    x1,x2,y1,y2 = [15,12,13],[15,12,13],[15,12,13],[15,12,13]
    cars_type = ['car','truck','van']
    confs = [50,70,80]
    '''
    return  cars_croped,cars_type,confs

def interest_point(image,angle):
     #Sideview
    if not angle :
        interest_croped = wheel_detector(image)
    #Forntview
    else :
        interest_croped = windshield_detector(image)
        
    return interest_croped

def classifytype(car_image,baseType):
    if baseType == "motorcycle":
        type_result = "Motorcycle"
        return type_result
    elif baseType == "bus" :
        type_result = "Bus"
        return type_result
    elif baseType == "car" or baseType == "truck" :
        cartype_results = cartype_model(car_image)
        cartype_dict = cartype_results[0].names
        cartype_probs = cartype_results[0].probs.data.tolist()
        type_result = cartype_dict[np.argmax(cartype_probs)]
        print(f"Type : {type_result}")
        type_result = definetype(type_result)
        print(f"Type_2 : {type_result}") 
        return type_result


def definetype(type:str) -> str:
    #Convertible ,Coupe	,Hatchback ,Pick-Up ,SUV ,Sedan	,Truck ,VAN
    # to ["Sedan", "SUV", "Pickup", "Van", "Bus", "Truck", "Motorcycle"]  
    if type in ["Sedan", "Convertible", "Coupe", "Hatchback"]:
        return "Sedan"
    else:
        return type