# importing packages 
from pytube import YouTube
import ffmpeg
import os 
  


def main():
    # url input from user
    print("Enter the URL of the video you want to download:")
    url_input = str(input(">> "))
    yt = YouTube(url_input)
    print()
    print("YouTube video title: {}".format(yt.title))
    print()

    # extract video of highest quality resolution possible.
    mp4_video_streams = yt.streams.filter(file_extension='mp4', adaptive=True, mime_type="video/mp4")
    video = mp4_video_streams.first()

    # extract audio of highest bit rate quality possible.
    mp4_audio_streams = yt.streams.filter(only_audio=True, mime_type="audio/mp4")
    audio = mp4_audio_streams.last()

    print("mp4 video: {}".format(video))
    print("mp4 audio: {}".format(audio))
    print()
    
    # check for destination to save file 
    print("Enter the destination (leave blank for current directory):") 
    destination = str(input(">> ")) or '.'
    
    # download the file
    video.download(output_path=destination, filename="video.mp4") 
    audio.download(output_path=destination, filename="audio.mp4")
    
    # result of success 
    print(yt.title + " has been successfully downloaded.")

    # ffmpeg conversion
    video = ffmpeg.input("video.mp4")
    audio = ffmpeg.input("audio.mp4")
    ffmpeg.concat(video, audio, v=1, a=1).output("result.mp4").run()

    # result of success 
    print(yt.title + " has been successfully converted.")

if __name__ == '__main__':
    main()