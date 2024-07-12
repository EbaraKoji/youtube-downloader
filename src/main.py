import argparse
from distutils.util import strtobool  # type: ignore

from loader import download_and_save_audio, download_and_save_video

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
    help='download mode(video/audio)',
    default='video',
    required=False,
)
parser.add_argument(
    '--resolution',
    '-r',
    help='video resolution',
    required=False,
)
parser.add_argument(
    '--caption',
    '-c',
    help='download caption',
    default=1,
    type=strtobool,
    required=False,
)
parser.add_argument(
    '--metadata',
    help='add metadata',
    default=1,
    type=strtobool,
    required=False,
)
parser.add_argument(
    '--filename',
    '-f',
    help='file name to save (video/audio/caption)',
    default=None,
    required=False,
)
args = parser.parse_args()

if args.resolution is None:
    resolutions = ['1080p', '720p']
else:
    resolutions = args.resolution

if args.mode == 'video':
    download_and_save_video(
        video_id=args.video_id,
        resolutions=resolutions,
        out_dir=args.output,
        with_caption=bool(args.caption),
        make_metadata=bool(args.metadata),
        file_name=args.filename,
    )
elif args.mode == 'audio':
    download_and_save_audio(
        video_id=args.video_id,
        out_dir=args.output,
        with_caption=bool(args.caption),
        make_metadata=bool(args.metadata),
        file_name=args.filename,
    )
else:
    raise ValueError('args.mode should be "video" or "audio".')
