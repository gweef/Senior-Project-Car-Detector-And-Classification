import tkinter as tk
from tkinter import ttk


class AppUI:
    def __init__(self, root):
        # ตัวแปรเก็บ path ของวิดีโอ
        self.video_path = tk.StringVar()
        
        # ตัวเลือกประเภทและสี
        self.types = ["Sedan", "SUV", "Pick-Up", "Van", "Bus", "Truck", "Motorcycle"]
        self.colors = ["Black", "Gray", "Silver", "White", "Red", "Blue", "Yellow", "Green", "Brown", "Pink", "Purple"]
        self.type_vars = [tk.BooleanVar() for _ in self.types]
        self.color_vars = [tk.BooleanVar() for _ in self.colors]
        
        self.processing_result = None
        self.processing_fullresult = None

        # สร้าง UI ต่างๆ
        self.type_frame = self.create_type_frame(root)
        self.color_frame = self.create_color_frame(root)
        self.video_frame = self.create_video_button(root)
        self.start_button = self.create_start_button(root)
        self.waiting_frame = self.create_waiting_frame(root)
        self.start_detial_frame,self.start_detial_label = self.create_start_detial_frame(root)
        self.log_frame, self.log_message = self.create_log_frame(root)
        self.cancel_button = self.create_cancel_button(root)
        self.progress_bar = self.create_progress_bar(self.waiting_frame)
        self.complete_frame = self.create_complete_frame(root)
        self.details_button = self.create_details_button(root)
        self.export_button = self.create_export_button(root)
        self.exportvar_button = self.create_exportVar_button(root)
        self.exportfull_button = self.create_exportFull_button(root)
        self.exportfullvar_button = self.create_exportFullVar_button(root)
        self.showimage_Frame = self.create_showimage_Frame(root)
        self.dataimage_Frame = self.create_dataimage_Frame(root)
        self.saveimage_button = self.create_saveimage_button(root)
        self.previousimage_button = self.create_previousimage_button(root)
        self.nextimage_button = self.create_nextimage_button(root)
        self.reset_button = self.create_reset_button(root)
        # สร้างตารางใน Frame
        self.data_table = self.create_data_table(root)
        
        
        
        # เก็บ UI Components ที่ต้องการซ่อนใน List
        self.all_ui_components = [
            self.type_frame, self.color_frame, self.video_frame, 
            self.start_button, self.waiting_frame, self.start_detial_frame,
            self.log_frame, self.cancel_button, self.complete_frame,
            self.details_button,self.data_table,self.export_button,self.exportvar_button,
            self.exportfull_button,self.exportfull_button,self.exportfullvar_button,
            self.showimage_Frame,self.saveimage_button,self.previousimage_button,
            self.nextimage_button,self.reset_button,self.dataimage_Frame
        ]

    def create_type_frame(self, root):
        frame = tk.Frame(root, bg="lightblue", bd=2, relief="ridge")
        frame.place(x=20, y=20, width=350, height=260)
        tk.Label(frame, text="-Type-", font=("Arial", 16), bg="lightblue").pack(anchor="n", pady=5)
            
        # เพิ่ม CheckBox "Select All"
        select_all_type = tk.BooleanVar()

        def toggle_all_types():
            for var in self.type_vars:
                var.set(select_all_type.get())  # ตั้งค่า CheckBox ทั้งหมดตาม Select All

        tk.Checkbutton(
            frame,
            text="Select All",
            bg="lightblue",
            variable=select_all_type,
            command=toggle_all_types
        ).pack(anchor="w", padx=10)
        for t, var in zip(self.types, self.type_vars):
            tk.Checkbutton(frame, text=t, bg="lightblue", variable=var).pack(anchor="w", padx=10)
        return frame

    def create_color_frame(self, root):
        frame = tk.Frame(root, bg="lightblue", bd=2, relief="ridge")
        frame.place(x=20, y=300, width=350, height=360)
        tk.Label(frame, text="-Color-", font=("Arial", 16), bg="lightblue").pack(anchor="n", pady=5)
        
        # เพิ่ม CheckBox "Select All"
        select_all_color = tk.BooleanVar()

        def toggle_all_types():
            for var in self.color_vars:
                var.set(select_all_color.get())  # ตั้งค่า CheckBox ทั้งหมดตาม Select All

        tk.Checkbutton(
            frame,
            text="Select All",
            bg="lightblue",
            variable=select_all_color,
            command=toggle_all_types
        ).pack(anchor="w", padx=10)
        
        for c, var in zip(self.colors, self.color_vars):
            tk.Checkbutton(frame, text=c, bg="lightblue", variable=var).pack(anchor="w", padx=10)
        return frame

    def create_video_button(self, root):
        button = tk.Button(root, bg="orange", bd=2, relief="ridge", text="เลือกวิดีโอ", font=("Arial", 16))
        button.place(x=380, y=20, width=400, height=305)
        return button

    def create_start_button(self, root):
        button = tk.Button(root, text="Start", bg="lime", font=("Arial", 18))
        button.place(x=505, y=340, width=150, height=50)
        return button

    def create_waiting_frame(self, root):
        frame = tk.Frame(root, bg="skyblue", bd=2, relief="ridge")
        tk.Label(frame, text="waiting...", bg="skyblue", font=("Arial", 24)).pack(pady=20)
        return frame
    
    def create_start_detial_frame(self, root):
        frame = tk.Frame(root, bg="white", bd=2, relief="ridge")

        # สร้าง StringVar สำหรับข้อความ
        start_detail_label = tk.StringVar()
        start_detail_label.set("")  # เริ่มต้นด้วยข้อความว่าง

        # สร้าง Label สำหรับแสดงข้อความ
        tk.Label(
            frame,
            textvariable=start_detail_label,
            bg="white",
            font=("Arial", 9),
            anchor="nw",
            justify="left",
            wraplength=300  # กำหนดความกว้างสำหรับตัดข้อความ
        ).pack(fill="both", expand=True, padx=5, pady=5)
        
        return frame,start_detail_label

    
    def create_log_frame(self, root):
        frame = tk.Frame(root, bg="white", bd=2, relief="ridge")
        log_message = tk.StringVar()
        log_message.set("")
        tk.Label(frame, textvariable=log_message, bg="white", font=("Arial", 14), anchor="w", justify="left").pack(fill="both", expand=True, padx=5, pady=5)
        return frame, log_message

    def create_cancel_button(self, root):
        button = tk.Button(root, text="Cancel", bg="red", font=("Arial", 18))
        return button

    def create_progress_bar(self, parent_frame):
        progress_bar = ttk.Progressbar(parent_frame, orient="horizontal", mode="indeterminate", length=200)
        progress_bar.pack(pady=10)
        return progress_bar

    def create_complete_frame(self, root):
        frame = tk.Frame(root, bg="skyblue", bd=2, relief="ridge")
        tk.Label(frame, text="complete", bg="skyblue", font=("Arial", 24)).pack(pady=20)
        return frame
    
    def create_details_button(self, root):
        button = tk.Button(root, text="View Details", bg="green", font=("Arial", 18))
        return button
    
    def create_export_button(self, root):
        button = tk.Button(root, text="Export File", bg="blue", font=("Arial", 18))
        return button
    
    def hide_all_ui(self):
        for component in self.all_ui_components:
            component.place_forget()
            
    def get_selected_types_and_colors(self):
        selected_types = [self.types[i] for i, var in enumerate(self.type_vars) if var.get()]
        selected_colors = [self.colors[i] for i, var in enumerate(self.color_vars) if var.get()]
        return selected_types, selected_colors
    
    def create_exportFull_button(self, root):
        button = tk.Button(root, text="Export Full File", bg="blue", font=("Arial", 15))
        return button

    def create_exportVar_button(self,root):
        button = tk.Button(root, text="Export Var(.plk)", bg="blue", font=("Arial", 15))
        return button
    
    def create_exportFullVar_button(self,root):
        button = tk.Button(root, text="Export Full Var", bg="blue", font=("Arial", 15))
        return button
    
    def create_showimage_Frame(self,root):
        frame = tk.Frame(root, bg="green", bd=2, relief="ridge")
        tk.Label(frame, text="image", bg="green", font=("Arial", 24)).pack(pady=20)
        return frame
    
    def create_dataimage_Frame(self,root):
        frame = tk.Frame(root, bg="skyblue", bd=2, relief="ridge")
        tk.Label(frame, text="dataimage", bg="skyblue", font=("Arial", 12)).pack(pady=8)
        return frame
    
    def create_saveimage_button(self,root):
        button = tk.Button(root, text="Save Image", bg="blue", font=("Arial", 18))
        return button
    
    def create_previousimage_button(self,root):
        button = tk.Button(root, text="<", bg="blue", font=("Arial", 25))
        return button
    
    def create_nextimage_button(self,root):
        button = tk.Button(root, text=">", bg="blue", font=("Arial", 25))
        return button
    
    def create_reset_button(self,root):
        button = tk.Button(root, text="Reset", bg="Red", font=("Arial", 12))
        return button
    
    def create_data_table(self, root):
        frame = tk.Frame(root, bg="lightblue", bd=2, relief="ridge")
        
        # สร้าง Treeview
        columns = ("carID", "Time", "Type", "Color")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        # กำหนดหัวข้อของแต่ละคอลัมน์
        tree.heading("carID", text="Car ID")
        tree.heading("Time", text="Time")
        tree.heading("Type", text="Type")
        tree.heading("Color", text="Color")

        # กำหนดขนาดของแต่ละคอลัมน์
        tree.column("carID", width=50, anchor="center")
        tree.column("Time", width=100, anchor="center")
        tree.column("Type", width=100, anchor="center")
        tree.column("Color", width=100, anchor="center")

        # เพิ่ม Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # วาง Scrollbar และ Treeview ใน Frame
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # เก็บ Treeview แยกต่างหาก
        self.treeview = tree

        # ซ่อน frame เริ่มต้น
        frame.place_forget()

        return frame

    def populate_table(self, data):
        """
        เติมข้อมูลในตาราง
        :param data: List ของ Dictionary ที่มีคีย์ 'carID', 'Time', 'Type', 'Color'
        """
        # ล้างข้อมูลเก่า
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # เติมข้อมูลใหม่
        for item in data:
            self.treeview.insert("", "end", values=(item["carID"], item["Time"], item["Type"], item["Color"]))
