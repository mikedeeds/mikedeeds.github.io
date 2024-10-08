# Create_SideBySide_images.py
#
# Takes in two jpeg images, places them into a single side by side image, and saves them as a new .jpg image.

from PIL import Image, ImageFilter
import cv2
import numpy as np


def align_and_merge_stereoscopic_images(left_image_pil, right_image_pil):

    # convert images from PIL to np:
    #left_image = np.array(left_image_pil)
    #right_image = np.array(right_image_pil)
    left_image = cv2.cvtColor(np.array(left_image_pil), cv2.COLOR_RGB2BGR)
    right_image = cv2.cvtColor(np.array(right_image_pil), cv2.COLOR_RGB2BGR)

    # Convert images to grayscale
    left_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
    right_gray = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)

    # Detect ORB keypoints and descriptors
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(left_gray, None)
    kp2, des2 = orb.detectAndCompute(right_gray, None)

    # Match descriptors using the BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    # Sort matches by distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Extract location of good matches
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Find homography matrix to align images
    h_matrix, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC, 5.0)

    # Use the homography matrix to warp the right image to align with the left image
    height, width, _ = left_image.shape
    aligned_right_image = cv2.warpPerspective(right_image, h_matrix, (width, height))

    # Resize the aligned images to ensure they have the same resolution
    left_resized = cv2.resize(left_image, (width, height))
    right_resized = cv2.resize(aligned_right_image, (width, height))

    # Convert the images back to PIL format for saving as JPEG
    left_final = Image.fromarray(cv2.cvtColor(left_resized, cv2.COLOR_BGR2RGB))
    right_final = Image.fromarray(cv2.cvtColor(right_resized, cv2.COLOR_BGR2RGB))

    # Create a new image that will hold the side by side result
    total_width = left_final.width + right_final.width
    max_height = max(left_final.height, right_final.height)
    side_by_side_image = Image.new('RGB', (total_width, max_height))

    # Paste the images side by side
    side_by_side_image.paste(left_final, (0, 0))
    side_by_side_image.paste(right_final, (left_final.width, 0))
    return side_by_side_image

def denoise_and_sharpen(input_image):

    # Convert the image to a numpy array (needed for OpenCV operations)
    image_np = np.array(input_image)

    # Step 1: Denoising using Non-Local Means Denoising (good for grainy noise)
    denoised_image = cv2.fastNlMeansDenoisingColored(image_np, None, 10, 10, 7, 21)

    # Step 2: Convert to LAB color space to enhance color contrast
    lab_image = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2LAB)

    # Split LAB image into L, A, and B channels
    l_channel, a_channel, b_channel = cv2.split(lab_image)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L-channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    # Merge the CLAHE enhanced L-channel with the A and B channels
    merged_lab = cv2.merge((cl, a_channel, b_channel))

    # Convert back to BGR color space
    enhanced_image = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

    # Step 3: Sharpening using a custom kernel
    sharpen_kernel = np.array([[-1, -1, -1],
                               [-1, 9, -1],
                               [-1, -1, -1]])
    sharpened_image = cv2.filter2D(enhanced_image, -1, sharpen_kernel)

    # Convert the result back to a PIL image
    clean_image = Image.fromarray(sharpened_image)
    return clean_image

def merge_images(left_image_path, right_image_path, output_path, clean_up_image):
    # Open the images
    imageL = Image.open(left_image_path)
    imageR = Image.open(right_image_path)

    if clean_up_image:
        imageL = denoise_and_sharpen(imageL)
        imageR = denoise_and_sharpen(imageR)

    if False:
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

    if True:
        merged_image = align_and_merge_stereoscopic_images(imageL, imageR)
    
    # Save the merged image
    merged_image.save(output_path, 'JPEG')
    print(f"Merged image saved as {output_path}")

# Example usage

if False:
    merge_images('../2019/textures/L.jpg', '../2019/textures/R.jpg', '../images/LRimage.jpg', False)
    merge_images('../2019/textures/scan7_l.jpg', '../2019/textures/scan7_r.jpg', '../images/wa_1964a_lr.jpg', False)
    merge_images('../2019/textures/scan8_l.jpg', '../2019/textures/scan8_r.jpg', '../images/wa_1964b_lr.jpg', False)
    merge_images('../2019/textures/scan9_l.jpg', '../2019/textures/scan9_r.jpg', '../images/wa_1964c_lr.jpg', False)
    merge_images('../2019/textures/scan7_l.jpg', '../2019/textures/scan7_r.jpg', '../images/wa_1964a_clean_lr.jpg', True)
    merge_images('../2019/textures/scan8_l.jpg', '../2019/textures/scan8_r.jpg', '../images/wa_1964b_clean_lr.jpg', True)
    merge_images('../2019/textures/scan9_l.jpg', '../2019/textures/scan9_r.jpg', '../images/wa_1964c_clean_lr.jpg', True)

if True:
    merge_images('../2019/textures/scan7_l.jpg', '../2019/textures/scan7_r.jpg', '../images/wa_1964a_aligned_lr.jpg', False)
    merge_images('../2019/textures/scan8_l.jpg', '../2019/textures/scan8_r.jpg', '../images/wa_1964b_aligned_lr.jpg', False)
    merge_images('../2019/textures/scan9_l.jpg', '../2019/textures/scan9_r.jpg', '../images/wa_1964c_aligned_lr.jpg', False)
