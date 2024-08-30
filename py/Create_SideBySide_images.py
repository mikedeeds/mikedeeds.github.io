# Create_SideBySide_images.py
#
# Takes in two jpeg images, places them into a single side by side image, and saves them as a new .jpg image.

from PIL import Image

def merge_images(left_image_path, right_image_path, output_path):
    # Open the images
    imageL = Image.open(left_image_path)
    imageR = Image.open(right_image_path)
    
    # Get dimensions of each image
    widthL, heightL = imageL.size
    widthR, heightR = imageR.size
    
    # Determine the dimensions of the merged image
    total_width = widthL + widthR
    max_height = max(heightL, heightR)
    
    # Create a new blank image with the total width and the max height
    merged_image = Image.new('RGB', (total_width, max_height))
    
    # Paste imageL and imageR into the merged image
    merged_image.paste(imageL, (0, 0))
    merged_image.paste(imageR, (widthL, 0))
    
    # Save the merged image
    merged_image.save(output_path, 'JPEG')
    print(f"Merged image saved as {output_path}")

# Example usage

merge_images('../2019/textures/L.jpg', '../2019/textures/R.jpg', '../images/LRimage.jpg')