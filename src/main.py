import argparse
import os
import subprocess
import sys
import traceback

from pytube import YouTube  # type: ignore
from pytube.exceptions import RegexMatchError  # type: ignore

from captions import add_subtitle_to_video, load_caption
from utils import combine_audio

parser = argparse.ArgumentParser()

parser.add_argument(
    'video_id',
    help='Youtube Video ID',
)
parser.add_argument(
    '--output',
    '-o',
    help='The name of output dir',
    required=False,
)
parser.add_argument(
    '--mode',
    '-m',
    help='download format(mp4/mp3)',
    default='mp4',
    required=False,
)
parser.add_argument(
    '--resolution',
    '-r',
    help='video resolution',
    required=False,
)
args = parser.parse_args()

try:
    url = f'https://www.youtube.com/watch?v={args.video_id}'
    yt = YouTube(url)
except RegexMatchError:
    print(f'"{url}" is not a valid Youtube URL.')
    sys.exit(1)

if args.resolution is None:
    video_resolutions = ['1080p', '720p']
else:
    video_resolutions = [args.resolution]

# XXX: need to modify function_patterns in ciper.py
# -> https://github.com/pytube/pytube/issues/1954

# High res video can only be downloaded without audio!

# Querying audio stream
audio_streams = (
    yt.streams.filter(
        progressive=True,
        file_extension='mp4',
    )
    .order_by('resolution')
    .desc()
)

if len(audio_streams) == 0:
    print('No audio available.')
    sys.exit(1)

# Usually high res video can only be downloaded without audio, but if available...
# if audio_streams[0].resolution in video_resolutions:
#     print('Downloading video with audio...')
#     video_stream = audio_streams[0]
#     print(f'Video resolution: {video_stream.resolution}')

#     if args.output is None:
#         file_name = video_stream.title.lower().replace(' ', '_')
#     else:
#         file_name = args.output
#     video = video_stream.download(
#         output_path='outputs/video',
#         filename=f'{file_name}.mp4',
#     )
#     print(video)
#     sys.exit(0)

audio_stream = audio_streams[-1]
print(f'Video with audio resolution: {audio_stream.resolution}')

# Querying video stream
video_stream = (
    yt.streams.filter(
        progressive=False,
        file_extension='mp4',
        res=video_resolutions,
    )
    .order_by('resolution')
    .desc()
    .first()
)

if video_stream is None:
    print('No allowed resolutions for video.')
    sys.exit(1)

print(f'Video resolution: {video_stream.resolution}')

if args.output is None:
    out_dir = f"outputs/{video_stream.title.lower().replace(' ', '_')}"
else:
    out_dir = f'outputs/{args.output}'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

with open(f'{out_dir}/url.txt', 'w') as f:
    f.write(url)

print('Downloading video for audio...')
video_for_audio = audio_stream.download(
    output_path=out_dir,
    filename='low_res.mp4',
)

print('converting mp4 to mp3...')
subprocess.run(
    [
        'ffmpeg',
        '-i',
        f'{out_dir}/low_res.mp4',
        f'{out_dir}/audio.mp3',
    ]
)
subprocess.run(['rm', '-rf', f'{out_dir}/low_res.mp4'])

# Download high-res video
video = video_stream.download(
    output_path=out_dir,
    filename='no_audio.mp4',
)

# using same output path as input one fails to combine!
combine_audio(
    f'{out_dir}/no_audio.mp4',
    f'{out_dir}/audio.mp3',
    f'{out_dir}/no_caption.mp4',
)
subprocess.run(['rm', '-rf', f'{out_dir}/no_audio.mp4'])

try:
    caption = load_caption(args.video_id)
except BaseException:
    traceback.print_exc()
    print('Failed to load caption.')
    sys.exit(1)

with open(f'{out_dir}/caption.srt', 'w', encoding='utf-8') as f:
    f.write(caption)

add_subtitle_to_video(
    f'{out_dir}/no_caption.mp4',
    f'{out_dir}/caption.srt',
    f'{out_dir}/video.mp4',
)
subprocess.run(['rm', '-rf', f'{out_dir}/no_caption.mp4'])

print(f'Successfully saved a video to {out_dir}.')
