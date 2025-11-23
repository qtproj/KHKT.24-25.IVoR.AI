# OFFICIAL

import flet as ft
import csv
import os


def tab2(page):
    # Function to read CSV data
    def readCsv(filePath):
        data = []
        if os.path.exists(filePath):
            with open(filePath, mode="r", encoding="utf-8", newline="") as file:
                csvReader = csv.DictReader(file)
                for row in csvReader:
                    data.append(row)
        return data

    # Function to write data to the CSV file
    def writeCsv(filePath, allRows):
        with open(filePath, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["License Plate", "Name", "DOB", "Graduation Year", "Class"],
            )
            writer.writeheader()
            writer.writerows(allRows)

    # CSV file path
    csvFilePath = "datauser/users_data.csv"
    
    # Load initial data
    data = readCsv(csvFilePath)

    def closeDiag():
        page.dialog.open = False
        page.update()

    # Define the DataTable
    dataTable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("License Plate")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Date of Birth")),
            ft.DataColumn(ft.Text("Graduation Year")),
            ft.DataColumn(ft.Text("Class")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
    )

    # Function to populate the table with rows
    def populateTable(rows):
        dataTable.rows.clear()
        for row in rows:
            dataTable.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row["License Plate"])),
                        ft.DataCell(ft.Text(row["Name"])),
                        ft.DataCell(ft.Text(row["DOB"])),
                        ft.DataCell(ft.Text(row["Graduation Year"])),
                        ft.DataCell(ft.Text(row["Class"])),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    # Edit Button (Pen Icon)
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        on_click=lambda e, r=row: editRowDialog(r),
                                    ),
                                    # Delete Button (Trash Icon)
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        on_click=lambda e, r=row: deleteRow(r),
                                    ),
                                ]
                            )
                        ),
                    ]
                )
            )
        page.update()

    # Populate the table initially
    populateTable(data)

    # Function to delete a row
    def deleteRow(row):
        # Remove the selected row from the data
        data.remove(row)

        # Rewrite the CSV file and refresh the table
        writeCsv(csvFilePath, data)
        populateTable(data)

    # Function to edit a row
    def editRowDialog(row):
        def saveChanges(e):
            # Update the row with new data
            row["License Plate"] = licensePlateInput.value
            row["Name"] = nameInput.value
            row["DOB"] = f"{dobMonthDropdown.value}/{dobDayDropdown.value}/{dobYearDropdown.value}"
            row["Graduation Year"] = gradYearInput.value
            row["Class"] = classInput.value

            # Rewrite the CSV file and refresh the table
            writeCsv(csvFilePath, data)
            populateTable(data)

            # Close the dialog
            page.dialog.open = False
            page.update()

        # Input fields for editing
        licensePlateInput = ft.TextField(label="License Plate", value=row["License Plate"])
        nameInput = ft.TextField(label="Name", value=row["Name"])

        # DOB Dropdowns for Day, Month, Year on the same row
        dobDayDropdown = ft.Dropdown(
            label="Day",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 32)],
            value=row["DOB"].split("/")[1] if row["DOB"] else "01",
            width=100,  # Adjust width for Day dropdown
        )
        dobMonthDropdown = ft.Dropdown(
            label="Month",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 13)],
            value=row["DOB"].split("/")[0] if row["DOB"] else "01",
            width=100,  # Adjust width for Month dropdown
        )
        dobYearDropdown = ft.Dropdown(
            label="Year",
            options=[ft.dropdown.Option(str(i)) for i in range(1900, 2024)],
            value=row["DOB"].split("/")[2] if row["DOB"] else "2023",
            width=120,  # Adjust width for Year dropdown
        )

        gradYearInput = ft.TextField(
            label="Graduation Year", value=row["Graduation Year"], hint_text="Year"
        )
        classInput = ft.TextField(label="Class", value=row["Class"])

        # Create the dialog with adjusted width and size
        page.dialog = ft.AlertDialog(
            title=ft.Text("Edit Row"),
            content=ft.Column(
                controls=[
                    licensePlateInput,
                    nameInput,
                    ft.Row(
                        controls=[
                            dobDayDropdown,
                            dobMonthDropdown,
                        ],
                        alignment=ft.MainAxisAlignment.START,  # Align the dropdowns to start
                    ),
                    dobYearDropdown,
                    gradYearInput,
                    classInput,
                ],
                scroll=ft.ScrollMode.AUTO,  # Enable scrolling if content overflows
            ),
            actions=[
                ft.TextButton("Save", on_click=saveChanges),
                ft.TextButton("Cancel", on_click=lambda e: closeDiag()),
            ],
        )
        page.dialog.width = 450  # Set a max width for the dialog
        page.dialog.height = 400  # Set a max height for the dialog
        page.dialog.open = True
        page.update()

    # Function to add a new row
    def addNewDialog():
        def saveNewData(e):
            # Create a new row
            newRow = {
                "License Plate": licensePlateInput.value,
                "Name": nameInput.value,
                "DOB": f"{dobMonthDropdown.value}/{dobDayDropdown.value}/{dobYearDropdown.value}",
                "Graduation Year": gradYearInput.value or "2023",
                "Class": classInput.value,
            }
            data.append(newRow)

            # Write the new row to the CSV and refresh the table
            writeCsv(csvFilePath, data)
            populateTable(data)

            # Close the dialog
            page.dialog.open = False
            page.update()

        # Input fields for adding a new row
        licensePlateInput = ft.TextField(label="License Plate")
        nameInput = ft.TextField(label="Name")

        # DOB Dropdowns for Day, Month, Year on the same row
        dobDayDropdown = ft.Dropdown(
            label="Day",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 32)],
            width=100,  # Adjust width for Day dropdown
        )
        dobMonthDropdown = ft.Dropdown(
            label="Month",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 13)],
            width=100,  # Adjust width for Month dropdown
        )
        dobYearDropdown = ft.Dropdown(
            label="Year",
            options=[ft.dropdown.Option(str(i)) for i in range(1900, 2024)],
            width=120,  # Adjust width for Year dropdown
        )

        gradYearInput = ft.TextField(label="Graduation Year", hint_text="Year")
        classInput = ft.TextField(label="Class")

        # Create the dialog with adjusted width and size
        page.dialog = ft.AlertDialog(
            title=ft.Text("Add New Row"),
            content=ft.Column(
                controls=[
                    licensePlateInput,
                    nameInput,
                    ft.Row(
                        controls=[
                            dobDayDropdown,
                            dobMonthDropdown,
                        ],
                        alignment=ft.MainAxisAlignment.START,  # Align the dropdowns to start
                    ),
                    dobYearDropdown,
                    gradYearInput,
                    classInput,
                ],
                scroll=ft.ScrollMode.AUTO,  # Enable scrolling if content overflows
            ),
            actions=[
                ft.TextButton("Add", on_click=saveNewData),
                ft.TextButton("Cancel", on_click=lambda e: closeDiag()),
            ],
        )
        page.dialog.width = 450  # Set a max width for the dialog
        page.dialog.height = 400  # Set a max height for the dialog
        page.dialog.open = True
        page.update()

    # Search input field
    searchInput = ft.TextField(
        label="Search by Name or License Plate",
        on_change=lambda e: populateTable(
            [
                row
                for row in data
                if searchInput.value.lower() in row["Name"].lower()
                or searchInput.value.lower() in row["License Plate"].lower()
            ]
        ),
    )

    # Add New button
    addNewButton = ft.ElevatedButton(
        text="Add New",
        icon=ft.icons.ADD,
        on_click=lambda e: addNewDialog(),
    )

    # Return the layout for the tab
    return ft.Column(
        expand=True,
        controls=[
            # Search and Add New section
            ft.Container(
                padding=10,
                content=ft.Row(
                    controls=[
                        ft.Container(
                            # expand=True, 
                            content=searchInput,
                        ),
                        addNewButton,
                    ],
                ),
            ),
            # Data table section inside a ListView for scrollability
            ft.ListView(
                expand=True,  # Ensure the ListView expands to fill available space
                controls=[dataTable],
            ),
        ],
    )