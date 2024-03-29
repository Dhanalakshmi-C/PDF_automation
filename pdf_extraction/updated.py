import base64

from ocr_tamil.ocr import OCR
import pandas as pd
import logging
import json
import os
import re
import datetime
from os.path import splitext, join
import cv2
# import fitz
import pandas as pd
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

from main import db

# local
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

coordinates_dict = {(38, 77, 557, 288): 1, (566, 77, 1084, 288): 2, (1095, 77, 1612, 287): 3, (38, 298, 557, 508): 4,
                    (566, 298, 1084, 508): 5, (1094, 298, 1613, 508): 6, (38, 518, 557, 728): 7,
                    (566, 518, 1084, 728): 8,
                    (1094, 518, 1613, 728): 9, (38, 738, 557, 948): 10, (566, 738, 1085, 948): 11,
                    (1094, 738, 1613, 948): 12,
                    (38, 959, 557, 1169): 13, (566, 959, 1085, 1169): 14, (1094, 959, 1613, 1169): 15,
                    (38, 1179, 557, 1389): 16,
                    (566, 1179, 1084, 1389): 17, (1094, 1179, 1613, 1389): 18, (38, 1399, 557, 1609): 19,
                    (566, 1399, 1085, 1609): 20,
                    (1094, 1400, 1613, 1609): 21, (38, 1619, 557, 1830): 22, (566, 1619, 1084, 1830): 23,
                    (1095, 1620, 1612, 1830): 24,
                    (38, 1839, 557, 2050): 25, (566, 1839, 1084, 2050): 26, (1095, 1840, 1613, 2050): 27,
                    (38, 2060, 557, 2271): 28,
                    (566, 2060, 1084, 2271): 29, (1095, 2060, 1612, 2270): 30}

coordinates = [(38, 77, 557, 288), (566, 77, 1084, 288), (1095, 77, 1612, 287), (38, 298, 557, 508),
               (566, 298, 1084, 508),
               (1094, 298, 1613, 508), (38, 518, 557, 728), (566, 518, 1084, 728), (1094, 518, 1613, 728),
               (38, 738, 557, 948),
               (566, 738, 1085, 948), (1094, 738, 1613, 948), (38, 959, 557, 1169), (566, 959, 1085, 1169),
               (1094, 959, 1613, 1169),
               (38, 1179, 557, 1389), (566, 1179, 1084, 1389), (1094, 1179, 1613, 1389), (38, 1399, 557, 1609),
               (566, 1399, 1085, 1609),
               (1094, 1400, 1613, 1609), (38, 1619, 557, 1830), (566, 1619, 1084, 1830), (1095, 1620, 1612, 1830),
               (38, 1839, 557, 2050),
               (566, 1839, 1084, 2050), (1095, 1840, 1613, 2050), (38, 2060, 557, 2271), (566, 2060, 1084, 2271),
               (1095, 2060, 1612, 2270)]

""" **************************** Conversion of pages to images *************************"""


def convert_pdf_to_images(pdf_paths, output_folder):
    try:
        for pdf_path in pdf_paths:
            pdf_filename = os.path.basename(pdf_path)
            pdf_name = os.path.splitext(pdf_filename)[0]
            pdf_output_folder = os.path.join(output_folder, pdf_name)

            # Create output folder for this PDF if it doesn't exist
            if not os.path.exists(pdf_output_folder):
                os.makedirs(pdf_output_folder)

            try:
                images = convert_from_path(pdf_path)
            except Exception as e:
                print(f'Error converting PDF "{pdf_path}": {e}')
                continue

            for i, image in enumerate(images, start=1):
                # Adjust the starting page number to 1 (not 0)
                image_filename = f'{str(i).zfill(2)}.jpg'
                image_path = os.path.join(pdf_output_folder, image_filename)
                image.save(image_path, 'JPEG')
                print(f'Saved {image_path}')

            print(f'PDF pages from "{pdf_path}" successfully converted to images and saved in: {pdf_output_folder}')

    except Exception as e:
        print(f'Error: {e}')


pdfs_collection_folder = 'tamil_pdf_collections'
output_folder = 'tamil_pdf_images_folder'
pdf_paths = [os.path.join(pdfs_collection_folder, filename) for filename in os.listdir(pdfs_collection_folder) if
             filename.endswith('.pdf')]

