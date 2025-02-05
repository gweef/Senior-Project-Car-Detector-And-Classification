import tkinter as tk
from ui.class_ui import AppUI
from ui.component import on_start, cancel_action, open_video_file,export_action,details_action,exportvar_action,resetcall,on_closing


def main_ui() :
    root = tk.Tk()
    root.title("Car Type and Color Recognition")
    root.geometry("810x700")

    app_ui = AppUI(root)
    
    
    # ตั้งค่าปุ่ม Start
    app_ui.start_button.config(
        command=lambda: on_start(app_ui)
    )
    
    #ปุ่มเลือกวิดีโอ
    app_ui.video_frame.config(
        command=lambda: open_video_file(app_ui.video_path,app_ui.video_frame)
    )
    
    #ปุ่มยกเลิก
    app_ui.cancel_button.config(
        command=lambda:cancel_action(app_ui)
    )
    
    app_ui.export_button.config(
        command=lambda: export_action(app_ui,0)
    )
    
    app_ui.exportfull_button.config(
        command=lambda: export_action(app_ui,1)    
    )
    
    app_ui.details_button.config(
        command=lambda: details_action(app_ui)
    )
    
    app_ui.exportvar_button.config(
        command=lambda: exportvar_action(app_ui,0)
    )
    
    app_ui.exportfullvar_button.config(
        command=lambda: exportvar_action(app_ui,1)
    )
    
    app_ui.reset_button.config(
        command= lambda : resetcall(app_ui)
    )
    
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    
    
    

    root.mainloop()
