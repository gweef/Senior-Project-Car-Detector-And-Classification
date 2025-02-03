from tkinter import messagebox, filedialog
import os
import threading
from functools import partial
import pandas as pd
import pickle

#main programe
from src.class_for_project import Car
from ui.class_ui import AppUI
from src.main_system import main_system

# สถานะการยกเลิก (pass-by-reference)
cancel_flag = [False]  # ใช้ list เพื่อให้สามารถแก้ไขค่าได้ใน Thread

def on_start(app_ui:AppUI):
    selected_types, selected_colors = AppUI.get_selected_types_and_colors(app_ui)
    if app_ui.video_path.get():
        messagebox.showinfo("Start", f"Video Path: {app_ui.video_path.get()}\nTypes: {selected_types}\nColors: {selected_colors}")

        app_ui.hide_all_ui()

        # แสดง UI ใหม่
        app_ui.showimage_Frame.place(x=380, y=20, width=400, height=305)
        app_ui.waiting_frame.place(x=20, y=20, width=350, height=640)
        app_ui.start_detial_frame.place(x=40, y=150, width=310, height=200)
        app_ui.log_frame.place(x=40, y=360, width=310, height=270)
        app_ui.cancel_button.place(x=505, y=340, width=150, height=50)
        app_ui.progress_bar.start(10)
        
        app_ui.start_detial_label.set(f"Video Path: {app_ui.video_path.get()}\n \nTypes: {selected_types}\n \nColors: {selected_colors}")
        
        # ตัวอย่างการแสดงข้อความใน log_frame
        app_ui.log_message.set("Process started...")

        # เรียกฟังก์ชัน `testa` ผ่าน Thread
        start_thread(app_ui)
    else:
        messagebox.showwarning("Warning", "กรุณาเลือกไฟล์วิดีโอก่อนเริ่มโปรแกรม!")
        
# ฟังก์ชันสำหรับปุ่ม "Cancel"
def cancel_action(app_ui:AppUI):
    global cancel_flag
    cancel_flag[0] = True  # ตั้งสถานะการยกเลิก
    
    app_ui.hide_all_ui()
    app_ui.progress_bar.stop()
    
#แก้---------------------------------------------------
    app_ui.type_frame.place(x=20, y=20, width=350, height=260)
    app_ui.color_frame.place(x=20, y=300, width=350, height=360)
    app_ui.video_frame.place(x=380, y=20, width=400, height=260)
    app_ui.start_button.place(x=520, y=400, width=100, height=50)
#------------------------------------------------------------

    
# ฟังก์ชันสำหรับเปลี่ยน UI เป็นหน้า Complete
def complete_action(app_ui:AppUI):
    # ซ่อน UI การรอประมวลผล
    app_ui.progress_bar.stop()
    app_ui.hide_all_ui()

    app_ui.showimage_Frame.place(x=380, y=20, width=400, height=305)
    app_ui.complete_frame.place(x=20, y=20, width=350, height=640)
    app_ui.details_button.place(x=505, y=340, width=150, height=50)
    app_ui.export_button.place(x=505, y=440, width=150, height=50)
    app_ui.cancel_button.place(x=505, y=590, width=150, height=50)
    
def details_action(app_ui:AppUI):
    selected_types, selected_colors = AppUI.get_selected_types_and_colors(app_ui)
    app_ui.hide_all_ui()
    
    
    app_ui.start_detial_frame.place(x=20, y=20, width=350, height=165)
    app_ui.start_detial_label.set(f"Video Path: {app_ui.video_path.get()}\n \nTypes: {selected_types}\n \nColors: {selected_colors}")
    data = [
        {"carID": car.id, "Time": car. timestamp, "Type": car.type, "Color": car.color}
        for car in app_ui.processing_result
    ]
    app_ui.populate_table(data)
    app_ui.data_table.place(x=20, y=185, width=350, height=485)  # แสดง frame ที่มี data_table
    
    app_ui.showimage_Frame.place(x=380, y=20, width=400, height=260)
    app_ui.dataimage_Frame.place(x=380, y=280, width=400, height=45)
    #APPUI.DATAIMAGE LOG MASSAGE
    app_ui.saveimage_button.place(x=505, y=340, width=150, height=50)
    app_ui.previousimage_button.place(x=380, y=340, width=75, height=50)
    app_ui.nextimage_button.place(x=705, y=340, width=75, height=50)
    
    app_ui.log_frame.place(x=380, y=490, width=400, height=50)
    app_ui.exportvar_button.place(x=380, y=550, width=150, height=50)
    app_ui.exportfullvar_button.place(x=550, y=550, width=150, height=50)
    app_ui.export_button.place(x=380, y=610, width=150, height=50)
    app_ui.exportfull_button.place(x=550, y=610, width=150, height=50)
    app_ui.reset_button.place(x=720, y=640, width=70, height=30)   
    
