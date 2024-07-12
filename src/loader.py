import os
import subprocess

from captions import add_subtitle_to_video, download_caption
from pytube import YouTube  # type: ignore
from pytube.exceptions import RegexMatchError  # type: ignore
from videos import combine_audio, download_audio, download_video


def download_and_save_video(
    video_id: str,
    resolutions: str | list[str] = ['1080p', '720p'],
    out_dir: str | None = None,
    with_caption=True,
    make_metadata=True,
    file_name=None,
):
    audio_name = 'audio.mp3' if file_name is None else f'{file_name}.mp3'
    video_name = 'video.mp4' if file_name is None else f'{file_name}.mp4'
    caption_name = 'caption.srt' if file_name is None else f'{file_name}.srt'

    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(url)
    except RegexMatchError:
        print(f'"{url}" is not a valid Youtube URL.')
        return False

    if out_dir is None:
        out_dir = f"outputs/{yt.title.lower().replace(' ', '_')}"
    else:
        out_dir = f'outputs/{out_dir}'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if make_metadata is True:
        with open(f'{out_dir}/url.txt', 'w') as f:
            f.write(url)

    success = download_audio(yt, output_path=out_dir, filename=audio_name)
    if success is False:
        return False
    # High res video can only be downloaded without audio!

    # XXX: need to modify function_patterns in ciper.py
    # -> https://github.com/pytube/pytube/issues/1954
    success = download_video(
        yt,
        output_path=out_dir,
        resolutions=resolutions,
        filename='no_audio.mp4',
    )
    if success is False:
        return False

    # using same output path as input one fails to combine!
    combine_audio(
        f'{out_dir}/no_audio.mp4',
        f'{out_dir}/{audio_name}',
        f'{out_dir}/no_caption.mp4',
    )
    subprocess.run(['rm', '-rf', f'{out_dir}/no_audio.mp4'])

    success = download_caption(video_id, f'{out_dir}/{caption_name}')
    if success is False:
        return False

    if with_caption is False:
        return True

    add_subtitle_to_video(
        f'{out_dir}/no_caption.mp4',
        f'{out_dir}/{caption_name}',
        f'{out_dir}/{video_name}',
    )
    subprocess.run(['rm', '-rf', f'{out_dir}/no_caption.mp4'])

    print(f'Successfully saved a video to {out_dir}.')

    return True


def download_and_save_audio(
    video_id: str,
    out_dir: str | None = None,
    with_caption=True,
    make_metadata=True,
    file_name=None,
):
    audio_name = 'audio.mp3' if file_name is None else f'{file_name}.mp3'
    caption_name = 'caption.srt' if file_name is None else f'{file_name}.srt'

    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(url)
    except RegexMatchError:
        print(f'"{url}" is not a valid Youtube URL.')
        return False

    if out_dir is None:
        out_dir = f"outputs/{yt.title.lower().replace(' ', '_')}"
    else:
        out_dir = f'outputs/{out_dir}'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if make_metadata is True:
        with open(f'{out_dir}/url.txt', 'w') as f:
            f.write(url)

    success = download_audio(yt, output_path=out_dir, filename=audio_name)
    if success is False:
        return False

    if with_caption is False:
        return True

    success = download_caption(video_id, f'{out_dir}/{caption_name}')
    if success is False:
        return False

    return True
