import cv2
import numpy as np

def merge_images(image_path_1, image_path_2, mask_path, save_path):
    print('image_path_1:', image_path_1)
    print('image_path_2:', image_path_2)
    print('mask_path:', mask_path)
    print('save_path:', save_path)
    # Load the images
    initial_image = cv2.imread(image_path_1)
    generated_image = cv2.imread(image_path_2)
    mask_image = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    # Ensure all images are the same size
    initial_image = cv2.resize(initial_image, (generated_image.shape[1], generated_image.shape[0]))
    mask_image = cv2.resize(mask_image, (generated_image.shape[1], generated_image.shape[0]))

    # Normalize the mask to be in the range of [0, 1] for blending
    mask_normalized = mask_image / 255.0
    inverse_mask_normalized = 1.0 - mask_normalized

    # Ensure mask arrays have three channels to match the images' dimensions
    mask_normalized = cv2.merge([mask_normalized, mask_normalized, mask_normalized])
    inverse_mask_normalized = cv2.merge([inverse_mask_normalized, inverse_mask_normalized, inverse_mask_normalized])

    # Blend the images using the masks
    foreground = generated_image * mask_normalized
    background = initial_image * inverse_mask_normalized
    merged_image = cv2.add(foreground, background)

    # Save
    cv2.imwrite(save_path, merged_image)
