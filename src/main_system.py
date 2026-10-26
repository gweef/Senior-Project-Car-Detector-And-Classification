import src.utils as utils
import src.color_manage as color_manage
import src.detector  as detector 
from src.class_for_project import Car


import cv2
import json
import numpy as np
from dataclasses import asdict
import matplotlib.pyplot as plt



def main_system(video_path,selected_types, selected_colors,cancel_flag, log_callback, result_callback):
    ##input(1)
    #video_path = "D:/SeniorProject/(1)main/project/data/sideview03_10s.mp4"  # พาธของไฟล์วิดีโอ
    angle = 0 #มุมข้าง
    fps_out = 3  # 1 เฟรม ต่อ 1 วินาที (for test)
    log_callback("Processing...")
    
    utils.delete_clash() #ลบรูปจากรอบก่อน

    try:
        # ดึงเฟรมจากวิดีโอ
        frames,times,timestemps = utils.video_to_frames(video_path, fps_out,cancel_flag)
        if cancel_flag[0]:  # ตรวจสอบสถานะการยกเลิก
            log_callback("Process canceled.")
            return
        print(f"complete {len(frames)} frame \n")
        log_callback(f"Total Frame {len(frames)} ")

    except Exception as e:
        print(f"error: {e}")
        
        
    cars = []
    car_id = 1
    try:
        for i in range(len(frames)) :
            log_callback(f"Video : {timestemps[i]} / {timestemps[len(frames)-1]} \n\nProcessing {i+1} / {len(frames)} Frame \n\nDetect - / - Car")
            car_croped,car_type,conf = detector.car_detector(frames[i])
            frame_id = i+1
            
            for j in range(len(car_croped)):
                if cancel_flag[0]:  # ตรวจสอบสถานะการยกเลิก
                    log_callback("Process canceled.")
                    return
                log_callback(f"Video : {timestemps[i]} / {timestemps[len(frames)-1]} \n\nProcessing {i+1} / {len(frames)} Frame \n\nDetect {j+1} / {len(car_croped)} Car")
                interest_croped = detector.interest_point(car_croped[j],angle) ### เพิ่มเขียน try กรณีไมีเจอล้อด้วย ########################################
                print("complete interest point")
                if interest_croped is None or len(interest_croped) == 0:
                    color_name_classify,h,s,v = 'null',0,0,0
                elif isinstance(interest_croped, np.ndarray):
                    color_name_classify,h,s,v = color_manage.color_classifier(interest_croped)
                print(f"complete color {j+1} car")

                # สร้าง Car object
                car = Car(
                    id=car_id,
                    frame=frame_id,
                    time_second = times[i],
                    timestamp=timestemps[i],
                    type= car_type[j],
                    color= color_name_classify,
                    h=h,
                    s=s,
                    v=v,
                    confidence = conf[j],
                    #image = utils.manage_imageresults(car_id,interest_croped,color_name_classify)
                    image = utils.manage_imageresults(car_id,car_croped[j],color_name_classify,car_type[j])
                )
                cars.append(car)
                print(f"{car_id},{car_type[j]}")
                car_id = car_id + 1
                
                ## input valiable to class
                #frame = i +1 , car id = j +1 , time = frameId/Time
            
            print(f"complete detect {i+1} frame")
            
            
        cars_result = utils.filter_car(cars,selected_types,selected_colors) 
        result = cars_result   # เก็บผลลัพธ์ของการประมวลผล
        full_result = cars

        for i in range(1):  # จำลองการทำงาน
            if cancel_flag[0]:  # ตรวจสอบสถานะการยกเลิก
                log_callback("Process canceled.")
                return
        log_callback("Process completed.")
        result_callback(result,full_result) 
            
            
        '''
        tempFile = utils.saveVariable(cars,video_path)
        
        # แปลงข้อมูลเป็น JSON
        json_data = utils.classToJson(cars)
        # แสดงผล JSON
        print(json_data)
        
        '''
            

    except Exception as e:
        print(f"error: {e}")