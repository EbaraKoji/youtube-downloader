import re
import traceback
from datetime import timedelta
from enum import Enum
from typing import TypedDict

import ffmpeg  # type: ignore
from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from youtube_transcript_api.formatters import SRTFormatter, WebVTTFormatter, TextFormatter  # type: ignore


class CaptionData(TypedDict):
    index: int
    start: float
    end: float
    duration: float
    text: str


class CaptionExt(Enum):
    SRT = 'srt'
    VTT = 'vtt'
    TXT = 'txt'


def load_yt_caption(
    video_id: str,
    exts: set[CaptionExt],
):
    if len(exts) == 0:
        raise ValueError('No ext item is provided.')
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatted = {}
    
    if CaptionExt.SRT in exts:
        formatter = SRTFormatter()
        formatted['srt'] = (formatter.format_transcript(transcript))
    
    if CaptionExt.VTT in exts:
        formatter = WebVTTFormatter()
        formatted['vtt'] = (formatter.format_transcript(transcript))

    if CaptionExt.TXT in exts:
        formatter = TextFormatter()
        formatted['txt'] = (formatter.format_transcript(transcript))

    return formatted


def download_caption(video_id: str, output_path: str, exts={CaptionExt.SRT}):
    try:
        captions = load_yt_caption(video_id, exts)
    except BaseException:
        traceback.print_exc()
        print('Failed to load caption.')
        return False

    for key in captions.keys():
        with open(f'{output_path}.{key}', 'w', encoding='utf-8') as f:
            f.write(captions[key])
    
    return True


def add_subtitle_to_video(
    input_video: str,
    subtitle_file: str,
    output_file: str,
    subtitle_language='a.en',
):
    video_input_stream = ffmpeg.input(input_video)
    subtitle_input_stream = ffmpeg.input(subtitle_file)
    subtitle_track_title = subtitle_file[:-3]

    stream = ffmpeg.output(
        video_input_stream,
        subtitle_input_stream,
        output_file,
        **{'c': 'copy', 'c:s': 'mov_text'},
        **{
            'metadata:s:s:0': f'language={subtitle_language}',
            'metadata:s:s:1': f'title={subtitle_track_title}',
        },
    )
    ffmpeg.run(stream, overwrite_output=True)


def strptime(time_str: str, ext=CaptionExt.SRT):
    """
    Parse time str.
    Args:
        time_str: time string to parse(formatted)
        ext: caption extension(srt or vtt).
    Returns:
        Total seconds of timedelta.
    """
    if ext == CaptionExt.SRT:
        pattern = re.compile(
            r'(?P<hour>\d+):(?P<min>\d\d):(?P<sec>\d\d),(?P<ms>\d\d\d)'
        )
    elif ext == CaptionExt.VTT:
        pattern = re.compile(
            r'(?P<hour>\d+):(?P<min>\d\d):(?P<sec>\d\d).(?P<ms>\d\d\d)'
        )
    else:
        raise ValueError('file extension should be .srt or .vtt')

    match = pattern.search(time_str)
    if match is None:
        raise ValueError('Timeformat is not valid.')

    return round(
        timedelta(
            hours=int(match.group('hour')),
            minutes=int(match.group('min')),
            seconds=int(match.group('sec')),
            milliseconds=int(match.group('ms')),
        ).total_seconds(),
        3,
    )


def strftime(t: timedelta | float, ext: CaptionExt):
    """
    Convert time to format string. (format: '%H:%M:%S,%f')

    Args:
        t: timedelta or total_seconds(float).
        ext: caption extension(srt or vtt).
    """
    if isinstance(t, timedelta):
        t = t.total_seconds()

    hours = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int(t % 60)
    milliseconds = int((t - int(t)) // 1000)

    delimiter = ',' if ext == CaptionExt.SRT else '.'
    return f'{hours:02}:{minutes:02}:{seconds:02}{delimiter}{milliseconds:03}'


def load_caption_file(file_path: str):
    """Convert srt to formatted list of dict."""
    if file_path[-3:] == CaptionExt.SRT.value:
        file_ext = CaptionExt.SRT
    elif file_path[-3:] == CaptionExt.VTT.value:
        file_ext = CaptionExt.VTT
    else:
        raise ValueError('file extension should be .srt or .vtt')

    with open(file_path, 'r') as f:
        caption_text = f.read()

    if file_ext == CaptionExt.SRT:
        pattern = re.compile(
            r'(?P<index>(^\d+$\n)?)(?P<start>^\d+:\d\d:\d\d,\d\d\d) --> (?P<end>\d+:\d\d:\d\d,\d\d\d$)\n(?P<text>^((.*)+\n)+?$)',
            re.MULTILINE,
        )
    elif file_ext == CaptionExt.VTT:
        pattern = re.compile(
            r'(?P<index>(^\d+$\n)?)(?P<start>^\d+:\d\d:\d\d\.\d\d\d) --> (?P<end>\d+:\d\d:\d\d\.\d\d\d$)\n(?P<text>^((.*)+\n)+?$)',
            re.MULTILINE,
        )

    result: list[CaptionData] = []
    for i, match in enumerate(pattern.finditer(caption_text)):
        start = strptime(match.group('start'), file_ext)
        end = strptime(match.group('end'), file_ext)
        text = (
            match.group('text').replace('\xa0', ' ').replace('\n', '').strip()
        ).strip()

        result.append(
            {
                'index': int(match.group('index') or i + 1),
                'start': start,
                'end': end,
                'text': text,
                'duration': round((end - start), 3),
            }
        )

    return result


def caption_to_sentences(caption: list[CaptionData]):
    """Convert caption so that each item is whole sentence."""
    converted: list[CaptionData] = []

    converted_item: CaptionData = {'text': ''}  # type: ignore
    index = 1
    for item in caption:
        if 'start' not in converted_item:
            converted_item['start'] = item['start']
            converted_item['index'] = index

        if converted_item['text'] != '':
            converted_item['text'] += ' '
        converted_item['text'] += item['text']

        if item['text'].endswith(('.', '!', '?')):
            converted_item['end'] = item['end']
            converted_item['duration'] = round(
                item['end'] - converted_item['start'], 3
            )
            converted.append(converted_item)
            index += 1
            converted_item = {'text': ''}  # type: ignore
        else:
            continue

    return converted


def convert_caption_item(data: CaptionData, ext=CaptionExt.SRT):
    return f"""{data['index']}
{strftime(data['start'], ext)} --> {strftime(data['end'], ext)}
{data['text']}

"""


def caption_to_txt(caption: list[CaptionData], ext=CaptionExt.SRT):
    caption_text = ''
    if ext == CaptionExt.VTT:
        caption_text += 'WEBVTT\n\n'
    for item in caption:
        caption_text += convert_caption_item(item, ext)
    return caption_text


def save_caption(caption: list[CaptionData], save_path: str):
    if save_path[-3:] == CaptionExt.SRT.value:
        file_ext = CaptionExt.SRT
    elif save_path[-3:] == CaptionExt.VTT.value:
        file_ext = CaptionExt.VTT
    else:
        raise ValueError('save_path extension should be .srt or .vtt')

    caption_text = caption_to_txt(caption, file_ext)

    with open(save_path, 'w') as f:
        f.write(caption_text)
