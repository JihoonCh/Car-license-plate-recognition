import cv2
import numpy as np
import easyocr
import pytesseract
import re
import os

# 한국 번호판 패턴
license_plate_pattern = re.compile(r'^\d{2,3}[가-힣]\s?\d{4}$')

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)
    return thresh

def validate_plate(text):
    text = re.sub(r'\s+', '', text)
    return bool(license_plate_pattern.match(text))

def detect_text(image_path, confidence_threshold=0.65):
    reader = easyocr.Reader(['ko', 'en'])
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 불러올 수 없습니다: {image_path}")
        return []

    result = reader.readtext(image)
    detected_plates = []

    for (bbox, text, prob) in result:
        if len(text) >= 7 and any(char.isdigit() for char in text):
            if prob < confidence_threshold:
                # 낮은 신뢰도 결과에 대한 추가 처리
                x, y = map(int, bbox[0])
                w = int(bbox[1][0] - bbox[0][0])
                h = int(bbox[2][1] - bbox[0][1])
                roi = image[y:y+h, x:x+w]

                # 이미지 전처리 및 Tesseract OCR 적용
                preprocessed = preprocess_image(roi)
                text_tesseract = pytesseract.image_to_string(preprocessed, lang='kor', config='--psm 7')
                text_tesseract = text_tesseract.strip()

                # EasyOCR과 Tesseract 결과 비교
                if validate_plate(text_tesseract):
                    text = text_tesseract
                    prob = max(prob, 0.8)  # 신뢰도 상향 조정

            if validate_plate(text):
                detected_plates.append((text, prob))

    return detected_plates

# 이미지 경로 설정
image_dir = '/home/jhchoi/Downloads/car'
image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]

# 이미지 처리
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    print(f"Processing {image_path}")
    plates = detect_text(image_path)
    if plates:
        for text, prob in plates:
            print(f"감지된 번호판: {text} (신뢰도: {prob:.2f})")
    else:
        print("감지된 번호판이 없습니다.")
    print()
