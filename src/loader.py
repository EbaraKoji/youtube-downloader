import os
import subprocess

from captions import (
    CaptionExt,
    add_subtitle_to_video,
    download_caption,
    save_caption,
    word_timestamp_to_caption,
)
from pytubefix import YouTube  # type: ignore
from pytubefix.exceptions import RegexMatchError  # type: ignore
from transcribe import generate_transcribed_caption
from translate import create_translated_caption
from videos import combine_audio, download_audio, download_video


def download_contents(
    video_id: str,
    mode='video',
    resolutions: str | list[str] = ['1080p', '720p'],
    out_dir: str | None = None,
    caption_exts: set[CaptionExt] = {CaptionExt.SRT},
    make_metadata=True,
    file_name=None,
):
    audio_name = 'audio.mp3' if file_name is None else f'{file_name}.mp3'
    video_name = 'video.mp4' if file_name is None else f'{file_name}.mp4'
    caption_name = 'caption' if file_name is None else file_name
    audio_success = video_success = cap_success = None

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

    if os.path.exists(out_dir):
        print(f'outdir: {out_dir} already exists.')
        return {
            'audio_success': False,
            'cap_success': False,
            'video_success': False,
            'out_dir': out_dir,
            'audio_name': audio_name,
            'caption_name': caption_name,
            'video_name': video_name,
        }
    else:
        os.mkdir(out_dir)

    if make_metadata is True:
        with open(f'{out_dir}/url.txt', 'w') as f:
            f.write(url)

    audio_success = download_audio(
        yt, output_path=out_dir, filename=audio_name
    )

    # High res video can only be downloaded without audio!

    # download caption
    cap_success = download_caption(
        video_id, f'{out_dir}/{caption_name}', caption_exts
    )

    if mode == 'video':
        # XXX: need to modify function_patterns in ciper.py
        # -> https://github.com/pytube/pytube/issues/1954
        video_success = download_video(
            yt,
            output_path=out_dir,
            resolutions=resolutions,
            filename=video_name,
        )

    return {
        'audio_success': audio_success,
        'cap_success': cap_success,
        'video_success': video_success,
        'out_dir': out_dir,
        'audio_name': audio_name,
        'caption_name': caption_name,
        'video_name': video_name,
    }


def transcribe_audio(
    out_dir: str,
    audio_name: str,
    translate=True,
    deepl_api_key: str | None = None,
):
    # transcribe caption from audio
    # TODO: add transcribe config(model_name, etc.)
    _, word_timestamps = generate_transcribed_caption(
        f'{out_dir}/{audio_name}'
    )
    caption = word_timestamp_to_caption(word_timestamps)
    save_caption(caption, f'{out_dir}/transcribe.vtt')

    # translate caption
    if translate is True:
        # TODO: error handling of api
        create_translated_caption(
            file_path=f'{out_dir}/transcribe.vtt',
            save_path=f'{out_dir}/translated.vtt',
            deepl_api_key=str(deepl_api_key),
            trim_caption_to_sentences=False,
        )


def download_and_save_video(
    video_id: str,
    mode='video',
    resolutions: str | list[str] = ['1080p', '720p'],
    out_dir: str | None = None,
    caption_exts: set[CaptionExt] = {CaptionExt.SRT},
    make_metadata=True,
    file_name=None,
    download_only=False,
    transcribe=False,
    translate=False,
    deepl_api_key: str | None = None,
):
    result = download_contents(
        video_id,
        mode,
        resolutions,
        out_dir,
        caption_exts,
        make_metadata,
        file_name,
    )

    download_success = not (
        (result['audio_success'] is False)
        or (result['video_success'] is False)
        or (result['cap_success'] is False)
    )
    if download_only or not download_success:
        return download_success

    if transcribe is True:
        transcribe_audio(
            result['out_dir'], result['audio_name'], translate, deepl_api_key
        )

    if mode == 'audio':
        return True

    # using same output path as input one fails to combine!
    subprocess.run(
        ['mv', f'{result["out_dir"]}/{result["video_name"]}', f'{result["out_dir"]}/no_audio.mp4']
    )
    combine_audio(
        f'{result["out_dir"]}/no_audio.mp4',
        f'{result["out_dir"]}/{result["audio_name"]}',
        f'{result["out_dir"]}/no_caption.mp4',
    )
    subprocess.run(['rm', '-rf', f'{result["out_dir"]}/no_audio.mp4'])

    if result['cap_success'] is False:
        caption_file = None
    elif CaptionExt.SRT in caption_exts:
        caption_file = f'{result["out_dir"]}/{result["caption_name"]}.srt'
    elif CaptionExt.VTT in caption_exts:
        caption_file = f'{result["out_dir"]}/{result["caption_name"]}.vtt'
    else:
        caption_file = None

    if caption_file is None:
        subprocess.run(
            [
                'mv',
                f'{result["out_dir"]}/no_caption.mp4',
                f'{result["out_dir"]}/{result["video_name"]}',
            ]
        )
    else:
        add_subtitle_to_video(
            f'{result["out_dir"]}/no_caption.mp4',
            caption_file,
            f'{result["out_dir"]}/{result["video_name"]}',
        )
        subprocess.run(['rm', '-rf', f'{result["out_dir"]}/no_caption.mp4'])

    print(f'Successfully saved a video to {result["out_dir"]}.')

    return True
