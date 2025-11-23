import os
import cv2
import csv
from datetime import datetime
from OCR import detectAndRecognize
from LPclassify import classify
import re

def getDayFolder():
    """
    Create and return the day's folder path with subfolders for 50cc and 100cc.
    """
    today = datetime.now().strftime("%d%m%Y")
    folderPath = os.path.join("output", today)
    os.makedirs(folderPath, exist_ok=True)

    # Create subfolders for 50cc and 100cc
    folder50cc = os.path.join(folderPath, "50cc")
    folder100cc = os.path.join(folderPath, "100cc")
    os.makedirs(folder50cc, exist_ok=True)
    os.makedirs(folder100cc, exist_ok=True)

    return folderPath, folder50cc, folder100cc


def save_plate(frame, plate_text, box, output_folder):
    """
    Save license plate image in a folder named after the license plate.
    If the folder exists, append the image; otherwise, create a new folder.
    """
    # Clean the license plate text to use as folder name (remove special characters)
    plate_id = re.sub(r'[^A-Za-z0-9]', '', plate_text)  # Remove special characters

    # Create the folder for the vehicle if it does not exist
    plate_folder = os.path.join(output_folder, plate_id)
    os.makedirs(plate_folder, exist_ok=True)

    # Crop the detected license plate region from the frame
    x1, y1, x2, y2 = box
    height, width = frame.shape[:2]
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(width, x2), min(height, y2)
    plate_image = frame[y1:y2, x1:x2]

    # Save the cropped image with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plate_image_filename = f"{plate_id}_{timestamp}.jpg"
    plate_image_path = os.path.join(plate_folder, plate_image_filename)

    # Save the image
    cv2.imwrite(plate_image_path, plate_image)
    print(f"Saved plate image: {plate_image_path}")


def log_results(csv_path, lp_text, is_valid):
    """
    Log or update license plate results in a CSV file.
    If the license plate already exists, update its information.
    """ 
    file_exists = os.path.exists(csv_path)

    lp_text = re.sub(r'[^A-Za-z0-9]', '', lp_text)  # Remove special characters
    rows = []
    if file_exists:
        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

    found = False
    for row in rows:
        if row[0] == lp_text:
            row[1] = is_valid
            found = True
            break

    if not found:
        rows.append([lp_text, is_valid])

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["License Plate", "Valid"])
        writer.writerows(rows)

    print(f"Log updated for license plate: {lp_text}")


def getUniqueFileName(filePath):
    """
    Generate a unique file name by appending a number if the file already exists.
    """
    base, ext = os.path.splitext(filePath)
    counter = 1
    uniqueFilePath = filePath

    while os.path.exists(uniqueFilePath):
        uniqueFilePath = f"{base}_{counter}{ext}"
        counter += 1

    return uniqueFilePath

def process_frame(frame, csv_path, folder_50cc, folder_100cc):
    """
    Process a single frame for license plate detection and classification.
    """
    recognized_plates = detectAndRecognize(frame)

    for lp_text, box in recognized_plates:
        plate_type = classify(lp_text)  # Get plate type (50cc, 100cc, invalid)

        if plate_type in ["50cc", "100cc"]:  # Process only valid plates
            color = (0, 255, 0) if plate_type == "50cc" else (0, 0, 255)
            x1, y1, x2, y2 = box

            # Draw bounding box and label on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            cv2.putText(frame, lp_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            log_results(csv_path, lp_text, plate_type)

            # Save image in the appropriate folder
            if plate_type == "50cc":
                save_plate(frame, lp_text, box, folder_50cc)
            elif plate_type == "100cc":
                save_plate(frame, lp_text, box, folder_100cc)

    return frame


def process_video(video_path):
    """
    Process a video file for license plate detection and classification.
    """
    folder_path, folder_50cc, folder_100cc = getDayFolder()
    csv_path = os.path.join(folder_path, "results.csv")

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Prepare output video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video_path = getUniqueFileName(os.path.join(folder_path, "outputVideo.mp4"))
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        print(f"Processing frame {frame_idx + 1}/{total_frames}")
        processed_frame = process_frame(frame, csv_path, folder_50cc, folder_100cc)
        out.write(processed_frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"Processing complete. Results saved in {folder_path}")


def process_image(image_path):
    """
    Process a single image file for license plate detection and classification.
    """
    folder_path, folder_50cc, folder_100cc = getDayFolder()
    csv_path = os.path.join(folder_path, "results.csv")

    frame = cv2.imread(image_path)
    processed_frame = process_frame(frame, csv_path, folder_50cc, folder_100cc)

    output_image_path = getUniqueFileName(os.path.join(folder_path, f"processed_{os.path.basename(image_path)}"))
    cv2.imwrite(output_image_path, processed_frame)
    print(f"Processed image saved to: {output_image_path}")

camera_stop_flag = False
def process_camera(camera_index=0):
    """
    Process live camera feed, detect license plates, and record the video.
    """
    folder_path, folder_50cc, folder_100cc = getDayFolder()
    csv_path = os.path.join(folder_path, "results.csv")

    cap = cv2.VideoCapture(camera_index)
    # cap = captureVid

    # Prepare video recording
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # Default to 30 FPS if unavailable
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_video_path = getUniqueFileName(os.path.join(folder_path, "CameraFeed.mp4"))
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera.")
            break

        # Process the frame for detection
        recognized_plates = detectAndRecognize(frame)

        for lp_text, box in recognized_plates:
            plate_type = classify(lp_text)
            if plate_type in ["50cc", "100cc"]:
                color = (0, 255, 0) if plate_type == "50cc" else (0, 0, 255)

                x1, y1, x2, y2 = box

                # Draw bounding rectangles
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                # Draw plate text
                cv2.putText(frame, lp_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                # Log results and save images
                log_results(csv_path, lp_text, plate_type)
                if plate_type == "50cc":
                    save_plate(frame, lp_text, box, folder_50cc)
                elif plate_type == "100cc":
                    save_plate(frame, lp_text, box, folder_100cc)

        # Show the live feed
        cv2.imshow("License Plate Detection", frame)
        

        # Write the frame to the output video
        out.write(frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
#     # path = """resources/test/anh2bienso.jpg"""
#     path = """resources/test/videoxe50cc.mp4"""
#     process_video(path)
#     # process_image(path)
#     path = """resources/test/videoxe100cc.mp4"""
    # process_video("""C:\\Users\\henry\\Downloads\\DATATEST\\6144676484480.mp4""") 
#     # process_image(path)
    process_camera()  