from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import threading
from functools import partial
import pandas as pd
import pickle
import numpy as np
import re

#main programe
from src.class_for_project import Car
from src.config import IMAGE_SHAPE
from ui.class_ui import AppUI
from src.main_system import main_system
from src.utils import delete_clash

# สถานะการยกเลิก (pass-by-reference)
cancel_flag = [False]  # ใช้ list เพื่อให้สามารถแก้ไขค่าได้ใน Thread

def on_start(app_ui:AppUI):
    selected_types, selected_colors = AppUI.get_selected_types_and_colors(app_ui)
    if app_ui.video_path.get():
        messagebox.showinfo("Start", f"Video Path: {app_ui.video_path.get()}\nTypes: {selected_types}\nColors: {selected_colors}")

        app_ui.hide_all_ui()

        # แสดง UI ใหม่
        app_ui.waitingimage_Frame.place(x=380, y=20, width=400, height=305)
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
    
    # ล้างค่าทั้งหมด
    app_ui.processing_result = None
    app_ui.processing_fullresult = None
    
    app_ui.hide_all_ui()
    app_ui.progress_bar.stop()
    
    app_ui.type_frame.place(x=20, y=20, width=350, height=260)
    app_ui.color_frame.place(x=20, y=300, width=350, height=360)
    app_ui.video_frame.place(x=380, y=20, width=400, height=305)
    app_ui.start_button.place(x=505, y=340, width=150, height=50)
    app_ui.loadfile_button.place(x=505, y=440, width=150, height=50)

    
# ฟังก์ชันสำหรับเปลี่ยน UI เป็นหน้า Complete
def complete_action(app_ui:AppUI):
    # ซ่อน UI การรอประมวลผล
    app_ui.progress_bar.stop()
    app_ui.hide_all_ui()
    
    app_ui.load_image(app_ui.image_file_list[app_ui.current_index])

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
        {"carID": car.id, "Time": car.timestamp, "Type": car.type, "Color": car.color}
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
    
    app_ui.load_image(app_ui.image_file_list[app_ui.current_index])
    
    app_ui.dropdown["values"] = app_ui.image_file_list
    app_ui.selected_file.set(app_ui.image_file_list[app_ui.current_index])
    
    app_ui.image_file_list = sorted(
        [f for f in os.listdir('clash') if f.endswith(".dat")], 
        key=extract_number
    )
    
    app_ui.log_frame.place(x=380, y=490, width=400, height=50)
    app_ui.exportvar_button.place(x=380, y=550, width=150, height=50)
    app_ui.export_button.place(x=380, y=610, width=150, height=50)
    app_ui.exportfull_button.place(x=550, y=610, width=150, height=50)
    app_ui.reset_button.place(x=720, y=640, width=70, height=30)
    
