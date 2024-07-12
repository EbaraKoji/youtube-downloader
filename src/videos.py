import subprocess

import moviepy.editor as mpe  # type: ignore
from pytube import YouTube  # type: ignore


def combine_audio(vidname: str, audname: str, outname: str, fps=60):
    # https://stackoverflow.com/questions/63881088/how-to-merge-mp3-and-mp4-in-python-mute-a-mp4-file-and-add-a-mp3-file-on-it
    if vidname == outname:
        raise ValueError(
            'using same outname as vidname causes combining bugs!'
        )
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname, fps=fps)


def download_audio(yt: YouTube, output_path: str, filename='audio.mp3'):
    audio_stream = (
        yt.streams.filter(
            progressive=True,
            file_extension='mp4',
        )
        .order_by('resolution')
        .first()
    )

    if audio_stream is None:
        print('No audio available.')
        return False

    print(f'Video with audio resolution: {audio_stream.resolution}')

    print('Downloading video for audio...')
    audio_stream.download(
        output_path=output_path,
        filename='low_res.mp4',
    )

    print('converting mp4 to mp3...')
    subprocess.run(
        [
            'ffmpeg',
            '-i',
            f'{output_path}/low_res.mp4',
            f'{output_path}/{filename}',
        ]
    )
    subprocess.run(['rm', '-rf', f'{output_path}/low_res.mp4'])
    return True


def download_video(
    yt: YouTube,
    output_path: str,
    resolutions: str | list[str] = ['1080p', '720p'],
    filename='video.mp4',
):
    video_stream = (
        yt.streams.filter(
            progressive=False,
            file_extension='mp4',
            res=resolutions,
        )
        .order_by('resolution')
        .desc()
        .first()
    )
    if video_stream is None:
        print('No allowed resolutions for video.')
        return False

    print(f'Video resolution: {video_stream.resolution}')

    print('Downloading video...')
    video_stream.download(
        output_path=output_path,
        filename=filename,
    )
    return True
