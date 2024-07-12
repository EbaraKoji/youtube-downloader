import argparse

from loader import download_and_make_captioned_video, download_audio_caption

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

if args.resolution is None:
    resolutions = ['1080p', '720p']
else:
    resolutions = args.resolution

if args.mode == 'mp4':
    download_and_make_captioned_video(args.video_id, resolutions, args.output)
elif args.mode == 'mp3':
    download_audio_caption(args.video_id, args.output)
