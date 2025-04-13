# WatermarkPro - Intelligent Image Watermarking System

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Features](#features)
4. [Installation & Setup](#installation--setup)
5. [Technical Implementation](#technical-implementation)
6. [API Documentation](#api-documentation)
7. [Security](#security)
8. [Testing & Quality Assurance](#testing--quality-assurance)
9. [Performance](#performance)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [Support & Resources](#support--resources)
13. [License](#license)

## Overview

WatermarkPro is a web application that enables users to add and remove watermarks from images using advanced computer vision techniques. Built with React, Flask, and MongoDB, it provides an intuitive interface for image watermarking management.

### Key Features
- Text watermark application with customizable properties
- AI-powered watermark removal
- Side-by-side comparison view
- Secure image storage
- User authentication and management

## Core Concepts

### 1. Digital Image Processing Fundamentals

#### Image Structure
- Images are matrices of pixels: `height × width × channels`
- RGB images have 3 channels (Red, Green, Blue)
- Each pixel value ranges from 0-255
- Alpha channel (transparency) ranges from 0.0 to 1.0

```python
# RGB Image representation
image = [
    [[R,G,B], [R,G,B], ...],  # Row 1
    [[R,G,B], [R,G,B], ...],  # Row 2
    # ... more rows
]
```

### 2. Watermarking Theory

#### Alpha Blending
The core formula for watermark application:

1. **Alpha Blending Formula**
   ```
   Result = (α × Watermark) + ((1 - α) × Original)
   where α is opacity (0.0 to 1.0)
   ```

2. **Text Rendering Process**
   - Convert text to bitmap
   - Apply transformations (rotation, scaling)
   - Blend with original image

### 2. Watermark Removal Theory

The removal process uses these key concepts:

1. **Watermark Detection**
   - Edge detection algorithms
   - Texture analysis
   - Color distribution analysis

2. **Image Inpainting**
   - Analyze surrounding pixels
   - Reconstruct damaged/watermarked areas
   - Use neighboring pixel information

## Technical Implementation

### Project Structure

## Features

### User Features
- Add text watermarks with customizable:
  - Font size, opacity, position
  - Angle and pattern (single/repeated)
- Remove watermarks using AI-powered detection
- Side-by-side comparison view
- Secure image storage and management
- User authentication and profile management

### Technical Features
- React-based responsive frontend
- Flask RESTful API backend
- MongoDB database integration
- Advanced image processing with OpenCV
- JWT authentication system

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB 4.4+
- Git

### Backend Setup
```bash
# Clone repository
git clone https://github.com/yourusername/watermarkpro.git
cd watermarkpro

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run backend
python backend/app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Technical Implementation

### 1. Watermark Application Process

First, let's understand the process, then look at the code:

1. **Image Preparation**
   - Load image into memory
   - Convert color space if needed
   - Create alpha channel for transparency

2. **Text Preparation**
   - Calculate text dimensions
   - Create text mask
   - Apply anti-aliasing

3. **Blending Process**
   - Position text on image
   - Apply opacity
   - Handle edge cases

Now, the implementation:

```python
def add_text_watermark(image_path, text, options):
    """
    Add text watermark to image with customizable options.
    
    Process:
    1. Load and prepare image
    2. Create text mask
    3. Apply transformations
    4. Blend watermark
    """
    # Load image
    image = cv2.imread(image_path)
    
    # Create text mask
    mask = np.zeros_like(image)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Position and render text
    text_size = cv2.getTextSize(text, font, options['font_size'], 2)[0]
    x = (image.shape[1] - text_size[0]) // 2
    y = (image.shape[0] + text_size[1]) // 2
    
    cv2.putText(mask, text, (x, y), font, 
                options['font_size'], (255,255,255), 2)
    
    # Apply transformations
    if options['angle']:
        matrix = cv2.getRotationMatrix2D(
            (image.shape[1]/2, image.shape[0]/2),
            options['angle'], 1.0)
        mask = cv2.warpAffine(mask, matrix, 
                             (image.shape[1], image.shape[0]))
    
    # Blend images
    result = cv2.addWeighted(
        image, 1 - options['opacity'],
        mask, options['opacity'], 0)
    
    return result, mask
```

### 2. Watermark Removal Process

Understanding the removal process:

1. **Detection Phase**
   - Convert to grayscale
   - Apply adaptive thresholding
   - Find potential watermark regions

2. **Mask Refinement**
   - Clean noise
   - Connect components
   - Expand mask slightly

3. **Inpainting**
   - Apply algorithm to masked regions
   - Blend with original
   - Post-process results

Implementation:

```python
def remove_watermark(image_path, mask_path=None):
    """
    Remove watermark from image using detection or provided mask.
    
    Process:
    1. Detect watermark or use mask
    2. Refine mask
    3. Apply inpainting
    """
    # Load image
    image = cv2.imread(image_path)
    
    if mask_path is None:
        # Detect watermark
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2)
        mask = thresh
    else:
        mask = cv2.imread(mask_path, 0)
    
    # Refine mask
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    # Apply inpainting
    result = cv2.inpaint(
        image, mask, 3,
        cv2.INPAINT_TELEA)
    
    return result
```

### 3. Database Schema

```javascript
// Users Collection
{
    _id: ObjectId,
    email: String,
    password_hash: String,
    created_at: DateTime,
    updated_at: DateTime
}

// Images Collection
{
    _id: ObjectId,
    user_id: ObjectId,
    original_filename: String,
    stored_filename: String,
    watermark_text: String,
    watermark_opacity: Float,
    watermark_angle: Float,
    mask_filename: String,
    created_at: DateTime
}
```

## API Documentation

### Authentication Endpoints

```http
POST /api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword"
}

Response: {
    "message": "User registered successfully",
    "user_id": "user_id_here"
}
```

```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword"
}

Response: {
    "access_token": "jwt_token_here",
    "user": {
        "id": "user_id",
        "email": "user@example.com"
    }
}
```

### Image Endpoints

```http
POST /api/watermark/add
Content-Type: multipart/form-data

Parameters:
- file: Image file
- watermark_text: String
- opacity: Float (0.0-1.0)
- angle: Float (degrees)
- position_x: Int (optional)
- position_y: Int (optional)

Response: {
    "image_id": "image_id_here",
    "original_url": "url_to_original",
    "watermarked_url": "url_to_watermarked",
    "comparison_url": "url_to_comparison"
}
```

```http
GET /api/images
Authorization: Bearer <token>

Response: {
    "images": [
        {
            "id": "image_id",
            "original_filename": "example.jpg",
            "watermark_text": "Copyright 2024",
            "created_at": "2024-01-01T00:00:00Z",
            "urls": {
                "original": "url_to_original",
                "watermarked": "url_to_watermarked",
                "comparison": "url_to_comparison"
            }
        }
    ]
}

## Security

## Testing & Quality Assurance

## Performance

## Troubleshooting

## Contributing

## Support & Resources

## License

