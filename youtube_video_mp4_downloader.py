from pytube import YouTube
from pytubefix import YouTube as YouTubeFix
import argparse
import os
import subprocess
import re

def get_clean_video_title(video_title):
    # Remove invalid characters for filenames
    res = re.sub(r'[\/:*?"<>|]', '', video_title)

    # Trim and replace spaces with underscores
    res = res.strip().replace(' ', '_')

    # Ensure the filename is not too long
    max_filename_length = 255  # Maximum length for most file systems
    if len(res) > max_filename_length:
        res = res[:max_filename_length]

    return res

def list_youtube_streams_asc(yt):
    try:
        print('YouTube video streams in ascending order in quality:')
        for stream in yt.streams.filter(file_extension='mp4', mime_type='video/mp4',
                                        adaptive=True).order_by('resolution').asc():
            print('itag={} mime_type={} res={} fps={} vcodec={}'
                  .format(stream.itag,stream.mime_type, stream.resolution,
                          stream.fps, stream.video_codec))
        print()
        print('YouTube audio streams in ascending order in quality:')
        for stream in yt.streams.filter(only_audio=True, 
                                        mime_type='audio/mp4').order_by('abr').asc():
            print('itag={} mime_type={} abr={} acodec={}'
                  .format(stream.itag, stream.mime_type, stream.abr, stream.audio_codec))
        print()
    except Exception as ex:
        ex.add_note('Failed to fetch streams for YouTube instance.')
        raise

def list_selected_youtube_streams(video, audio):
    if video is not None:
        print('video in mp4 format:\nitag={} mime_type={} res={} fps={} vcodec={}\n'
            .format(video.itag, video.mime_type, video.resolution, video.fps, video.video_codec))
    if audio is not None:
        print('audio in mp4 format:\nitag={} mime_type={} abr={} acodec={}\n'
            .format(audio.itag, audio.mime_type, audio.abr, audio.audio_codec))

def get_highest_quality_video_stream(yt):
    # extract video of highest quality resolution possible.
    try:
        mp4_video_streams = yt.streams.filter(file_extension='mp4', adaptive=True,
                                            mime_type='video/mp4').order_by('resolution').desc()
        return mp4_video_streams.first()
    except Exception as ex:
        ex.add_note('Failed to fetch streams for YouTube instance.')
        raise

def pick_quality_video_stream(yt):
    # select quality resolution for video.
    try:
        itag = int(input('Input valid itag for video resolution quality: '))
        video = yt.streams.filter(file_extension='mp4', adaptive=True,
                            mime_type='video/mp4').order_by('resolution').desc().get_by_itag(itag)
        if video is None:
            raise ValueError('No video stream was found for given itag {}'.format(itag))
        return video
    except Exception as ex:
        ex.add_note('Failed to fetch streams for YouTube instance.')
        raise

def get_highest_quality_audio_stream(yt):
    # extract audio of highest bit rate quality possible.
    try:
        mp4_audio_streams = yt.streams.filter(only_audio=True,
                                            mime_type='audio/mp4').order_by('abr').desc()
        return mp4_audio_streams.first()
    except Exception as ex:
        ex.add_note('Failed to fetch streams for YouTube instance.')
        raise

def pick_quality_audio_stream(yt):
    # select bit rate quality for audio
    try:
        itag = int(input('Input valid itag for audio bit rate quality: '))
        audio = yt.streams.filter(only_audio=True,
                                mime_type='audio/mp4').order_by('abr').desc().get_by_itag(itag)
        if audio is None:
            raise ValueError('No audio stream was found for given itag {}'.format(itag))
        return audio
    except Exception as ex:
        ex.add_note('Failed to fetch streams for YouTube instance.')
        raise

def download_streams_to_dir(destination, audio, video, audio_only, video_only, download_both):
    try:
        if download_both:
            video.download(output_path=destination, filename='video.mp4') 
            audio.download(output_path=destination, filename='audio.mp4')
        else:
            video.download(output_path=destination, filename='video.mp4') if video_only else audio.download(output_path=destination, filename='audio.mp4')
        
        if audio_only or download_both:
            print('Converting mp4 audio to mp3...')
            subprocess.run('ffmpeg -y -i audio.mp4 -f mp3 -ab 320000 -vn {}\\audio.mp3'.format(destination), shell=True)
            print()
    except Exception as ex:
        ex.add_note('Failed to download stream(s) or ffmpeg command failed.')
        raise

