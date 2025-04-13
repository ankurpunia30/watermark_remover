import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import uuid
import math
from flask import current_app

def generate_unique_filename(original_filename):
    """Generate a unique filename with timestamp and UUID"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(original_filename)[1]
    return f"{timestamp}_{unique_id}{ext}"

def get_default_font(size=40):
    """Get a default font, trying system fonts first then falling back to default"""
    try:
        return ImageFont.truetype("arialbd.ttf", size)  # Default Windows font
    except OSError:
        try:
            return ImageFont.truetype("Arial.ttf", size)  # Try another common name
        except OSError:
            return ImageFont.load_default()  # Fallback to a basic font

def create_watermark_mask(text, width, height, size=None, opacity=128, angle=30):
    """
    Generates a watermark mask with the specified text.

    Args:
        text (str): Text to be used in the watermark
        width (int): Width of the watermark mask
        height (int): Height of the watermark mask
        size (int): Font size for watermark text (calculated from dimensions if None)
        opacity (int): Opacity of the watermark (0-255)
        angle (int): Rotation angle of the text
    """
    # Calculate size based on image dimensions if not provided
    if size is None:
        if width > height:
            size = math.floor((width / 100) * 3.5)
        else:
            size = math.floor((height / 100) * 3.5)

    # Create transparent image for watermark
    watermark = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    font = get_default_font(size)

    # Define step size for repeating watermark
    step_x, step_y = size * 10, size * 3

    # Create repeating pattern
    for y in range(0, height, int(step_y)):
        for x in range(0, width, int(step_x)):
            text_img = Image.new("RGBA", (int(step_x), int(step_y)), (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0, 0), text, font=font, fill=(128, 128, 128, opacity))

            rotated = text_img.rotate(angle, expand=True)
            watermark.paste(rotated, (x, y), rotated)

    return watermark

def add_text_watermark(image_path, text, position='center', opacity=0.5, pattern='repeat', spacing=100, angle=30, font_size=None):
    """
    Add text watermark to image with various pattern options.
    Returns the watermarked image and mask for removal.
    """
    try:
        # Load and convert image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size

        # Create watermark mask
        watermark = create_watermark_mask(
            text=text,
            width=width,
            height=height,
            size=font_size,
            opacity=int(opacity * 255),
            angle=angle
        )

        # Create mask for removal
        mask = watermark.convert("L")
        
        # Composite watermark onto image
        watermarked = Image.alpha_composite(img, watermark)
        
        # Convert to BGR for OpenCV compatibility
        watermarked_cv = cv2.cvtColor(np.array(watermarked.convert('RGB')), cv2.COLOR_RGB2BGR)
        mask_cv = np.array(mask)

        return watermarked_cv, mask_cv

    except Exception as e:
        current_app.logger.error(f"Error in add_text_watermark: {str(e)}")
        raise

def detect_watermark(image_path):
    """Detect watermark in image using adaptive thresholding"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Remove noise
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    return mask

def extract_watermark_features(mask):
    """Extract features from watermark mask for matching"""
    # Calculate histogram
    hist = cv2.calcHist([mask], [0], None, [256], [0, 256])
    
    # Calculate other features (e.g., contours, moments)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        moments = cv2.moments(contours[0])
    else:
        moments = {}
    
    return {
        'histogram': hist.flatten().tolist(),
        'moments': {str(k): float(v) for k, v in moments.items()}
    }

def remove_watermark(image_path, mask_path=None):
    """
    Remove watermark using inpainting or provided mask
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Failed to load image")

        if mask_path:
            # Use provided mask
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                raise ValueError("Failed to load mask")

            # Ensure mask matches image dimensions
            if mask.shape != img.shape[:2]:
                mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
        else:
            # Detect watermark
            mask = detect_watermark(image_path)

        # Convert mask to binary
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_not(mask)

        # Apply inpainting
        result = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        return result

    except Exception as e:
        current_app.logger.error(f"Error in remove_watermark: {str(e)}")
        raise

def save_processed_image(image, filename, folder):
    """Save processed image to file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    cv2.imwrite(filepath, image)
    return filepath

def save_mask(mask, filename, folder):
    """Save mask to file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    cv2.imwrite(filepath, mask)
    return filepath

def create_comparison_image(original_path, watermarked_path, removed_path=None):
    """
    Creates a side-by-side comparison of original, watermarked, and optionally removed watermark images.
    Returns a single image with all versions for comparison.
    """
    try:
        # Read images
        original = cv2.imread(original_path)
        watermarked = cv2.imread(watermarked_path)
        
        # Calculate target size (maintain aspect ratio)
        target_height = 500
        aspect_ratio = original.shape[1] / original.shape[0]
        target_width = int(target_height * aspect_ratio)
        
        # Resize images
        original_resized = cv2.resize(original, (target_width, target_height))
        watermarked_resized = cv2.resize(watermarked, (target_width, target_height))
        
        if removed_path and os.path.exists(removed_path):
            removed = cv2.imread(removed_path)
            removed_resized = cv2.resize(removed, (target_width, target_height))
            # Create canvas for three images
            comparison = np.zeros((target_height, target_width * 3 + 20, 3), dtype=np.uint8)
            # Add images
            comparison[:, :target_width] = original_resized
            comparison[:, target_width + 10:target_width * 2 + 10] = watermarked_resized
            comparison[:, target_width * 2 + 20:] = removed_resized
            # Add labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(comparison, 'Original', (10, 30), font, 1, (255, 255, 255), 2)
            cv2.putText(comparison, 'Watermarked', (target_width + 20, 30), font, 1, (255, 255, 255), 2)
            cv2.putText(comparison, 'Removed', (target_width * 2 + 30, 30), font, 1, (255, 255, 255), 2)
        else:
            # Create canvas for two images
            comparison = np.zeros((target_height, target_width * 2 + 10, 3), dtype=np.uint8)
            # Add images
            comparison[:, :target_width] = original_resized
            comparison[:, target_width + 10:] = watermarked_resized
            # Add labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(comparison, 'Original', (10, 30), font, 1, (255, 255, 255), 2)
            cv2.putText(comparison, 'Watermarked', (target_width + 20, 30), font, 1, (255, 255, 255), 2)
        
        return comparison
        
    except Exception as e:
        current_app.logger.error(f"Error creating comparison: {str(e)}")
        raise

def save_comparison(comparison_image, original_filename, folder):
    """Save comparison image with a unique filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    comparison_filename = f"comparison_{timestamp}_{unique_id}_{original_filename}"
    
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    filepath = os.path.join(folder, comparison_filename)
    cv2.imwrite(filepath, comparison_image)
    return comparison_filename 