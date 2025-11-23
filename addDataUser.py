import os
import csv
from shutil import copy2

def addData(imagefile, lplate, name, dob, grad, inclass):
    # Resolve absolute paths
    base_dir = os.path.abspath('datauser')
    imagefile = os.path.abspath(imagefile)
    license_dir = os.path.join(base_dir, lplate)
    csv_file = os.path.join(base_dir, 'users_data.csv')
    
    os.makedirs(license_dir, exist_ok=True)
    
    # Save the image in the license plate's folder
    image_dest = os.path.join(license_dir, os.path.basename(imagefile))
    try:
        copy2(imagefile, image_dest)
    except FileNotFoundError:
        # print(f"Image file '{imagefile}' not found. Please check the path.")
        return
    
    # Load existing data and update/append entry for the license plate
    updated = False
    rows = []
    header = ['License Plate', 'Name', 'DOB', 'Graduation Year', 'Class', 'Image Path']
    
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            if rows and rows[0] == header:
                for i, row in enumerate(rows[1:], start=1):
                    if row[0] == lplate:
                        rows[i] = [lplate, name, dob, grad, inclass, image_dest]
                        updated = True
                        break
    
    if not updated:
        rows.append([lplate, name, dob, grad, inclass, image_dest])
    
    # Write the updated rows back to the CSV file
    with open(csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows[1:] if rows and rows[0] == header else rows)
    
    # print(f"Data for license plate '{lplate}' {'updated' if updated else 'added'} successfully.")
    # print(f"Image saved to: {image_dest}")
    # print(f"CSV updated at: {csv_file}")

# # Example usage
# addData("sources/test/a.jpg", "ABC123", "John Doe", "1990-01-01", "2013", "Physics")
