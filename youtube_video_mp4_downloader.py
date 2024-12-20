from pytube import YouTube
from pytube.cli import on_progress as pytube_on_progress
from pytubefix import YouTube as YouTubeFix
from pytubefix.cli import on_progress as pytubefix_on_progress
from ffmpeg_check import is_ffmpeg_installed
from datetime import datetime
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


def download_streams_to_dir(destination, audio, video, audio_only, video_only, download_both, create_mp3):
    try:
        dest = os.path.abspath(destination)
        if download_both:
            print('File size of video stream in megabytes: {:.02f} MB'.format(video.filesize_mb))
            print('File size of audio stream in megabytes: {:.02f} MB'.format(audio.filesize_mb))
            start = datetime.now()
            video.download(output_path=dest, filename='video.mp4')
            end = datetime.now()
            delta = (end - start).total_seconds()
            print('Time to download video stream: {:.03f} seconds'.format(delta))
            start = datetime.now()
            audio.download(output_path=dest, filename='audio.mp4')
            end = datetime.now()
            delta = (end - start).total_seconds()
            print('Time to download audio stream: {:.03f} seconds'.format(delta))
        else:
            if video_only:
                print('File size of video stream in megabytes: {:.02f} MB'.format(video.filesize_mb))
                start = datetime.now()
                video.download(output_path=dest, filename='video.mp4')
                end = datetime.now()
                delta = (end - start).total_seconds()
                print('Time to download video stream: {:.03f} seconds'.format(delta))
            else:
                print('File size of audio stream in megabytes: {:.02f} MB'.format(audio.filesize_mb))
                start = datetime.now()
                audio.download(output_path=dest, filename='audio.mp4')
                end = datetime.now()
                delta = (end - start).total_seconds()
                print('Time to download audio stream: {:.03f} seconds'.format(delta))
        if (audio_only or download_both) and create_mp3:
            print('Converting mp4 audio to mp3...')
            if is_ffmpeg_installed():
                mp4_path = os.path.join(dest, 'audio.mp4')
                mp3_path = os.path.join(dest, 'audio.mp3')
                start = datetime.now()
                subprocess.run(f'ffmpeg -loglevel quiet -y -i {mp4_path} -f mp3 -ab 320000 -vn {mp3_path}', shell=True)
                end = datetime.now()
                delta = (end - start).total_seconds()
                print('Time to convert mp4 audio to mp3: {:.03f} seconds'.format(delta))
                print('audio.mp3 file size is {:.02f} MB'.format(os.path.getsize(mp3_path) / (1024 * 1024)))
            else:
                print('ffmpeg is not installed, canceling mp4 to mp3 conversion operation.')
            print()
    except Exception as ex:
        ex.add_note('Failed to download stream(s) or ffmpeg command failed.')
        raise


def merge_streams(destination, merge, download_both, title):
    if not is_ffmpeg_installed():
        print('ffmpeg is not installed, canceling merge streams operation.') 
        return
    if merge and download_both:
        print('Merging mp4 video and audio streams together...')
        try:
            dest = os.path.abspath(destination)
            video_path = os.path.join(dest, 'video.mp4')
            audio_path = os.path.join(dest, 'audio.mp4')
            output_path = os.path.join(dest, 'output.mp4')
            cmd = f'ffmpeg -loglevel quiet -y -i {video_path} -i {audio_path} -c:v copy -c:a copy {output_path}'
            start = datetime.now()
            subprocess.run(cmd, shell=True)
            end = datetime.now()
            merge_time = (end - start).total_seconds()
            print('{} has been successfully converted to mp4. Video and audio streams were merged.\nTime to merge streams: {:.03f} seconds'
                .format(title, merge_time))
            print()
            clean_title = get_clean_video_title(title)
            rename_path = os.path.join(dest, f'{clean_title}.mp4')
            os.replace('{}'.format(output_path), '{}'.format(rename_path))
            print('Merged output file name is {}.mp4'.format(clean_title))
            print('{}.mp4 file size is {:.02f} MB'.format(clean_title, os.path.getsize(rename_path) / (1024 * 1024)))
        except Exception as ex:
            ex.add_note('ffmpeg merge command or renaming merged output file failed')
            raise


def download_youtube_video_pytube(url, audio_only, video_only, destination, auto, merge, create_mp3, show_video_info):
    yt = None
    try:
        yt = YouTube(url, on_progress_callback=pytube_on_progress)
    except Exception as ex:
        print('Failed to create YouTube instance from url {}\n Exception is {}'.format(url, ex))
        print('Exception type: {}.\n'.format(type(ex)))
        ex.add_note('Please check you are passing a valid YouTube url.')
        raise

    yt.bypass_age_gate() # needed for pytube module for age restricted content
    print()
    print('YouTube video title: {}'.format(yt.title))
    if show_video_info:
        output_video_info(yt)
    print()

    list_youtube_streams_asc(yt)

    video = get_highest_quality_video_stream(yt) if auto else pick_quality_video_stream(yt)
    audio = get_highest_quality_audio_stream(yt) if auto else pick_quality_audio_stream(yt)

    list_selected_youtube_streams(video, audio)

    download_both = (audio_only and video_only) or (not audio_only and not video_only)
    download_streams_to_dir(destination, audio, video, audio_only, video_only, download_both, create_mp3)
    print('{} has been successfully downloaded as audio and/or video files separately.'.format(yt.title))
    print()

    merge_streams(destination, merge, download_both, yt.title)
    print('Output files can be located at {}'.format(os.path.abspath(destination)))