# ฟังก์ชันเปิดไฟล์วิดีโอ
def open_video_file(video_path, video_frame):
    file_path = filedialog.askopenfilename(
        title="เลือกไฟล์วิดีโอ",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
    )
    if file_path:
        video_path.set(file_path)
        file_name = os.path.basename(file_path)
        video_frame.config(text=f"📁 {file_name[:20]}...")
    else:
        video_frame.config(text="เลือกวิดีโอ")


def start_thread(app_ui:AppUI):
    selected_types, selected_colors = AppUI.get_selected_types_and_colors(app_ui)
    global cancel_flag
    cancel_flag[0] = False
    thread = threading.Thread(
        target=lambda: main_system(
            app_ui.video_path.get(),
            selected_types,
            selected_colors,
            cancel_flag,
            app_ui.log_message.set,
            partial(process_result_callback, app_ui)
        )
    )
    thread.start()
    
    
def process_result_callback(app_ui:AppUI, result,full_result):
    app_ui.processing_result= result  # เก็บผลลัพธ์
    app_ui.processing_fullresult = full_result

    # หยุด ProgressBar
    app_ui.progress_bar.stop()

    # คืน UI เดิมและแสดงผลลัพธ์
    complete_action(app_ui)
    messagebox.showinfo("Complete", "Processing complete!")
    
def export_action(app_ui:AppUI,full):
    """
    เซฟข้อมูลจากออบเจ็กต์ของ Car เป็นไฟล์ Excel หรือ CSV
    :param app_ui: Instance ของ UI (สำหรับการแจ้งเตือน)
    :param car_objects: List ของออบเจ็กต์ Car
    """
    # แปลงข้อมูลจากออบเจ็กต์ Car เป็น List ของ Dictionary
    savetable = app_ui.processing_result
    if full : savetable = app_ui.processing_fullresult
    data = [
        {
            "ID": car.id,
            "Frame": car.frame,
            "Time (Second)": car.time_second,
            "Timestamp": car.timestamp,
            "Type": car.type,
            "Color": car.color,
            "H": car.h,
            "S": car.s,
            "V": car.v,
            "X1": car.x1,
            "Y1": car.y1,
            "X2": car.x2,
            "Y2": car.y2,
            "Confidence": car.confidence,
        }
        for car in savetable
    ]

    # สร้าง DataFrame
    df = pd.DataFrame(data)

    # เปิดหน้าต่างให้ผู้ใช้เลือกตำแหน่งไฟล์ที่ต้องการบันทึก
    file_path = filedialog.asksaveasfilename(
        title="Save as",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
    )

    if file_path:
        # ตรวจสอบนามสกุลไฟล์
        if file_path.endswith(".xlsx"):
            df.to_excel(file_path, index=False)  # บันทึกเป็น Excel
        elif file_path.endswith(".csv"):
            df.to_csv(file_path, index=False)  # บันทึกเป็น CSV
        else:
            app_ui.log_message.set("Unsupported file format!")
            return

        # แจ้งเตือนเมื่อบันทึกสำเร็จ
        app_ui.log_message.set(f"File saved successfully(table)")
        messagebox.showinfo("Success", f"File saved successfully at:\n{file_path}")
    else:
        app_ui.log_message.set("File save canceled!")
        
        
def exportvar_action(app_ui:AppUI,full):
    """
    เซฟ app_ui.processing_result ในรูปของไฟล์ .pkl
    """
    savedata = app_ui.processing_result
    if full : savedata = app_ui.processing_fullresult
    
    
    if not savedata:
        messagebox.showwarning("Warning", "No data to save! Processing result is empty.")
        return

    # เปิดหน้าต่างให้ผู้ใช้เลือกตำแหน่งและชื่อไฟล์
    file_path = filedialog.asksaveasfilename(
        title="Save Processing Result",
        defaultextension=".pkl",
        filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
    )

    if file_path:
        try:
            # บันทึกข้อมูล processing_result ลงในไฟล์ .pkl
            with open(file_path, "wb") as file:
                pickle.dump(savedata, file)
            messagebox.showinfo("Success", f"File saved successfully at:\n{file_path}")
            app_ui.log_message.set("File saved successfully(.plk)")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file:\n{e}")
    else:
        messagebox.showinfo("Canceled", "Save operation was canceled.")
     
def resetcall(app_ui:AppUI):
    call = messagebox.askquestion("Reset Programe","When you press reset program, all results will be deleted.")
    if call == 'yes' : 
        reset_action(app_ui)
        
def reset_action(app_ui:AppUI):
    app_ui.hide_all_ui()
    
    app_ui.processing_result = None
    app_ui.processing_fullresult = None
        
    app_ui.type_frame.place(x=20, y=20, width=350, height=260)
    app_ui.color_frame.place(x=20, y=300, width=350, height=360)
    app_ui.video_frame.place(x=380, y=20, width=400, height=305)
    app_ui.start_button.place(x=505, y=340, width=150, height=50)
    


