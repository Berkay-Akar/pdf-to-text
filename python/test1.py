import cv2
import numpy as np
import pytesseract
from pytesseract import Output

# Function to determine if a checkbox is checked
def is_checked(checkbox_area):
    # Calculate the percentage of white pixels in the area
    white_pixels = cv2.countNonZero(checkbox_area)
    total_pixels = checkbox_area.size
    white_ratio = white_pixels / total_pixels

    # Consider it checked if the white_ratio is below a threshold (e.g., less than 30% white pixels)
    return white_ratio < 0.3

# Load the image
image_path = '/Users/univenn/Documents/aws-textractor/test.png'
image = cv2.imread(image_path)

# Convert image to grayscale and apply adaptive thresholding
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours to detect checkboxes
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Dictionary to hold checkbox positions and their checked status
checkboxes = {}

# Analyze each contour to determine if it's a checkbox
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if 20 < w < 40 and 20 < h < 40:  # Size range for checkboxes
        checkbox_area = thresh[y:y+h, x:x+w]
        checked = is_checked(checkbox_area)
        checkboxes[(x, y)] = checked

# Use PyTesseract to extract text data with bounding boxes
custom_config = r'--oem 3 --psm 6'
text_data = pytesseract.image_to_data(gray, config=custom_config, output_type=Output.DICT)

# This list will hold tuples of the form (line_num, text, checkbox_yes_checked, checkbox_no_checked)
entries = []

# Process the text data to associate text with checkboxes
for i, text in enumerate(text_data['text']):
    if int(text_data['conf'][i]) > 60:  # Confidence threshold
        x, y, w, h = (text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i])
        line_num = text_data['line_num'][i]

        # Find checkboxes on the same line as the text
        line_checkboxes = {pos: status for pos, status in checkboxes.items() if abs(pos[1] - y) < h}

        # Sort checkboxes by x position (horizontal order)
        sorted_checkboxes = sorted(line_checkboxes.items(), key=lambda item: item[0][0])

        # Associate the text with the appropriate checkbox statuses
        if len(sorted_checkboxes) >= 2:
            # Assuming the first checkbox is 'Yes' and the second is 'No'
            checkbox_yes_checked = 'Yes' if sorted_checkboxes[0][1] else 'No'
            checkbox_no_checked = 'Yes' if sorted_checkboxes[1][1] else 'No'

            entries.append((line_num, text, checkbox_yes_checked, checkbox_no_checked))
        else:
            # Handle cases where not enough checkboxes are found
            print(f"Not enough checkboxes on line {line_num} for text: {text}")

# Now, we'll print the entries in a structured way
for entry in entries:
    line_num, text, checkbox_yes, checkbox_no = entry
    print(f"Line {line_num}: {text} | Checkbox Yes: {checkbox_yes} | Checkbox No: {checkbox_no}")

# Save any remaining unchecked checkboxes for manual review
unchecked_checkboxes = {pos: status for pos, status in checkboxes.items() if not status}
for pos, status in unchecked_checkboxes.items():
    print(f"Unchecked checkbox at position {pos} may need manual review.")