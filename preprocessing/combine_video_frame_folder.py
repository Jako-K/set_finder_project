"""
FILE DESCRIPTION:
This file can combine different folders containing video extractions which have been performed with the
`preprocess_video.py` file. This can easily be extended to more than 2 folders, but this hasn't been necessary.
"""

import os
import glob
from helpers import number_of_files_in


FOLDER_PATH_A = "?"
FOLDER_PATH_B = "?"

folders_a = glob.glob(FOLDER_PATH_A + "/*")
folders_b = glob.glob(FOLDER_PATH_B + "/*")


def get_largest_file_name(path):
    file_numbers = []
    for image_path in glob.glob( os.path.join(path, "*") ):
        number_str = image_path[image_path.rfind("\\")+1:-4]
        file_numbers.append(int(number_str))
    return max(file_numbers)


for i in range(81):
    folder_a, folder_b = folders_a[i], folders_b[i]
    highest_num = number_of_files_in(folder_a)

    for image_path in glob.glob( os.path.join(folder_b, "*") ):
        new_file_name = str(get_largest_file_name(folder_a) + 1)
        new_file_path = os.path.join(folder_a, new_file_name + ".png")
        os.rename(image_path, new_file_path)




