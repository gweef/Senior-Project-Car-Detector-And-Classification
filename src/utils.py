import cv2
import json
from dataclasses import asdict
import datetime
import pickle
import os
import pandas as pd
from tkinter import messagebox, filedialog

# ฟังก์ชันสำหรับแปลงวิดีโอเป็นเฟรมโดยเก็บในหน่วยความจำ
def video_to_frames(video_path, fps_out):
    """
    ลดเฟรมเรทของวิดีโอให้เหลือ fps_out และคืนค่ารายการของเฟรมที่เลือก
    :param video_path: เส้นทางไฟล์วิดีโอที่นำเข้า
    :param fps_out: เฟรมเรทที่ต้องการ (เฟรมต่อวินาที)
    :return: list_of_frames (รายการที่เก็บเฟรมแต่ละเฟรม)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise FileNotFoundError(f"ไม่สามารถเปิดไฟล์วิดีโอ: {video_path}")
    
    # อ่านข้อมูลเฟรมเรตเดิมของวิดีโอ
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(original_fps / fps_out)  # คำนวณจำนวนเฟรมที่ต้องข้าม
    
    frames  = []
    times = []
    timestamps = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        time = frame_count / frame_interval
        if not ret:
            break
        
        # เลือกเฉพาะเฟรมตาม frame_interval
        if frame_count % frame_interval == 0:
            # คำนวณตำแหน่งเวลาในรูปแบบ mm:ss.ss
            time = frame_count / original_fps
            minutes = int(time // 60)
            seconds = time % 60
            if seconds < 10:
                timestamp = f"{minutes:02}:0{seconds:04.2f}"
            else:
                timestamp = f"{minutes:02}:{seconds:05.2f}"
            frames.append(frame)
            times.append(float(f"{time:.2f}"))
            timestamps.append(timestamp)
        frame_count += 1

    cap.release()
    return frames,times,timestamps


def classToJson(cars) :
    # แปลงข้อมูลเป็น JSON
    cars_dict = [asdict(Car) for Car in cars]  # แปลงแต่ละ Car เป็น dict
    json_data = json.dumps(cars_dict, indent=4)  # แปลง dict เป็น JSON
    # retrun JSON
    return json_data
    
def filter_car(cars, type_filter, color_filter):
    """
    ฟิลเตอร์รถตาม type และ color ที่กำหนด

    Parameters:
        cars (list): รายการของ Car objects
        type_filter (list): รายการประเภทของรถที่ต้องการกรอง
        color_filter (list): รายการสีของรถที่ต้องการกรอง

    Returns:
        list: รายการของ Car objects ที่ผ่านการกรอง
    """
    # กรองเฉพาะรถที่ type และ color ตรงกับ filter
    cars_filtered = [
        car for car in cars 
        if str(car.type).lower() in [t.lower() for t in type_filter] and car.color.lower() in [c.lower() for c in color_filter]
    ]
    return cars_filtered


def saveVariable(variable,file_path) :
    video_name = os.path.splitext(os.path.basename(file_path))[0]
    save_dir = os.path.join(os.path.dirname(__file__), "../results")
    save_file_name = os.path.join(save_dir, f"{video_name}_var_{getTimeToSave()}.pkl")
    # ตรวจสอบว่ามีโฟลเดอร์ results หรือไม่ ถ้าไม่มีให้สร้าง
    os.makedirs(save_dir, exist_ok=True)
    # บันทึกตัวแปรลงไฟล์ด้วย pickle
    with open(save_file_name, 'wb') as file:
        pickle.dump(variable, file)
    
    print(f"save complete: {save_file_name}")
    
    return save_file_name

def loadVariable(file_path) :
        try:
            # เปิดไฟล์ในโหมด binary (อ่าน)
            with open(file_path, 'rb') as file:
                variable = pickle.load(file)
            print(f"load complete: {file_path}")
            return variable
        except FileNotFoundError:
            print(f"not found: {file_path}")
        except pickle.UnpicklingError:
            print(f"error: {file_path}")

def getTimeToSave():
    time = datetime.datetime.now()
    return f"{time.day}-{time.month}-{time.year}_{time.hour}-{time.minute}"