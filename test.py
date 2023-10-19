import cv2
import numpy as np


def unrotate_image(image, angle_degrees):

    # Calculate the reverse angle
    reverse_angle_degrees = -angle_degrees
    rows, cols = image.shape[:2]
    
    # Get the rotation matrix for the reverse angle
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), reverse_angle_degrees, 1)
    
    # Apply the reverse rotation
    unrotated_image = cv2.warpAffine(image, M, (cols, rows))
    
    return unrotated_image

def unrotate_image_unknown_angle(image):
    best_unrotated_image = None
    best_quality = float('-inf')
    
    for angle in range(-45, 46, 1):  # Search over a range of angles from -45 to 45 degrees
        unrotated_image = unrotate_image(image, angle)
        quality = measure_image_quality(unrotated_image)
        
        if quality > best_quality:
            best_quality = quality
            best_unrotated_image = unrotated_image
    
    return best_unrotated_image

def measure_image_quality(image):
    # Implement a quality metric here (e.g., image entropy, edge detection, feature matching)
    # The metric depends on the specific problem and what you consider "quality."

    # Example: Calculate image entropy
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    hist /= hist.sum()
    entropy = -np.sum(hist * np.log2(hist + np.finfo(float).eps))
    return entropy

# Example usage:
input_image = cv2.imread('rotated_image.jpg')  # Replace with your rotated image file path
unrotated_image = unrotate_image_unknown_angle(input_image)

# Display the rotated and unrotated images
cv2.imshow('Rotated Image', input_image)
cv2.imshow('Unrotated Image', unrotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