convert_pdf_to_images(pdf_paths, output_folder)

""" *********************** Cropping function ********************** """


def crop_and_save_images(input_for_individual, coordinates, coordinates_dict, output_for_individual):
    try:
        if not os.path.exists(output_for_individual):
            os.makedirs(output_for_individual)

        images_to_skip = 3
        images_to_skip_end = 2

        for root, dirs, files in os.walk(input_for_individual):
            for dir in dirs:
                input_folder_path = os.path.join(input_for_individual, dir)
                output_folder_path = os.path.join(output_for_individual, dir)
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)

                counter = 1
                filenames_sorted = sorted(os.listdir(input_folder_path))
                for filename in filenames_sorted[images_to_skip:-images_to_skip_end]:
                    image_path = os.path.join(input_folder_path, filename)
                    image = cv2.imread(image_path)
                    page_number = str(os.path.splitext(filename)[0])
                    for coord in coordinates:
                        x1, y1, x2, y2 = coord
                        cropped_image = image[y1:y2, x1:x2]
                        if coord in coordinates_dict.keys():
                            page_no = coordinates_dict[coord]
                            output_filename = f"{dir}_{page_number}_{str(page_no).zfill(2)}.jpg"
                            print("output :", output_filename, "%%%%%%")
                            output_path = os.path.join(output_folder_path, output_filename)
                            cv2.imwrite(output_path, cropped_image)
                            print(f'Saved {output_path}')
                            with open(output_path, "rb") as image_file:
                                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

                            data_no = '/'.join(output_filename.split("_")[1:]).strip(".jpg")
                            # print(data)
                            # Insert into MongoDB
                            collection_name = dir  # You can use the subfolder name as the collection name
                            collection = db[collection_name]
                            doc = {
                                "pdf_name": dir,
                                "page_no": page_number,
                                "cropped_image_path": output_path,
                                "c_image": base64_image,
                                "status": "new",
                                "serial_no": None,
                                "data_no": data_no,
                                "name": None,
                                "voter_id": None,
                                "relation": None,
                                "relation_name": None,
                                "house_no": None,
                                "gender": None,
                                "age": None,
                                "created_on": datetime.datetime.now().strftime("%Y-%m-%d")
                            }
                            collection.insert_one(doc)
                    counter += 1
        print('PDF pages successfully cropped and saved')

    except Exception as e:
        print(f'Error cropping images: {e}')


input_for_crop = "tamil_pdf_images_folder"
output_of_crop = "tamil_cropped_images"

# crop_and_save_images(input_for_crop, coordinates, coordinates_dict, output_of_crop)

""" ************************* Extraction function **************************"""


# first page data extraction

def extract_text_from_first_page(images_folder, output_path):
    try:
        ocr = OCR(detect=True)

        for root, dirs, files in os.walk(images_folder):
            for directory in dirs:
                input_folder_path = os.path.join(images_folder, directory)
                output_folder_path = os.path.join(output_path, directory)
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)

                for filename in os.listdir(input_folder_path):
                    if filename == "01.jpg":
                        # Construct the full path to the image
                        image_path = os.path.join(input_folder_path, filename)

                        try:
                            # Perform OCR on the image
                            extracted_text_list = ocr.predict(image_path)
                            extracted_text = ' '.join(extracted_text_list)  # Join the list of strings into one

                            # Write the extracted text to a text file if it's not empty
                            if extracted_text:
                                output_file_path = os.path.join(output_folder_path,
                                                                f"{os.path.splitext(filename)[0]}_{directory}.txt")
                                with open(output_file_path, "w", encoding="utf-8") as text_file:
                                    text_file.write(extracted_text)
                                print("Text extracted and saved:", output_file_path)
                            else:
                                print("No text extracted from", image_path)

                        except Exception as e:
                            print(f"Error processing image {image_path}: {e}")

    except Exception as e:
        print(f'Error: {e}')


images_folder = "tamil_pdf_images_folder"
output_path = "first_pages_data_collection"

# extract_text_from_first_page(images_folder, output_path)


# first page data processing

