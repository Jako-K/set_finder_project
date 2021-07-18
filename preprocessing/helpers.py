"""
FILE DESCRIPTION:
Contains must of the functionality necessary for the initial card extraction and the following image augmentation.
"""


import cv2
import seaborn; seaborn.set_style("darkgrid")
import numpy as np
import glob
import os
import itertools
import random
from scipy import ndimage
from skimage import transform
import utilsm.helpers as helpers


########################################################################################################
#################################        EXTRACTION HELPERS       ######################################
########################################################################################################


def extract_singe_card(image, contour_threshold, max_contour_threshold = 10**6):
    """
    Cut out card, and make the background transparent.
    image_transparent_background_cropped = extract_singe_card(cv2_color_image)
    """

    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    # Make alpha mask with contours of the cards
    alpha_mask = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    bounding_box, count = None, 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if (area > contour_threshold) and (area < max_contour_threshold):
            count += 1
            cv2.drawContours(image=alpha_mask,
                             contours=[cnt],  # the extra [] is just overcome some cv2 shenanigans
                             contourIdx=-1,
                             color=(0, 0, 0, 255),
                             thickness=-1,
                             )
            bounding_box = cv2.boundingRect(cnt)

    if count == 0:
        raise RuntimeError(f"Found no contours with an area greater than over equal to {contour_threshold}")
    if count != 1:
        raise RuntimeError(f"Found more than 1 contour with an area greater than over equal to {contour_threshold}")


    # Make the background transparent
    b_channel, g_channel, r_channel = cv2.split(image)
    _, _, _, alpha_channel = cv2.split(alpha_mask)
    return cv2.bitwise_and(image, image, mask=alpha_channel)

    image_transparent_background = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

    # Crop the image according to its bounding boxes
    x, y, w, h = bounding_box
    image_transparent_cropped = image_transparent_background[y:y + h, x:x + w]

    return image_transparent_cropped


def number_of_files_in(folder_path):
    return len(glob.glob( os.path.join(folder_path, "*")))


def unfair_coin_flip(p):
    return random.random() > p


def card_extraction_try(image):
    final_image = None
    areas_to_try = [20_000, 50_000, 80_000, 100_000]
    last_error = None
    
    for area in areas_to_try:
        # ´extract_singe_card´ raises an error if no cards were found or if more than one was found.
        try:
            final_image = extract_singe_card(image, area, 500_000)
        except RuntimeError as error:
            last_error = error
            continue
        return final_image
    
    print(last_error)
    return None


def resize_image(image, scaling):
    width = int(image.shape[1] * scaling)
    height = int(image.shape[0] * scaling)
    return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)


def make_set_folders(folder_path:str):
    possibilities = [["blue", "green", "red"],
                     ["1", "2", "3"],
                     ["diamond", "squiggle", "oval"],
                     ["filled", "empty", "strips"]]

    strings = []
    combinations = list((itertools.product(*possibilities)))
    for combination in combinations:
        string = ""
        for element in combination:
            string += element + "_"
        strings.append(string[:-1])
    for string in strings:
        os.mkdir(os.path.join(folder_path, string))



########################################################################################################
#################################        AUGMENTATION HELPERS       ####################################
########################################################################################################


def get_random_image_of_type(path, card_type):
    scale_percent = random.randint(10, 50) * 0.01

    combined_path = os.path.join(path, card_type)
    assert os.path.exists(combined_path), "Bad path"
    images = glob.glob(combined_path + "/*")
    image_path = random.choice(images)
    image = cv2.imread(image_path, -1)
    return resize_image(image, scale_percent)


def get_random_background(background_paths):
    scale_percent = random.randint(25, 50) * 0.01

    image_path = random.choice(background_paths)
    image = cv2.imread(image_path, -1)
    return resize_image(image, scale_percent)


def random_shear_with_padding(image):
    x, y, _ = image.shape
    pad_amount = max(x,y) # Just to be sure, probably to big, but doesn't really matter
    padded_image = cv2.copyMakeBorder( image, *(pad_amount for _ in range(4)), cv2.BORDER_CONSTANT)
    shear_amount = random.randint(-10,10) * 0.05 # these are just some acceptable shear values
    affine_tf = transform.AffineTransform(shear=shear_amount)
    sheared_image_float = transform.warp(padded_image, inverse_map=affine_tf)
    sheared_image_unit8 = (sheared_image_float * 255).astype('uint8')
    return sheared_image_unit8


