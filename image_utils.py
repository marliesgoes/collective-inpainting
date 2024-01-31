import cv2

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

    # Normalize and threshold the mask to ensure it's binary
    _, mask_image = cv2.threshold(mask_image, 128, 255, cv2.THRESH_BINARY)

    # Create an inverse mask
    inverse_mask = 255 - mask_image

    # Use the mask to take regions from the generated image and background from the initial image
    foreground = cv2.bitwise_and(generated_image, generated_image, mask=mask_image)
    background = cv2.bitwise_and(initial_image, initial_image, mask=inverse_mask)

    # Merge the images
    merged_image = cv2.add(foreground, background)

    # Save
    cv2.imwrite(save_path, merged_image)