def process_text_files(first_page_path):
    data_to_insert = []  # Initialize a list to store data for insertion

    for root, dirs, files in os.walk(first_page_path):
        for file in files:
            if file.endswith(".txt"):  # Process only text files
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    page_one_text = f.read()
                    detail = page_one_text.split(" ")
                    data = file.split(".")[0]
                    pdf_name = data.split('_')[1]
                    print(pdf_name, "%%%%%&U**((()")
                    # image_path = file
                    image_path = os.path.join(root, "01.jpg")

                    part_no = ""
                    village = ""
                    ward = ""
                    post_office = ""
                    police_station = ""
                    block = ""
                    subdivision = ""
                    division = ""
                    district = ""
                    pin_code = ""

                    found_first_occurrence = False
                    first_occurrence = False
                    for item in detail:
                        item = item.strip(':')
                        if "நகரம்/கிராமம்" in item or "நகரம்கிராமம்" in item:
                            village_index = detail.index(item) + 1
                            if village_index < len(detail):
                                village = detail[village_index]
                            else:
                                village = None

                        if "அலுவலகம்" in item:
                            post_office = ' '.join(detail[detail.index(item) + 1: detail.index("காவல்")]).replace("க்","").replace("டி", "")

                        if "நிலையம்" in item:
                            station_index = detail.index(item) + 1
                            if station_index + 2 < len(detail):
                                police_station = ' '.join(detail[station_index:station_index + 2])
                            else:
                                police_station = None

                        elif "பஞ்சாயத்து" in item:
                            block_index = detail.index(item) + 1
                            if block_index < len(detail):
                                block = detail[block_index].replace("க்", "")
                            else:
                                block = None

                        elif "கோட்டம்" in item:
                            division = detail[detail.index(item) + 2]

                        elif "மாவட்டம்" in item:
                            district = detail[detail.index(item) + 1: detail.index("குறியீட்டு")][0]

                        elif "வட்டம்" in item:
                            subdivision = detail[detail.index(item) + 1]
                        elif "குறியீட்டு" in item:
                            pin_code = detail[detail.index(item) + 3]

                        if "பாகம்" in item:
                            if found_first_occurrence:
                                continue
                            item_index = detail.index(item)
                            part_no = detail[item_index + 2].strip(":")
                            found_first_occurrence = True
                        if "சட்டமன்றத்" in item:
                            if first_occurrence:
                                continue
                            if "பாகம்" not in detail:
                                name_of_assembly_constituency = ""
                            else:
                                item_index = detail.index(item)
                                if "பாகம்" in detail[item_index:]:
                                    assembly_constituency = ' '.join(
                                        detail[item_index + 9: detail.index("பாகம்")])
                                    first_occurrence = True
                                else:
                                    assembly_constituency = ""
                    f_image_path = file
                    data_dict = {
                        "pdf_name": pdf_name,
                        "first_page_path": image_path,
                        "பாகம் எண்": part_no,
                        "நகரம் / கிராமம்": village,
                        "வார்டு": ward,
                        "அஞ்சல் அலுவலகம்": post_office,
                        "காவல் நிலையம்": police_station,
                        "பஞ்சாயத்து": block,
                        "வட்டம்": subdivision,
                        "கோட்டம்": division,
                        "மாவட்டம்": district,
                        "மாநிலம்": "தமிழ்நாடு",
                        "சட்டமன்ற தொகுதி": assembly_constituency,
                        "அஞ்சல் குறியீட்டு எண்": pin_code,
                        # "status": status,
                        "text_path": f_image_path,
                        "created_on": datetime.datetime.now(),
                        "fp_image": image_path
                    }
                    data_to_insert.append(data_dict)  # Add the data_dict to the list for insertion

    mapping = {
        "பாகம் எண்": "part_no",
        "நகரம் / கிராமம்": "village",
        "வார்டு": "ward",
        "அஞ்சல் அலுவலகம்": "post_office",
        "காவல் நிலையம்": "police_station",
        "பஞ்சாயத்து": "block",
        "வட்டம்": "subdivision",
        "கோட்டம்": "division",
        "மாவட்டம்": "district",
        "அஞ்சல் குறியீட்டு எண்": "pin_code",
        "pdf_name": "pdf_name",
        "மாநிலம்": "state",
        "சட்டமன்ற தொகுதி": "assembly_constituency"
    }
    # Rename keys for all dictionaries in the list
    data_to_insert = [{mapping.get(old_key, old_key): value for old_key, value in data.items()} for data in
                      data_to_insert]
    collection_name = "first_page_data"  # You can use the subfolder name as the collection name
    collection = db[collection_name]
    collection.insert_many(data_to_insert)  # Use insert_many to insert all data_dict documents at once

    print(f"{len(data_to_insert)} data entries saved to MongoDB collection '{collection_name}'")
    print(f"{data_to_insert} data entries saved to MongoDB collection '{collection_name}'")
    return data_dict


