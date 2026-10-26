import cv2
import json
from dataclasses import asdict
import datetime
import pickle
import os
import pandas as pd
from tkinter import messagebox, filedialog
import numpy as np

from src.config import IMAGE_SHAPE
from src.class_for_project import Car

# ฟังก์ชันสำหรับแปลงวิดีโอเป็นเฟรมโดยเก็บในหน่วยความจำ
def video_to_frames(video_path, fps_out,cancel_flag):
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
    frame_interval = int(original_fps/fps_out)  # คำนวณจำนวนเฟรมที่ต้องข้าม
    
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
        if cancel_flag[0]:  # ตรวจสอบสถานะการยกเลิก
            cap.release()
            return

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
        if str(car.type).lower() in [str(t).lower() for t in type_filter] and str(car.color).lower() in [c.lower() for c in color_filter]
    ]
    return cars_filtered

def save_to_memmap(array: np.ndarray, file_path: str) -> str:
    """
    บันทึก np.ndarray ลงในไฟล์ .dat โดยใช้ np.memmap
    
    Parameters:
        array (np.ndarray): อาร์เรย์ที่ต้องการบันทึก
        file_path (str): พาธของไฟล์ .dat ที่จะบันทึก
    
    Returns:
        str: พาธของไฟล์ .dat ที่ถูกบันทึก
    """
    if array is None:
        raise ValueError("Input array is None. Cannot save to memmap.")

    shape = array.shape
    dtype = array.dtype

    # ตรวจสอบและสร้างไดเรกทอรีถ้ายังไม่มี
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # ใช้ memmap เพื่อเขียนข้อมูลลงไฟล์
    memmap_array = np.memmap(file_path, dtype=dtype, mode='w+', shape=shape)
    memmap_array[:] = array[:]
    memmap_array.flush()  # บันทึกข้อมูลลงดิสก์

    return file_path

def load_from_memmap(file_path: str, shape: tuple, dtype: np.dtype) -> np.memmap:
    """
    โหลดข้อมูลจากไฟล์ .dat เป็น np.memmap
    
    Parameters:
        file_path (str): พาธของไฟล์ .dat
        shape (tuple): รูปร่างของอาร์เรย์ที่บันทึก
        dtype (np.dtype): ประเภทของข้อมูลที่บันทึก
    
    Returns:
        np.memmap: อ็อบเจ็กต์ memmap ที่สามารถใช้งานได้เหมือน np.ndarray
    """
    return np.memmap(file_path, dtype=dtype, mode='r', shape=shape)


def manage_imageresults(id,image, color_results,car_type):
    if color_results == "null":
        return 0
    else :
        #จัดการการบันทึกภาพ
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        file_path = f"clash/{id}_{car_type}_{color_results}.dat"
        image_resized = resize_with_padding(image, target_size=IMAGE_SHAPE[:2])
        return save_to_memmap(image_resized, file_path)
    
    
def resize_with_padding(image, target_size):
    """
    ปรับขนาดภาพโดยรักษาอัตราส่วนเดิม และเติมขอบ (padding) เพื่อให้พอดีกับ target_size

    Parameters:
        image (np.ndarray): ภาพต้นฉบับ
        target_size (tuple): ขนาดเป้าหมาย (width, height)

    Returns:
        np.ndarray: ภาพที่ถูกปรับขนาดและเติมขอบ
    """
    original_height, original_width = image.shape[:2]
    target_width, target_height = target_size

    # คำนวณอัตราส่วนการย่อขนาด
    scale = min(target_width / original_width, target_height / original_height)

    # คำนวณขนาดใหม่ที่รักษาอัตราส่วนเดิม
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    # ย่อขนาดภาพ
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # คำนวณ padding ที่ต้องเติม
    top_pad = (target_height - new_height) // 2
    bottom_pad = target_height - new_height - top_pad
    left_pad = (target_width - new_width) // 2
    right_pad = target_width - new_width - left_pad

    # เติมขอบด้วยสีดำ (0) หรือสีขาว (255) ถ้าต้องการ
    padded_image = cv2.copyMakeBorder(resized_image, top_pad, bottom_pad, left_pad, right_pad,
                                      cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return padded_image

    
def delete_clash():
    folder_path = "clash"  # กำหนดโฟลเดอร์ที่ต้องการลบไฟล์

    # ตรวจสอบว่าโฟลเดอร์มีอยู่จริง
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):  # ตรวจสอบว่าเป็นไฟล์ ไม่ใช่โฟลเดอร์
                os.remove(file_path)
                print(f"ลบไฟล์: {file_path}")
    else:
        print("โฟลเดอร์ไม่มีอยู่")



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