def extract_number(filename):
    """ ดึงตัวเลขจากชื่อไฟล์ เช่น 'data_10.dat' → 10 """
    match = re.search(r'\d+', filename)  # ค้นหาตัวเลขในชื่อไฟล์
    return int(match.group()) if match else float('inf')  # คืนค่าเป็น int ถ้าพบเลข   
    
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
    
    #ริสไฟล์.dat ที่อยู่ในโฟลเดอร์ clash
    app_ui.image_file_list = [f for f in os.listdir("clash") if f.endswith(".dat")]

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
    Save app_ui.processing_result in the form of a .pkl file.
    The .dat files are now expected to be created using np.memmap.
    """
    video_path = app_ui.video_path.get()
    selected_types = [var.get() for var in app_ui.type_vars]
    selected_colors = [var.get() for var in app_ui.color_vars]
    result = app_ui.processing_result
    full_result = app_ui.processing_fullresult
    
    clash = "clash"  # Folder that contains the .dat files
    
    dat_files = {}

    # Read all .dat files in the folder
    for filename in os.listdir(clash):
        if filename.endswith(".dat"):
            file_path = os.path.join(clash, filename)
            try:
                # Using np.memmap to read the .dat file
                data = np.memmap(file_path, dtype='float32', mode='r')  # Adjust dtype based on your file content
                dat_files[filename] = data
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to read {filename}: {e}")
                
    # Combine all data
    combined_data = {
        "video_path": video_path,
        "selected_types": selected_types,
        "selected_colors": selected_colors,
        "result": result,
        "full_result": full_result,
        "dat_files": dat_files
    }

    if not full_result:
        messagebox.showwarning("Warning", "No data to save! Processing result is empty.")
        return

    # Open a dialog to allow the user to choose a location and filename for saving
    file_path = filedialog.asksaveasfilename(
        title="Save Processing Result",
        defaultextension=".pkl",
        filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
    )

    if file_path:
        try:
            # Save the processing_result data to a .pkl file
            with open(file_path, "wb") as file:
                pickle.dump(combined_data, file)
            messagebox.showinfo("Success", f"File saved successfully at:\n{file_path}")
            app_ui.log_message.set("File saved successfully(.pkl)")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file:\n{e}")
    else:
        messagebox.showinfo("Canceled", "Save operation was canceled.")
        
def loadfile_action(app_ui:AppUI):
    """
    โหลดข้อมูลจากไฟล์ .pkl และแสดงผลลัพธ์
    """
    delete_clash()
    video_path,selected_types,selected_colors,result,full_result = load_from_plk()
    
    if video_path == None:
        return
    
    app_ui.video_path.set(video_path)
    
    # ล้างค่าทั้งหมด
    for var in app_ui.type_vars:
        var.set(False)
    for var in app_ui.color_vars:
        var.set(False)
        
    # ตั้งค่าคืนค่าให้ type_vars
    for var, value in zip(app_ui.type_vars, selected_types):
        var.set(value)
    # ตั้งค่าคืนค่าให้ color_vars
    for var, value in zip(app_ui.color_vars, selected_colors):
        var.set(value)
    if result:
        process_result_callback(app_ui,result,full_result)
        app_ui.log_message.set(f"File loaded successfully!")
        
def load_from_plk():
    """
    โหลดข้อมูลจากไฟล์ .plk ผ่านหน้าต่างเลือกไฟล์ และบันทึกไฟล์ .bat ทั้งหมดลงในโฟลเดอร์ clash
    """
    file_path = filedialog.askopenfilename(
        title="Load Processing Result",
        filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
    )
    
    if not file_path:
        messagebox.showinfo("Canceled", "Load operation was canceled.")
        return None, None, None, None, None
    
    try:
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        # ดึงข้อมูล
        video_path = data.get("video_path")
        selected_types = data.get("selected_types")
        selected_colors = data.get("selected_colors")
        result = data.get("result")
        full_result = data.get("full_result")
        dat_files = data.get("dat_files", {})
        
        # สร้างโฟลเดอร์ clash ถ้ายังไม่มี
        clash_folder = "clash"
        os.makedirs(clash_folder, exist_ok=True)
        
        # บันทึกไฟล์ .dat ทั้งหมดลงในโฟลเดอร์ clash
        for filename, content in dat_files.items():
            file_path = os.path.join(clash_folder, filename)
            try:
                # ใช้ np.memmap เพื่อสร้างไฟล์ .dat
                memmap_data = np.memmap(file_path, dtype='float32', mode='w+', shape=content.shape)
                memmap_data[:] = content[:]  # คัดลอกข้อมูลจาก content ไปยัง memmap
            except Exception as e:
                messagebox.showwarning("Warning", f"can't save flie : {filename}: {e}")
        
        messagebox.showinfo("Success", f"File loaded successfully from:\n{file_path}\n.dat files saved to clash folder.")
        
        return video_path,selected_types,selected_colors,result, full_result
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the file:\n{e}")
        return None , None, None, None, None
        
def save_image_action(app_ui:AppUI):
    """
    บันทึกภาพจากไฟล์ .dat ที่เลือกเป็นไฟล์ภาพ (PNG, JPEG)
    """
    filename = app_ui.image_file_list[app_ui.current_index]
    filepath = os.path.join("clash", filename)
    memmap_array = np.memmap(filepath, dtype=np.uint8, mode='r', shape=IMAGE_SHAPE)
    image = Image.fromarray(memmap_array, "RGB")
    
    # กำหนดชื่อไฟล์เริ่มต้นจากชื่อไฟล์ .dat
    default_filename = os.path.splitext(os.path.basename(filename))[0] + ".png"
    
    # เปิด dialog ให้ผู้ใช้เลือกตำแหน่งเซฟไฟล์
    output_image = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default_filename, filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All Files", "*.*")])
    
    if not output_image:
        messagebox.showinfo("Canceled", "Save operation was canceled.")
        app_ui.log_message.set(f"Save operation was canceled")
        return None
    
    if output_image:
        image.save(output_image)
        print(f"Image saved as {output_image}")
        app_ui.log_message.set(f"Image save successfully!")   
     
def resetcall(app_ui:AppUI):
    call = messagebox.askquestion("Reset Programe","When you press reset program, all results will be deleted.")
    if call == 'yes' : 
        reset_action(app_ui)
        
def reset_action(app_ui:AppUI):
    app_ui.hide_all_ui()
    
    # ล้างค่าทั้งหมด
    app_ui.video_path.set("")
    for var in app_ui.type_vars:
        var.set(False)
    for var in app_ui.color_vars:
        var.set(False)
    app_ui.processing_result = None
    app_ui.processing_fullresult = None
        
    app_ui.type_frame.place(x=20, y=20, width=350, height=260)
    app_ui.color_frame.place(x=20, y=300, width=350, height=360)
    app_ui.video_frame.place(x=380, y=20, width=400, height=305)
    app_ui.start_button.place(x=505, y=340, width=150, height=50)
    app_ui.loadfile_button.place(x=505, y=440, width=150, height=50)
    
    app_ui.video_frame.config(text="เลือกวิดีโอ")
    
    
def show_previous(app_ui:AppUI):
    if app_ui.current_index > 0:
        app_ui.current_index -= 1
        app_ui.selected_file.set(app_ui.image_file_list[app_ui.current_index])
        app_ui.load_image(app_ui.image_file_list[app_ui.current_index])

def show_next(app_ui:AppUI):
    if app_ui.current_index < len(app_ui.image_file_list) - 1:
        app_ui.current_index += 1
        app_ui.selected_file.set(app_ui.image_file_list[app_ui.current_index])
        app_ui.load_image(app_ui.image_file_list[app_ui.current_index])
    
# ฟังก์ชันที่จะเรียกใช้เมื่อกดปุ่มปิด X
def on_closing(root):
    if messagebox.askokcancel("ออกจากโปรแกรม", "คุณต้องการออกจากโปรแกรมและลบไฟล์ทั้งหมดหรือไม่?"):
        delete_clash()  # เรียกใช้ฟังก์ชันลบไฟล์
        root.destroy()  # ปิดโปรแกรม


