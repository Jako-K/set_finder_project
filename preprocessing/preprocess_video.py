"""
FILE DESCRIPTION:
This file detect and extract set cards from video-files. To function correctly in needs to be given exactly 81 videos,
which correspond to 1 video for each set card type. As a side note, avoid super bright videos and very white backgrounds
"""

import os
import glob
import cv2
from tqdm.notebook import tqdm
from helpers import resize_image, make_set_folders, number_of_files_in, card_extraction_try


if __name__ == "__main__":
    # Path stuff
    SET_FOLDER_PATH = "?"
    VIDEO_PATH = "?"

    if len(glob.glob(os.path.join(SET_FOLDER_PATH, "*"))) == 0:
        make_set_folders(SET_FOLDER_PATH)

    folder_paths = glob.glob(os.path.join(SET_FOLDER_PATH, "*")); assert len(folder_paths) == 81, "Too few/many folders"
    video_paths =  glob.glob(os.path.join(VIDEO_PATH, "*")); assert len(video_paths) == 81, "Too few/many videos"

    # Hyperparameters
    save_every_nth_frame = 10
    scale_factor = 0.50

    # Loop over all 81 videos
    for i in tqdm(range(81)):
        video_path, folder_path = video_paths[i], folder_paths[i]
        cap = cv2.VideoCapture(video_path)
        frame_i = -1

        # Loop over all frames in the i'th video
        while cap.isOpened():
            frame_i += 1 # Easier to start at -1 and increment here, instead of the end due to ´continue´
            video_feed_active, frame = cap.read()

            # Clean up when all frames has been dealt with
            if not video_feed_active:
                cap.release()
                cv2.destroyAllWindows()
                break

            # Processing each frame is unnecessary, so just take every n'th one.
            if frame_i%save_every_nth_frame != 0:
                continue

            resized = resize_image(frame, scale_factor)
            final_image = card_extraction_try(resized)

            # If card extraction was successful --> save it
            if final_image is not None:
                save_path = os.path.join(folder_path, str(number_of_files_in(folder_path)) + '.jpg')
                assert not os.path.exists(save_path), "Path already exists, shouldn't happened"

                save_path_as_png = save_path[:-4] + ".png" # .png for alpha
                cv2.imwrite(save_path_as_png, final_image)