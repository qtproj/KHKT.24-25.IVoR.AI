import flet as ft
import csv, threading, time
from sources.tab2 import tab2
from sources.tab1 import tab1
from main import process_camera, process_image, process_video

def main(page: ft.Page):
 
    # Tab "About"
    # def tab3():
    #     return ft.Container(
    #         expand=True,
    #         content=ft.Text("About Tab Content", style="headlineMedium"),
    #     )

    # Create Tabs
    def createTabs():
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Live", 
                    icon=ft.icons.HOME_ROUNDED, 
                    content=ft.Container(
                        padding=5,
                        content=tab1(page),
                    ),
                ),
                ft.Tab(
                    text="Search", 
                    icon=ft.icons.MANAGE_SEARCH_ROUNDED, 
                    content=tab2(page)
                ),
                # ft.Tab(
                #     text="About", 
                #     icon=ft.icons.PERSON_ROUNDED, 
                #     content=pass
                # ),
            ],
        )

    def show_loading_dialog(page, message="PROCESSING... PLEASE WAIT!!!"):
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Text(message),
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.dialog.close())
            ],
        )
        page.dialog = loading_dialog
        page.dialog.open = True
        page.update()

    # Hide loading dialog
    def hide_loading_dialog(page):
        page.dialog.open = False
        page.update()

    # Image processing function
    def processImage(image_path, page):
        show_loading_dialog(page, message="PROCESSING IMAGE... PLEASE WAIT!!!")
        try:
            # Simulate image processing
            process_image(image_path)
        finally:
            hide_loading_dialog(page)

    # Video processing function
    def processVideo(video_path, page):
        show_loading_dialog(page, message="PROCESSING VIDEO... PLEASE WAIT!!!")
        try:
            # Simulate video processing
            process_video(video_path)
        finally:
            hide_loading_dialog(page)

# FilePicker callbacks
    def on_image_result(e: ft.FilePickerResultEvent, page):
        if e.files:
            file_path = e.files[0].path
            print(f"Selected image file: {file_path}")

            # Run image processing in a separate thread
            threading.Thread(target=processImage, args=(file_path, page)).start()

    def on_video_result(e: ft.FilePickerResultEvent, page):
        if e.files:
            file_path = e.files[0].path
            print(f"Selected video file: {file_path}")

            # Run video processing in a separate thread
            threading.Thread(target=processVideo, args=(file_path, page)).start()
    
    filePicker_image = ft.FilePicker(on_result=lambda e: on_image_result(e, page))
    filePicker_video = ft.FilePicker(on_result=lambda e: on_video_result(e, page))
    
    page.overlay.append(filePicker_image)
    page.overlay.append(filePicker_video)

    def imageProcess(e):
        filePicker_image.pick_files(allow_multiple=False)
    def videoProcess(e):
        filePicker_video.pick_files(allow_multiple=False)

    # Create Buttons
    def createButtons():
        return ft.Container(
            height=60,
            # bgcolor="green",
            padding=10,
            content=ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                text="Open Camera",
                                icon=ft.icons.VIDEOCAM_ROUNDED,
                                on_click=lambda _: process_camera(camera_index=0),
                            ),
                            # ft.ElevatedButton(
                            #     text="Stop Camera",
                            #     icon=ft.icons.VIDEOCAM_OFF,
                            #     on_click=lambda _:,
                            # ),
                            ft.ElevatedButton(  
                                text="From Image",
                                icon=ft.icons.IMAGE_ROUNDED,
                                on_click=imageProcess,
                            ),
                            ft.ElevatedButton(
                                text="From Video",
                                icon=ft.icons.VIDEO_FILE_ROUNDED,
                                on_click=videoProcess,
                            ),
                        ]
                    ),
                    ft.ElevatedButton(
                        text="Quit App",
                        icon=ft.icons.EXIT_TO_APP_ROUNDED,
                        on_click=lambda _: page.window.close(),
                    ),
                ],
            ),
        )
    page.update()
    
    # Page Layout
    page.add(
        ft.Column(
            expand=True,
            controls=[
                # Full width container for the Tabs section
                ft.Container(
                    expand=True,
                    content=createTabs(),
                ),
                createButtons(),
            ],
        )
    )


if __name__ == "__main__":
    ft.app(target=main)