import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
from LPclassify import *

# Initialize PaddleOCR
PADDLEOCR = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='en', det=False, show_log=False)

# Load YOLO Model
model = YOLO("model/LicensePlateDetect/weights/LPdetect.pt")  # Replace with your YOLOv8 model path


def preprocessPlate(plate):
    """
    Preprocess the license plate image for OCR by converting to grayscale, 
    binarizing, and reducing noise.
    """
    gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    _, binary_plate = cv2.threshold(gray_plate, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Binarize
    denoised_plate = cv2.GaussianBlur(binary_plate, (5, 5), 0)  # Reduce noise
    return denoised_plate

def readLP(plate):
    """
    Perform OCR on the cropped license plate region using PaddleOCR with preprocessing.
    """
    # Preprocess the plate image before feeding it to OCR
    preprocessedPlate = preprocessPlate(plate)
    
    try:
        # Perform OCR
        result = PADDLEOCR.ocr(preprocessedPlate, cls=False, det=True)  # Enable detection
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return ""

    # Parse the OCR result
    text = ''
    if result and isinstance(result[0], list):  # Ensure result structure
        for line in result[0]:
            if len(line) > 1 and isinstance(line[1], (list, tuple)):  # Check for valid text
                text += line[1][0]  # Extract recognized text safely

    return text.strip()  # Return cleaned text

def detectAndRecognize(image, detection_threshold=0.5):
    """
    Detect license plates using YOLO and recognize text using PaddleOCR.
    """
    try:
        # Detect license plates with YOLO
        results = model(image)  # Detect plates
        boxes = results[0].boxes.xyxy.cpu().numpy()  # Bounding boxes
        scores = results[0].boxes.conf.cpu().numpy()  # Confidence scores
    except Exception as e:
        print(f"Error during YOLO detection: {e}")
        return []

    # Initialize result list
    recognizedPlates = []

    for idx, box in enumerate(boxes):
        if scores[idx] > detection_threshold:  # Filter by confidence score
            x1, y1, x2, y2 = map(int, box[:4])  # Ensure only the first four values are used
            
            # Crop license plate region
            plateRegion = image[y1:y2, x1:x2]
            
            # Perform OCR on cropped plate region
            plateText = readLP(plateRegion)

            # finalPlateText = re.sub(r'[^A-Za-z0-9]', '', plate_text)
            
            if plateText:  # If OCR found some text
                recognizedPlates.append((plateText, (x1, y1, x2, y2)))  # Save text and bounding box
    
    return recognizedPlates