def extract_largest_contour(image):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    largest_area_index = np.argmax([cv2.contourArea(c) for c in contours])
    bounding_box = cv2.boundingRect(contours[largest_area_index])
    x, y, w, h = bounding_box
    cropped_image = image[y:y + h, x:x + w]
    return cropped_image


def draw_single_yolo_bb_cv2(image_cv2, x, y, w, h, color=(0,0,255)):
    dh, dw, _ = image_cv2.shape

    l = int( (x - w/2) * dw)
    r = int( (x + w/2) * dw)
    t = int( (y - h/2) * dh)
    b = int( (y + h/2) * dh)

    if l < 0: l = 0
    if r > dw - 1: r = dw - 1
    if t < 0: t = 0
    if b > dh - 1: b = dh - 1

    cv2.rectangle(image_cv2, (l, t), (r, b), color, 2)
    return image_cv2


def plot_cv2_image(image, name=""):
    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def place_card_randomly_on_background(background_image, card_image, do_rotate=True, do_shear=True, debug=False, resize_final=False):

    if do_rotate:
        card_image = ndimage.rotate(card_image, random.randint(0, 365))

    if do_shear:
        card_image = random_shear_with_padding(card_image)
        card_image = extract_largest_contour(card_image)

    # Conceptually this is the same as randomly placing the card in
    # a black image with the same dimensions as the background image
    H, W, _ = background_image.shape
    h, w, _ = card_image.shape
    x, y = random.randint(0, W - w - 1), random.randint(0, H - h - 1)
    top, bottom, left, right = y, H - y - h, x, W - x - w
    temp = cv2.copyMakeBorder(card_image, top, bottom, left, right, cv2.BORDER_CONSTANT)

    # Masks
    _, _, _, alpha_mask = cv2.split(temp)
    rgb_mask = cv2.merge((alpha_mask, alpha_mask, alpha_mask))
    temp_reversed = cv2.bitwise_not(rgb_mask)

    # Cut out the image and the reverse in card_image and background image respectively
    card_cutout = cv2.bitwise_and(temp[:, :, :-1], rgb_mask)
    background_cutout = cv2.bitwise_and(background_image, temp_reversed)

    # Find the card's bounding box again ones it has been placed.
    # This is somewhat wasteful, but had some issues with the bounding boxes being
    # slightly to large. Guess it was caused by the round corners of the card
    # and the rotation. All in all, the computational overhead is not to bad, so why not do the easy thing.
    contours, _ = cv2.findContours(image=alpha_mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    largest_area_index = np.argmax([cv2.contourArea(c) for c in contours])
    bounding_box = cv2.boundingRect(contours[largest_area_index])
    x, y, w, h = bounding_box

    # Calculate card image coordinates in percentage (YOLO expects this format)
    center_x = x + w / 2
    center_y = y + h / 2
    center_x_norm = center_x / W
    center_y_norm = center_y / H
    w_norm = w / W
    h_norm = h / H
    yolo_coord_format = [center_x_norm, center_y_norm, w_norm, h_norm]

    final_image = card_cutout + background_cutout

    if resize_final:
        final_image = resize_image(final_image, resize_final)

    if debug:
        print("Yolo coordinates: ", yolo_coord_format)
        plot_cv2_image(draw_single_yolo_bb_cv2(final_image, *yolo_coord_format), "final with bb")

    return final_image, yolo_coord_format


def save_all(merged_image, yolo_coord, card_type, card_type_label, name, image_path, labels_path, overwrite=False):
    file_name = card_type + "-" + name

    cv2.imwrite(image_path + f"/{file_name}.png", merged_image)
    yolo_format = f"{card_type_label} {yolo_coord[0]} {yolo_coord[1]} {yolo_coord[2]} {yolo_coord[3]}"

    file_path = labels_path + f"/{file_name}.txt"
    if not overwrite:
        assert not os.path.exists(file_path), "File name already exists"

    file = open(file_path, mode="a")
    print(yolo_format, file=file)
    file.close()