def merge_streams(destination, convert, download_both, title):
    if convert and download_both:
        try:
            cmd = 'ffmpeg -y -i {}\\video.mp4 -i {}\\audio.mp4 -c:v copy -c:a copy {}\\output.mp4'
            subprocess.run(cmd.format(destination, destination, destination), shell=True)

            # result of success 
            print('{} has been successfully converted to mp4. Video and audio streams were merged.'
                .format(title))
            print()

            clean_title = get_clean_video_title(title)
            os.replace('{}\\output.mp4'.format(destination), '{}\\{}.mp4'.format(destination, clean_title))
            print('Merged output file name is {}'.format(clean_title))
        except Exception as ex:
            ex.add_note('ffmpeg merge command or renaming merged output file failed')
            raise

def download_youtube_video_pytube(url, audio_only, video_only, destination, auto, convert):
    yt = None
    try:
        # url input from user
        yt = YouTube(url)
    except Exception as ex:
        print('Failed to create YouTube instance from url {}\n Exception is {}'.format(url, ex))
        print('Exception type: {}.\n'.format(type(ex)))
        ex.add_note('Please check you are passing a valid YouTube url.')
        raise

    yt.bypass_age_gate() # needed for pytube module for age restricted content
    print()
    print('YouTube video title: {}'.format(yt.title))
    print()

    list_youtube_streams_asc(yt)

    video = get_highest_quality_video_stream(yt) if auto else pick_quality_video_stream(yt)
    audio = get_highest_quality_audio_stream(yt) if auto else pick_quality_audio_stream(yt)

    list_selected_youtube_streams(video, audio)

    download_both = (audio_only and video_only) or (not audio_only and not video_only)
    download_streams_to_dir(destination, audio, video, audio_only, video_only, download_both)
    print('{} has been successfully downloaded as audio and/or video files separately.'.format(yt.title))
    print()

    # ffmpeg conversion
    merge_streams(destination, convert, download_both, yt.title)


def download_youtube_video_pytubefix(url, audio_only, video_only, destination, auto, convert):
    yt = None
    try:
        # url input from user
        yt = YouTubeFix(url)
    except Exception as ex:
        print('Failed to create YouTube instance from url {}\n Exception is {}'.format(url, ex))
        print('Exception type: {}.\n'.format(type(ex)))
        ex.add_note('Please check you are passing a valid YouTube url.')
        raise

    print()
    print('YouTube video title: {}'.format(yt.title))
    print()

    list_youtube_streams_asc(yt)

    video = get_highest_quality_video_stream(yt) if auto else pick_quality_video_stream(yt)
    audio = get_highest_quality_audio_stream(yt) if auto else pick_quality_audio_stream(yt)

    list_selected_youtube_streams(video, audio)

    download_both = (audio_only and video_only) or (not audio_only and not video_only)
    download_streams_to_dir(destination, audio, video, audio_only, video_only, download_both)
    print('{} has been successfully downloaded as audio and/or video files separately.'.format(yt.title))
    print()

    # ffmpeg conversion
    merge_streams(destination, convert, download_both, yt.title)


def main(url, audio_only, video_only, destination, auto, convert):
    passed = False
    print('Attepting to download video with pytube.')
    try:
        download_youtube_video_pytube(url, audio_only, video_only, destination, auto, convert)
        print('Downloaded video succcessfully with pytube.\n')
        passed = True
    except Exception as ex:
        print('Failed to download video with pytube. Exception is {}\n'.format(ex))
    if not passed:
        print('Attepting to download video with pytubefix.')
        try:
            download_youtube_video_pytubefix(url, audio_only, video_only, destination, auto, convert)
            print('Downloaded video succcessfully with pytubefix.\n')
        except Exception as ex:
            print('Failed to download video with pytubefix. Exception is {}\n'.format(ex))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-ao', '--audio_only', default=0, type=int, help='only audio in mp3 + mp4 format (0 for no [default], 1 for yes)' , choices=(0,1))
    parser.add_argument('-vo', '--video_only', default=0, type=int, help='only video in mp4 format (0 for no [default], 1 for yes)', choices=(0,1))
    parser.add_argument('-dest', '--destination', default='.', type=str, help='destination directory (absolute path) to download mp4 file to, defaults to current directory')
    parser.add_argument('-m', '--merge', default=1, type=int, help='merge audio and video in mp4 format together (0 for no, 1 for yes [default])', choices=(0,1))
    parser.add_argument('-u', '--url', type=str, help='URL of the video to download', required=True)
    parser.add_argument('-a', '--auto', default=1, type=int, help='automatically selects bitrate for both audio and video (0 for no, 1 for yes [default])', choices=(0,1))
    
    args = parser.parse_args()
    if args.url is None:
        print('Not running script because url was not passed. Please pass in an YouTube video url.')
    else:
        main(args.url, args.audio_only, args.video_only, args.destination, args.auto, args.merge)