first_page = "first_pages_data_collection"
# process_text_files(first_page)


# Voter list data Extraction

def extract_text_from_voter_list(images_path, output_folder):
    try:
        ocr = OCR(detect=True)
        os.makedirs(output_folder, exist_ok=True)

        limit = 800
        for root, dirs, files in os.walk(images_path):
            for directory in dirs:
                input_path = os.path.join(images_path, directory)
                output_path = os.path.join(output_folder, directory)
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                counter = 0

                for filename in sorted(os.listdir(input_path)):
                    if filename.endswith('.jpg'):
                        image_path = os.path.join(input_path, filename)
                        try:
                            extracted_text = ocr.predict(image_path)
                            print(extracted_text)

                            # Convert extracted_text to string if it's a list
                            if isinstance(extracted_text, list):
                                extracted_text = ' '.join(extracted_text)

                            if extracted_text:
                                if counter >= limit:
                                    print(f"Limit reached for {directory}. Skipping further entries.")
                                    break

                                output_file_path = os.path.join(output_path,
                                                                f"{os.path.splitext(filename)[0]}_{str(counter + 1).zfill(2)}.txt")
                                with open(output_file_path, "w", encoding="utf-8") as text_file:
                                    text_file.write(extracted_text)
                                print(output_file_path)
                                counter += 1
                            else:
                                print(f"{image_path} is empty. Skipping...")
                        except IndexError as e:
                            print(f"Error processing {image_path}: {e}. Skipping...")
                        except Exception as e:
                            logger.info(image_path)
                            print(f"Error processing {image_path}: {e}")

        print("Converted text successfully")

    except Exception as e:
        print(f'Error: {e}')


# Example usage:
images_path = "tamil_cropped_images"
output_folder = "tamil_extracted_data"

# extract_text_from_voter_list(images_path, output_folder)


def extract_data_by_status_new(images_path, output_folder, start_limit):
    try:
        ocr = OCR(detect=True)
        os.makedirs(output_folder, exist_ok=True)

        # Get list of all collections in the database
        collections = db.list_collection_names()

        for collection_name in collections:
            # Query documents with status "new"
            query = {"status": "new"}
            cursor = db[collection_name].find(query)

            # If there are documents with status "new" in this collection
            count = sum(1 for _ in cursor)
            cursor.rewind()  # Reset cursor to the beginning

            if count > 0:
                print(f"Processing collection: {collection_name}")

                # Dictionary to keep track of limit for each folder
                folder_limits = {}

                for document in cursor:
                    cropped_image_path_db = document["cropped_image_path"]

                    for root, dirs, files in os.walk(images_path):
                        for directory in dirs:
                            input_path = os.path.join(images_path, directory)
                            output_path = os.path.join(output_folder, directory)
                            if not os.path.exists(output_path):
                                os.makedirs(output_path)

                            # Get or initialize the limit for this folder
                            folder_limit = folder_limits.get(directory, start_limit)
                            limit = folder_limit

                            for filename in sorted(os.listdir(input_path)):
                                if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                                    image_path = os.path.join(input_path, filename)
                                    try:
                                        if image_path == cropped_image_path_db:
                                            extracted_text = ocr.predict(image_path)
                                            if isinstance(extracted_text, list):
                                                extracted_text = ' '.join(extracted_text)
                                            if extracted_text:
                                                output_file_name = f"{os.path.splitext(filename)[0]}_{limit:02d}.txt"
                                                output_file_path = os.path.join(output_path, output_file_name)
                                                with open(output_file_path, "w", encoding="utf-8") as text_file:
                                                    text_file.write(extracted_text)
                                                print(f"Extracted text saved to: {output_file_path}")
                                                # Increment the limit for the next file
                                                folder_limits[directory] = limit + 1
                                            else:
                                                print(f"{image_path} is empty. Skipping...")
                                    except IndexError as e:
                                        print(f"Error processing {image_path}: {e}. Skipping...")
                                    except Exception as e:
                                        logger.info(image_path)
                                        print(f"Error processing {image_path}: {e}")

        print("Extraction complete.")

    except Exception as e:
        print(f'Error: {e}')


