import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\2690360\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Load the image using cv2.imread to get a NumPy array
img_path = r"project\img\dialogueItems\drinks\DrinkNormalDialogue.png"
img = cv2.imread(img_path)

# Ensure the image was loaded successfully
if img is None:
    print(f"Failed to load image from {img_path}")
else:
    # Make a new copy of the original image for processing
    img_copy = img.copy()

    # Upscale the image
    upscaled = cv2.resize(img_copy, None, fx=20, fy=20, interpolation=cv2.INTER_LINEAR)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(upscaled, (5, 5), 0)

    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(blurred, None, 10, 10, 7, 21)

    # Convert to black and white
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    _, black_and_white = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR settings
    custom_config = r'--oem 3 --psm 6 -l eng'
    text = pytesseract.image_to_string(black_and_white, config=custom_config)
    print(text)

    # Draw rectangles around detected letters
    h, w = black_and_white.shape
    boxes = pytesseract.image_to_boxes(black_and_white, config=custom_config)
    for b in boxes.splitlines():
        b = b.split(' ')
        upscaled = cv2.rectangle(upscaled, (int(b[1])*2, h*2 - int(b[2])*2), (int(b[3])*2, h*2 - int(b[4])*2), (0, 255, 0), 2)

    # Save the processed image with rectangles
    output_path_with_boxes = 'processed_image_with_boxes.png'
    cv2.imwrite(output_path_with_boxes, upscaled)
    print(f"Processed image with detected letters saved to {output_path_with_boxes}")