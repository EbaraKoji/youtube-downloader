import argparse
import os
from distutils.util import strtobool  # type: ignore

from captions import CaptionExt
from clients import setup_default_clients
from dotenv import load_dotenv
from loader import download_and_save_video

load_dotenv()

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
    '--srt',
    help='download srt caption',
    default=0,
    type=strtobool,
    required=False,
)

parser.add_argument(
    '--vtt',
    help='download vtt caption',
    default=1,
    type=strtobool,
    required=False,
)

parser.add_argument(
    '--txt',
    help='download txt caption',
    default=0,
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
parser.add_argument(
    '--download_only',
    help='whether to download_only',
    default=0,
    type=strtobool,
    required=False,
)
parser.add_argument(
    '--transcribe',
    help='whether to transcribe caption',
    default=0,
    type=strtobool,
    required=False,
)
parser.add_argument(
    '--translate',
    help='whether to translate caption',
    default=0,
    type=strtobool,
    required=False,
)
args = parser.parse_args()

setup_default_clients()

if args.resolution is None:
    resolutions = ['1080p', '720p']
else:
    resolutions = args.resolution

exts: set[CaptionExt] = set()
if bool(args.srt) is True:
    exts.add(CaptionExt.SRT)
if bool(args.vtt) is True:
    exts.add(CaptionExt.VTT)
if bool(args.txt) is True:
    exts.add(CaptionExt.TXT)


download_and_save_video(
    video_id=args.video_id,
    mode=args.mode,
    resolutions=resolutions,
    out_dir=args.output,
    caption_exts=exts,
    make_metadata=bool(args.metadata),
    file_name=args.filename,
    download_only=bool(args.download_only),
    transcribe=bool(args.transcribe),
    translate=bool(args.translate),
    deepl_api_key=os.environ.get('DEEPL_API_KEY'),
)
