import os
import subprocess

from captions import add_subtitle_to_video, download_caption
from pytube import YouTube  # type: ignore
from pytube.exceptions import RegexMatchError  # type: ignore
from videos import combine_audio, download_audio, download_video


def download_and_make_captioned_video(
    video_id: str,
    resolutions: str | list[str] = ['1080p', '720p'],
    out_dir: str | None = None,
):
    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(url)
    except RegexMatchError:
        print(f'"{url}" is not a valid Youtube URL.')
        return False

    if out_dir is None:
        out_dir = f"outputs/{yt.title.lower().replace(' ', '_')}"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    with open(f'{out_dir}/url.txt', 'w') as f:
        f.write(url)

    success = download_audio(yt, output_path=out_dir)
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
        f'{out_dir}/audio.mp3',
        f'{out_dir}/no_caption.mp4',
    )
    subprocess.run(['rm', '-rf', f'{out_dir}/no_audio.mp4'])

    success = download_caption(video_id, f'{out_dir}/caption.srt')
    if success is False:
        return False

    add_subtitle_to_video(
        f'{out_dir}/no_caption.mp4',
        f'{out_dir}/caption.srt',
        f'{out_dir}/video.mp4',
    )
    subprocess.run(['rm', '-rf', f'{out_dir}/no_caption.mp4'])

    print(f'Successfully saved a video to {out_dir}.')

    return True


def download_audio_caption(
    video_id: str,
    out_dir: str | None = None,
):
    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(url)
    except RegexMatchError:
        print(f'"{url}" is not a valid Youtube URL.')
        return False

    if out_dir is None:
        out_dir = f"outputs/{yt.title.lower().replace(' ', '_')}"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    with open(f'{out_dir}/url.txt', 'w') as f:
        f.write(url)

    success = download_audio(yt, output_path=out_dir)
    if success is False:
        return False

    success = download_caption(video_id, f'{out_dir}/caption.srt')
    if success is False:
        return False

    return True
