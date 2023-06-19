from pathlib import Path
from typing import List

from natsort import natsorted


def get_starting_frames(folder_path: str, video_file_pattern: str = "*/BehavCam*/*.avi") -> List[int]:
    """
    Returns the list of starting frames for the behavior movies.
    Each entry is a frame number that corresponds to the first frame of each file listed in file_paths as if they were continuous.

    Parameters
    ----------
    folder_path : str
        The folder path that points to the main Miniscope folder.
        The behavior movie files are expected to be located in subfolders (e.g. 'BehavCam 2/') within the main folder.
    video_file_pattern: str, optional
        The file pattern to look for in the folder.
    """
    try:
        import cv2
    except ImportError:
        raise "To use this function install cv2: \n\n pip install opencv-python-headless\n\n"

    folder_path = Path(folder_path)
    behavior_video_file_paths = natsorted(list(folder_path.glob(video_file_pattern)))
    assert behavior_video_file_paths, f"Could not find the video files in '{folder_path}'."

    starting_frames = [0]
    for video_file_path in behavior_video_file_paths[:-1]:
        video_capture = cv2.VideoCapture(str(video_file_path))
        num_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        starting_frames.append(starting_frames[-1] + num_frames)

    return starting_frames