def download_youtube_video_pytubefix(url, audio_only, video_only, destination, auto, merge, create_mp3, show_video_info):
    yt = None
    try:
        yt = YouTubeFix(url, on_progress_callback=pytubefix_on_progress)
    except Exception as ex:
        print('Failed to create YouTube instance from url {}\n Exception is {}'.format(url, ex))
        print('Exception type: {}.\n'.format(type(ex)))
        ex.add_note('Please check you are passing a valid YouTube url.')
        raise

    print()
    print('YouTube video title: {}'.format(yt.title))
    if show_video_info:
        output_video_info(yt)
    print()

    list_youtube_streams_asc(yt)

    video = get_highest_quality_video_stream(yt) if auto else pick_quality_video_stream(yt)
    audio = get_highest_quality_audio_stream(yt) if auto else pick_quality_audio_stream(yt)

    list_selected_youtube_streams(video, audio)

    download_both = (audio_only and video_only) or (not audio_only and not video_only)
    download_streams_to_dir(destination, audio, video, audio_only, video_only, download_both, create_mp3)
    print('{} has been successfully downloaded as audio and/or video files separately.'.format(yt.title))
    print()

    merge_streams(destination, merge, download_both, yt.title)
    print('Output files can be located at {}'.format(os.path.abspath(destination)))


def output_video_info(yt):
    print(f'YouTube video_id: {yt.video_id}')
    print(f'YouTube author: {yt.author}')
    print(f'YouTube channel_id: {yt.channel_id}')
    print(f'YouTube channel url: {yt.channel_url}')
    print(f'YouTube video publish date: {yt.publish_date}')
    print(f'YouTube video length (MM:SS): {yt.length // 60}:{yt.length % 60}')
    print(f'YouTube video views: {yt.views}')
    if type(yt) == YouTubeFix:
        print(f'YouTube video likes: {yt.likes}')
    print(f'YouTube video average rating: {yt.rating}')
    print(f'YouTube video description: {yt.description}')


def main(url, audio_only, video_only, destination, auto, merge, create_mp3, show_video_info):
    passed = False
    print('Attepting to download video with pytube.')
    try:
        download_youtube_video_pytube(url, audio_only, video_only, destination, auto, merge, create_mp3, show_video_info)
        print('Downloaded video succcessfully with pytube.\n')
        passed = True
    except Exception as ex:
        print('Failed to download video with pytube. Exception is {}\n'.format(ex))
    if not passed:
        print('Attepting to download video with pytubefix.')
        try:
            download_youtube_video_pytubefix(url, audio_only, video_only, destination, auto, merge, create_mp3, show_video_info)
            print('Downloaded video succcessfully with pytubefix.\n')
        except Exception as ex:
            print('Failed to download video with pytubefix. Exception is {}\n'.format(ex))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ao', '--audio_only', default=0, type=int, help='only audio in mp4 format (0 for no [default], 1 for yes)' , choices=(0,1))
    parser.add_argument('-vo', '--video_only', default=0, type=int, help='only video in mp4 format (0 for no [default], 1 for yes)', choices=(0,1))
    parser.add_argument('-dest', '--destination', default='.', type=str, help='destination directory (absolute path) to download mp4 and mp3 files to, defaults to current directory')
    parser.add_argument('-m', '--merge', default=1, type=int, help='merge audio and video in mp4 format together (0 for no, 1 for yes [default])', choices=(0,1))
    parser.add_argument('-u', '--url', type=str, help='URL of the video to download', required=True)
    parser.add_argument('-a', '--auto', default=1, type=int, help='automatically selects bitrate for both audio and video (0 for no, 1 for yes [default])', choices=(0,1))
    parser.add_argument('--create_mp3', default=0, type=int, help='creates mp3 file from downloaded mp4 file (0 for no [default], 1 for yes)', choices=(0,1))
    parser.add_argument('-vi', '--video_info', default=0, type=int, help='Displays extended information (likes, views, video length, publish date, etc.) about the video (0 for no [default], 1 for yes)', choices=(0,1))
    args = parser.parse_args()
    if args.url is None:
        print('Not running script because url was not passed. Please pass in an YouTube video url.')
    else:
        main(args.url, args.audio_only, args.video_only, args.destination, args.auto, args.merge, args.create_mp3, args.video_info)
