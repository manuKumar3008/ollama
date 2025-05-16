from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

image = Image.open('C:Users/mkumar/OneDrive/Pictures/Screenshots/school.webp')
text = pytesseract.image_to_string(image)
print("Extracted Text:\n", text)
