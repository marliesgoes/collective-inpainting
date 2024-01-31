from image_utils import merge_images

image_path_1 = 'static/background.jpg'
image_path_2 = 'static/prev_image.jpg'
mask_path = 'static/masks/mask_fence_detail.jpg'
save_path = 'static/test_image_utils.jpg'
merge_images(image_path_1, image_path_2, mask_path, save_path)