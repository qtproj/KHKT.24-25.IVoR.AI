import flet as ft
import csv, os, base64, threading, time
from io import BytesIO
from PIL import Image
from datetime import datetime
from pathlib import Path

# from main import *
from LPclassify import classify


def tab1(page):
    # stop_event = threading.Event()
    # def process_camera_in_flet(view_frame, page, camera_index=0):
    #     """
    #     Process live camera feed and display it in the Flet app.
    #     """
    #     stop_event.clear()  # Ensure the stop event is cleared before starting

    #     def run_camera():
    #         folder_path, folder_50cc, folder_100cc = getDayFolder()
    #         csv_path = os.path.join(folder_path, "results.csv")

    #         cap = cv2.VideoCapture(camera_index)
    #         fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #         fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # Default to 30 FPS if unavailable
    #         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #         output_video_path = getUniqueFileName(os.path.join(folder_path, "CameraFeed.mp4"))
    #         out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    #         try:
    #             while not stop_event.is_set():  # Stop the loop if the stop_event is set
    #                 ret, frame = cap.read()
    #                 if not ret:
    #                     print("Failed to read from camera.")
    #                     break

    #                 # Process the frame for detection
    #                 recognized_plates = detectAndRecognize(frame)

    #                 for lp_text, box in recognized_plates:
    #                     plate_type = classify(lp_text)
    #                     if plate_type in ["50cc", "100cc"]:
    #                         color = (0, 255, 0) if plate_type == "50cc" else (0, 0, 255)

    #                         x1, y1, x2, y2 = box

    #                         # Draw bounding rectangles
    #                         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

    #                         # Draw plate text
    #                         cv2.putText(frame, lp_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    #                         # Log results and save images
    #                         log_results(csv_path, lp_text, plate_type)
    #                         if plate_type == "50cc":
    #                             save_plate(frame, lp_text, box, folder_50cc)
    #                         elif plate_type == "100cc":
    #                             save_plate(frame, lp_text, box, folder_100cc)

    #                 # Convert frame to base64 for Flet
    #                 _, buffer = cv2.imencode(".jpg", frame)
    #                 frame_data = base64.b64encode(buffer).decode("utf-8")

    #                 # Update the view_frame in the Flet UI
    #                 view_frame.content = ft.Image(src_base64=frame_data)
    #                 page.update()

    #                 # Write the frame to the output video
    #                 out.write(frame)

    #             print("Camera feed stopped.")
    #         finally:
    #             cap.release()
    #             out.release()
    #             cv2.destroyAllWindows()

    #     threading.Thread(target=run_camera, daemon=True).start()

    # def process_camera_live():
    #     # Show loading popup while camera initializes
    #     loading_popup = ft.AlertDialog(title=ft.Text("Opening Camera, please wait..."))
    #     page.dialog = loading_popup
    #     page.dialog.open = True
    #     page.update()

    #     def start_camera():
    #         try:
    #             # Start the camera feed in Flet
    #             process_camera_in_flet(view_frame, page)
    #         finally:
    #             page.dialog.open = False
    #             page.update()

    #     # Run the camera in a separate thread
    #     threading.Thread(target=start_camera).start()


    # Function to read data from the CSV file
    def readCsv(filePath):
        data = []
        if os.path.exists(filePath):
            with open(filePath, mode="r", encoding="utf-8", newline="") as file:
                csvReader = csv.DictReader(file)
                for row in csvReader:
                    data.append(row)
        return data

    # Get the folder of that day. 
    def getDayFolder():
        """
        Create and return the day's folder path with subfolders for 50cc and 100cc.
        """
        today = datetime.now().strftime("%d%m%Y")
        folderPath = os.path.join("output", today)
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
            return folderPath
        return folderPath   
    
    csvFilePath = os.path.join(getDayFolder(), "results.csv")

    # Load initial data
    data = readCsv(csvFilePath)

    # Define the DataTable
    dataTable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("License Plate")),
            ft.DataColumn(ft.Text("Vehicle")),
        ],
        rows=[],
    )  

    # Populate table
    def populateTable(rows):
        dataTable.rows.clear()
        for row in rows:
            dataTable.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row["License Plate"])),
                        ft.DataCell(ft.Text(row["Valid"])),
                    ]
                )
            )
        page.update()

    populateTable(data)

    # Background thread to monitor CSV changes
    def monitorCsv():
        last_modified = os.path.getmtime(csvFilePath) if os.path.exists(csvFilePath) else 0
        while True:
            time.sleep(2)  # Check every 2 seconds
            if os.path.exists(csvFilePath):
                current_modified = os.path.getmtime(csvFilePath)
                if current_modified != last_modified:
                    last_modified = current_modified
                    new_data = readCsv(csvFilePath)
                    populateTable(new_data)

    # Start the monitoring thread
    threading.Thread(target=monitorCsv, daemon=True).start()

    # def appCam(cameraIndex=0):
    #     # process_camera()
    #     loadingPopup = ft.AlertDialog(title=ft.Text("Opening Camera, please wait..."))
    #     page.dialog = loadingPopup
    #     page.dialog.open = True
    #     page.update()

    #     def camRun():
    #         cap = cv2.VideoCapture(cameraIndex)
    #         if not cap.isOpened():
    #             raise Exception("Failed to open camera")
            
    #         page.dialog.open = False
    #         page.update

    #         while True:
    #             ret, frame = cap.read()
    #             if not ret:
    #                 print("Failed to read from camera.")
    #                 break
            

    # # Left section: Unified frame for camera/video/image view
    view_frame = ft.Container(
        expand=True,
        bgcolor="black",  # Placeholder for the camera or video/image view
        alignment=ft.alignment.center,
    )

    # Open Camera Button
    # open_camera_button = ft.ElevatedButton(
    #     text="Open Camera",
    #     icon=ft.icons.VIDEOCAM,
    #     on_click=lambda e: start_camera(view_frame, page),
    # )

    # # Stop Camera Button
    # stop_camera_button = ft.ElevatedButton(
    #     text="Stop Camera",
    #     icon=ft.icons.VIDEOCAM_OFF,
    #     on_click=lambda e: stop_camera_feed(),
    # )


    # Left side layout
    left_layout = ft.Column(
        expand=2,
        controls=[
            view_frame,
            # open_camera_button,
            # stop_camera_button,
        ],
        spacing=20,
    )

    # Right section: Search and List view
    searchInput = ft.TextField(
        label="Search by License Plate",
        on_change=lambda e: populateTable(
            [
                row
                for row in data
                if searchInput.value.lower() in row["License Plate"].lower()
            ]
        ),
    )

    list_view = ft.ListView(
        expand=1,
        spacing=10,
        controls=[dataTable],
    )

    # Load data initially into the list view
    populateTable(data)


    # Right Side (DataList & )
    right_layout = ft.Column(
        expand=1,
        controls=[
            searchInput, 
            list_view,
        ],
        spacing=20,
    )

    # Combine both sections into a row
    layout = ft.Row(
        controls=[
            left_layout, 
            right_layout
        ],
        spacing=20,
    )

    return layout