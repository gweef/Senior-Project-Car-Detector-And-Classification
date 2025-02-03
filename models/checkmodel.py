import torch

model_path = "models/wheel01.pt"
checkpoint = torch.load(model_path, map_location='cpu')

# ตรวจสอบข้อมูลใน checkpoint
print(checkpoint.keys())

# หากมีส่วน 'meta' หรือ 'version' ให้พิมพ์ออกมา
if 'meta' in checkpoint:
    print(checkpoint['version'])
    
from ultralytics import YOLO

# Load your trained model
model = YOLO('models/wheel01.pt')
model.to('cuda')

import torch
print(torch.cuda.is_available()) 

import torch
import torchvision

print("PyTorch version:", torch.__version__)
print("Torchvision version:", torchvision.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
