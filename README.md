# youtube_video_mp4_downloader
YouTube Video MP4 Downloader. Downloads and extracts YouTube videos into separate audio and video mp4 files, then merges them back together (creates up to 4 files if downloading, converting, and merging both audio + video streams). Useful for avoiding ads on the YouTube player or storing YouTube videos locally on your device. Downloads at highest quality possible for both audio and video automatically, but quality can manually selected for both.


## Prerequisites
- pytube (https://pypi.org/project/pytube/)
- ffmpeg (https://www.ffmpeg.org/, not installed in virtual environment)
  - You can check if ffmpeg is installed in your environment by running `ffmpeg_check.py`
- pytubefix (https://pypi.org/project/pytubefix/)


## Usage
* Pass YouTube video url (-u flag, required) and directory (-dest flag, requires absolute path, defaults to current directory) to save the video, audio, combined video and audio file to.
* -ao flag (defaults to 0) sets only audio in mp4 format (0 for no, 1 for yes)
* -vo flag (defaults to 0) sets only video in mp4 format (0 for no, 1 for yes)
* -m flag (defaults to 1) merges audio and video in mp4 format togeher (0 for no, 1 for yes)
* --auto flag (defaults to 1) automatically selects bitrate for both audio and video (0 for no, 1 for yes)
* --create_mp3 flag (deaults to 0) creates mp3 file from downloaded mp4 file (0 for no, 1 for yes)
* -dest flag (defaults to current directory) sets output directory (absolute path) to download mp4 and mp3 files to
* -vi flag (defaults to 0) displays extended information (likes, views, video length, publish date, etc.) about the video (0 for no, 1 for yes)


## Should I use pytube or pytubefix for downloading videos?
The current script implementation will first try to download using pytube module. If using pytube fails, then the script will attempt to use pytubefix module to download the video instead.
It is difficult to determine whether pytube or pytubefix is the better to choice to use due to future possible changes on YouTube's end and whether the maintainers of both modules will update their pacakges respectively when such situations occur.
You will need to determine whether which option/module works for you and if both modules work then which module suits your needs. It is possible that both modules can be broken. Check pull requests and issues on the respective GitHub repositories to resolve the issue you're facing.


## Should I use a virtual environlment?
Yes you should. You can follow the steps to create the virtual environment here - https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments. You should create the virtual environment in the same directory where you downloaded the repository, then use pip in the virtual environment to install the packages described in the prerequisites section except for ffmpeg. ffmpeg will need to be installed separately outside the virtual environment.
