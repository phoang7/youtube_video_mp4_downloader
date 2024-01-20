# importing packages 
from pytube import YouTube
import ffmpeg
import argparse


def main(url, audio_only, video_only, destination, convert):
    # url input from user
    yt = YouTube(url)
    print()
    print("YouTube video title: {}".format(yt.title))
    print()

    # extract video of highest quality resolution possible.
    mp4_video_streams = yt.streams.filter(file_extension='mp4', adaptive=True, mime_type="video/mp4")
    video = mp4_video_streams.first()

    # extract audio of highest bit rate quality possible.
    mp4_audio_streams = yt.streams.filter(only_audio=True, mime_type="audio/mp4")
    audio = mp4_audio_streams.last()

    print("video in mp4 format: {}".format(video))
    print("audio in mp4 format: {}".format(audio))
    print()
    
    # download the file
    download_both = (audio_only and video_only) or (not audio_only and not video_only)
    if download_both:
        video.download(output_path=destination, filename="video.mp4") 
        audio.download(output_path=destination, filename="audio.mp4")
    else:
        video.download(output_path=destination, filename="video.mp4") if video_only else audio.download(output_path=destination, filename="audio.mp4")
    
    # result of success 
    print(yt.title + " has been successfully downloaded as audio and video files separately.")
    print()

    # ffmpeg conversion

    if convert and download_both: 
        video = ffmpeg.input("video.mp4")
        audio = ffmpeg.input("audio.mp4")
        ffmpeg.concat(video, audio, v=1, a=1).output("result.mp4").run()
        # result of success 
        print(yt.title + " has been successfully converted to mp4.")
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-ao", "--audio_only", default=0, type=int, help="only audio in mp4 format (0 for no [default], 1 for yes)")
    parser.add_argument("-vo", "--video_only", default=0, type=int, help="only video in mp4 format (0 for no [default], 1 for yes)")
    parser.add_argument("-dest", "--destination", default=".", type=str, help="destination directory to download mp4 file to, defaults to current directory")
    parser.add_argument("-m", "--merge", default=1, type=int, help="merge audio and video in mp4 format together (0 for no, 1 for yes [default])")
    parser.add_argument("-u", "--url", type=str, help="URL of the video to download", required=True)
    
    args = parser.parse_args()
    if args.url is None:
        print("Not running script because url was not passed. Please pass in an YouTube video url.")
    else:
        main(args.url, args.audio_only, args.video_only, args.destination, args.merge)