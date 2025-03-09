import numpy as np
import cv2 as cv
from sklearn.cluster import KMeans

# ฟังก์ชั่นแปลง HSV เป็น binHSV
def get_HSV_bins(hsv_pixel, binH, binS, binV):
    h, s, v = hsv_pixel

    # แบ่งค่า H, S, V ลงใน bins ตามค่าที่กำหนด
    bin_h = int(h / (180 / binH))  # Hue: 0-180 (แบ่ง binH = 16)
    bin_s = int(s / (256 / binS))  # Saturation: 0-255 (แบ่ง binS = 16)
    bin_v = int(v / (256 / binV))  # Value: 0-255 (แบ่ง binV = 4)

    return bin_h, bin_s, bin_v

# ฟังก์ชันตรวจสอบว่าเป็นสีขาว ดำ เทา หรือ เงิน
def get_achromatic_color_name(hsv_pixel):
    bin_h, bin_s, bin_v = get_HSV_bins(hsv_pixel, binH=16, binS=8, binV=16)
    # ใช้ Saturation และ Value ในการคำนวณ
    if bin_s <= 1 or bin_v <= 4 : # Saturation ต่ำมาก ถือว่าเป็นสีไม่มีสี
        if bin_v >= 12:  # Value สูงมาก ถือว่าเป็นสีขาว (ได้ผลดีมากๆ)
            return 'White'
        elif bin_v <= 4:  # Value ต่ำมาก ถือว่าเป็นสีดำ
            return 'Black'
        elif 4 < bin_v <= 6 and bin_s <= 1 :  # Value อยู่ในช่วงกลาง ถือว่าเป็นสีเทา
            return 'Gray'
        elif 6 < bin_v <= 11 and bin_s <= 1:  # Value อยู่ในช่วงนี้ ถือว่าเป็นสีเงิน
            return 'Silver'    
    return get_color_name_from_HSV(hsv_pixel)

# ฟังก์ชันตรวจสอบว่าพิกเซลนั้นเป็นสีอะไรในกรณีมีสี
def get_color_name_from_HSV(hsv_pixel):
    h, s, v = hsv_pixel
    bin_h, bin_s, bin_v = get_HSV_bins(hsv_pixel, binH=60, binS=16, binV=16)
    # ตรวจสอบ Saturation ให้เพียงพอสำหรับการระบุสี
    if bin_s >= 4 and bin_v >= 2:
        if (0 <= bin_h <= 3) or (57 <= bin_h <= 60):
            return 'Red'
        elif 3 < bin_h <= 5:
            return 'Brown'
        elif 5 < bin_h <= 11:
            return 'Yellow'
        elif 11 < bin_h <=26:
            return 'Green'
        elif 26 < bin_h <= 46:
            return 'Blue'
        elif 46 < bin_h <=51 :
            return 'Purple'
        elif 51 < bin_h <=56 :
            return 'Pink'
    return 'Unknown'

#--------------------------------------------------------------------------------------------------------------

def luminance_edit(image):    
    # แปลงภาพเป็น LAB
    image_lab = cv.cvtColor(image, cv.COLOR_BGR2LAB)
    L, A, B = cv.split(image_lab)
    
    # คำนวณค่า Luminance
    luminance = L.astype(np.float32)

    # คำนวณค่า Max, Min, Median ของ Luminance
    luminance_median = np.median(luminance)

    # 🔹 Trimmed Mean (เอาเฉพาะค่ากลาง 90%)
    lower_bound = np.percentile(luminance, 5)   # ตัด 5% ล่าง
    upper_bound = np.percentile(luminance, 95)  # ตัด 5% บน
    trimmed_luminance = luminance[(luminance >= lower_bound) & (luminance <= upper_bound)]
    luminance_mean_trimmed = np.mean(trimmed_luminance)  # ใช้ค่าที่ตัด Outlier แล้ว

    #ใช้ Median + Trimmed Mean ในการตัดสิน
    if luminance_median < 80 or luminance_mean_trimmed < 80:
        adjusted_L = L + (100 - luminance_median) * 0.5  # เพิ่มสว่าง

        #ใช้ CLAHE ปรับ Contrast เฉพาะภาพมืด
        adjusted_L = np.clip(adjusted_L, 0, 255).astype(np.uint8)
        clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        adjusted_L = clahe.apply(adjusted_L)

    else:
        adjusted_L = L - (luminance_median - 80) * 0.5  # ลดสว่าง
    
    # จำกัดค่า Luminance ให้อยู่ในช่วง 0-255
    adjusted_L = np.clip(adjusted_L, 0, 255).astype(np.uint8)

    # รวมค่า L, A, B กลับเป็นภาพ LAB
    adjusted_lab = cv.merge([adjusted_L, A, B])

    # แปลงกลับเป็น BGR
    adjusted_image_bgr = cv.cvtColor(adjusted_lab, cv.COLOR_LAB2BGR)
    
    return adjusted_image_bgr

def blur_edit(image):
    ksize = (5,5)
    blur_edited = cv.GaussianBlur(image, ksize, 0)  
    #blur_edited = image
    return blur_edited

def k_means_clustering(image,k):
    kernal = k # 11 color + 1 unknow
    # แปลงเป็นค่า HSV
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    # Reshape ข้อมูลเพื่อใช้ใน K-means
    hsv_pixels = hsv_image.reshape((-1, 3))

    # ใช้ K-means clustering เพื่อหาค่าสีหลัก
    kmeans = KMeans(n_clusters=kernal)
    kmeans.fit(hsv_pixels)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    label_counts = np.bincount(labels)
    dominant_color = colors[label_counts.argmax()]
    
    h = dominant_color[0]
    s = dominant_color[1]
    v = dominant_color[2]
    return h,s,v


def hsv_classify(image):
    
    h,s,v = k_means_clustering(image,2)
    # ตรวจสอบกลุ่มสีไม่มีสี (Achromatic)
    hsv_color = [h,s,v]
    achromatic_color = get_achromatic_color_name(hsv_color)
    
    if achromatic_color:
        h,s,v = k_means_clustering(image,4)
        hsv_color = [h,s,v]
        achromatic_color = get_achromatic_color_name(hsv_color)
        return achromatic_color,h,s,v
    else:
        # ตรวจสอบกลุ่มสีที่มีสี
        h,s,v = k_means_clustering(image,7)
        hsv_color = [h,s,v]
        color_name = get_color_name_from_HSV(hsv_color)
        return color_name,h,s,v
    
    '''
    color_name = 'red'
    return color_name
    '''

def color_classifier(image):
    #luminance_edited = luminance_edit(image)
    
    blur_edited = blur_edit(image) 
    
    #h,s,v = k_means_clustering(blur_edited)
    
    color_name_classify,h,s,v = hsv_classify(blur_edited)
    
    return color_name_classify,h,s,v