# Example usage:
images_path = "tamil_cropped_images"
output_folder = "tamil_extracted_data"

# Start the limit from 501 for each folder
start_limit = 501

# extract_data_by_status_new(images_path, output_folder, start_limit)


# Extracted data processing
def text_extracter(extracted_folder):
    data_by_subfolder = {}  # Dictionary to store extracted data by subfolder
    result_list = []
    # count = 0
    for root, dirs, files in os.walk(extracted_folder):
        for dir in dirs:
            subfolder_path = os.path.join(root, dir)
            subfolder_data = []  # List to store extracted data from current subfolder
            for filename in os.listdir(subfolder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(subfolder_path, filename)
                    with open(file_path, 'r', encoding="utf-8") as file:
                        extracted_text = file.read()

                    if extracted_text.strip() == '':
                        continue
                    data_dict = {}
                    # global count
                    # count += 1
                    # data_dict["எண்"] = count
                    page = filename.split('.')[0]
                    pdf_name = page.split("_")[0]
                    page_no = page.split("_")[1]
                    data_no = page.split("_")[2]
                    data_dict["பக்க எண்"] = page_no
                    data_dict["pdf_name"] = page.split("_")[0]
                    data_dict["data_no"] = page_no + "/" + data_no
                    # data_dict["created_on"] = datetime.datetime.now().strftime("%Y-%m-%d")

                    serial_no = page.split("_")[3]
                    data_dict["எண்"] = serial_no

                    detail = extracted_text.split()
                    print(detail)

                    missing_voter_ids = []
                    missing_names = []

                    for i, word in enumerate(detail):
                        if word.startswith(
                                ('FM', 'ZB', 'TK', 'CD', 'IX', 'CF', 'TW', 'HN', 'XR', 'SS', 'NU', 'WU', 'AX', 'IBU', 'MPR')):
                            data_dict["வாக்காளர் எண்"] = word
                            break
                    else:
                        print("Voter ID Missing")
                        missing_voter_ids.append(detail)
                    if missing_voter_ids:
                        with open('missing_voter_ids.txt', 'a') as file:
                            for data in missing_voter_ids:
                                file.write(' '.join(data) + '\n')

                    pattern = re.compile(r'(?:பெயர்ஃ|பெயர்)[\s:]*(.*?)(?:[\s:|$])', re.IGNORECASE)
                    detail_str = ' '.join(detail)

                    match = re.search(pattern, detail_str)
                    if match:
                        data_dict["பெயர்"] = match.group(1)
                        print(data_dict["பெயர்"])
                    else:
                        print("Name missing")
                        missing_names.append(detail_str)
                    if missing_names:
                        with open('missing_names.txt', 'a') as file:
                            for data in missing_names:
                                file.write(' '.join(data) + '\n')

                    if "கணவர" in detail:
                        try:
                            # data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("கணவர")])
                            data_dict["Relative"] = "கணவர்"
                            data_dict["உறவுப் பெயர்"] = ''.join(detail[detail.index("கணவர") + 2:detail.index("வீட்டு")])
                        except ValueError:
                            data_dict["பெயர்"] = None

                    if "கணவர்" in detail:
                        # data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("கணவர்")])
                        data_dict["உறவு"] = "கணவர்"
                        data_dict["உறவுப் பெயர்"] = ''.join(
                            detail[
                            detail.index("கணவர்") + 2:detail.index("வீட்டு")]) if "வீட்டு" in detail else ''.join(
                            detail[detail.index("கணவர்") + 2:detail.index("எண்")])

                    if "தந்தையின்" in detail:
                        try:

                            # data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("தந்தையின்")])
                            data_dict["உறவு"] = "தந்தை"
                            data_dict["உறவுப் பெயர்"] = ''.join(
                                detail[detail.index("தந்தையின்") + 2:detail.index(
                                    "வீட்டு")]) if "வீட்டு" in detail else ''.join(
                                detail[detail.index("தந்தையின்") + 2:detail.index("எண்")])
                        except ValueError:
                            data_dict["உறவுப் பெயர்"] = None
                    if "தந்தையின்னிபெ" in detail:
                        # data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("தந்தையின்னிபெ")])
                        data_dict["உறவு"] = "தந்தை"
                        data_dict["உறவுப் பெயர்"] = ''.join(
                            detail[detail.index("தந்தையின்னிபெ") + 2:detail.index(
                                "வீட்டு")]) if "வீட்டு" in detail else ''.join(
                            detail[detail.index("தந்தையின்") + 2:detail.index("எண்")])

                    if "வீட்டு" in detail:
                        try:
                            data_dict["வீட்டு எண்"] = ''.join(detail[detail.index("எண்") + 1:detail.index("Photo")])
                        except ValueError:
                            data_dict["வீட்டு எண்"] = None

                    if "available" in detail:
                        data_dict["பாலினம்"] = ''.join(detail[detail.index("available") - 1])
                    if "வயது" in detail:
                        try:
                            age1 = ' '.join(detail[detail.index("வயது") + 1:detail.index("பாலினம்")])
                            age_parts = age1.split(" ")
                            if len(age_parts) > 1:
                                age = age_parts[1]
                            else:
                                age = age_parts[0]
                            data_dict["வயது"] = age
                        except ValueError:
                            data_dict["வயது"] = None

                    data_dict["text_data"] = extracted_text
                    data_dict["image_path"] = page
                    status = "incomplete"
                    if all(data_dict.get(key) for key in ["பெயர்", "வயது", "வாக்காளர் எண்", "பாலினம்"]):
                        status = "completed"
                    elif any(data_dict.get(key) for key in ["பெயர்", "வயது", "வாக்காளர் எண்", "பாலினம்"]):
                        status = "partially completed"
                    if all(value is None for value in data_dict.values()):
                        status = "failed"
                    data_dict["status"] = status

                    print(data_dict)
                    if bool(data_dict):
                        result_list.append(data_dict)
                        subfolder_data.append(data_dict)

                    mapping = {
                        "பக்க எண்": "page_no",
                        "எண்": "serial_no",
                        "பெயர்": "name",
                        "வாக்காளர் எண்": "voter_id",
                        "உறவு": "relation",
                        "உறவுப் பெயர்": "relation_name",
                        "வயது": "age",
                        "வீட்டு எண்": "house_no",
                        "பாலினம்": "gender",
                        "status": "status"

                    }
                    # Rename keys
                    data_dict = {mapping.get(old_key, old_key): value for old_key, value in data_dict.items()}
                    collection_name = dir  # You can use the subfolder name as the collection name
                    collection = db[collection_name]
                    filter_criteria = {
                        "pdf_name": pdf_name, "page_no": page_no, "data_no": data_dict["data_no"]
                    }
                    data_dict.pop('status', None)

                    update_operation = {
                        "$set": {
                            **data_dict,
                            "status": status
                        }
                    }

                    # Perform the update operation
                    result = collection.update_one(filter_criteria, update_operation, upsert=True)

                    if result.matched_count == 0:
                        print("No document matched the update criteria.")
                    elif result.modified_count > 0:
                        print("Document updated successfully.")
                    else:
                        print("Update operation did not modify any documents.")

                    print(f"Data saved to MongoDB collection '{collection_name}'")

            # Extract first page data
            # output_path = "first_pages_data_collection"
            # first_page_data = process_text_files(output_path)

            # Merge first page data with extracted text data
            # for item in subfolder_data:
            #     item.update(first_page_data)
            data_by_subfolder[dir] = subfolder_data
    return data_by_subfolder


# extracted_folder = "tamil_extracted_data"
# data_by_subfolder = text_extracter(extracted_folder)

"""for subfolder, extracted_data_list in data_by_subfolder.items():
    df = pd.DataFrame(extracted_data_list)
    excel_folder = "output_excel"
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    excel_file = os.path.join(excel_folder, f'{excel_folder}_{subfolder}.xlsx')
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"Excel data saved to '{excel_file}'")"""
