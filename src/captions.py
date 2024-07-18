import re
import traceback
from datetime import timedelta
from typing import TypedDict

import ffmpeg  # type: ignore
from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from youtube_transcript_api.formatters import SRTFormatter  # type: ignore


def load_caption(
    video_id: str,
    formatter=SRTFormatter(),
):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatted = formatter.format_transcript(transcript)
    return formatted


def download_caption(video_id: str, output_file: str):
    try:
        caption = load_caption(video_id)
    except BaseException:
        traceback.print_exc()
        print('Failed to load caption.')
        return False

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(caption)
    return True


def add_subtitle_to_video(
    input_video: str,
    subtitle_file: str,
    output_file: str,
    subtitle_language='a.en',
):
    video_input_stream = ffmpeg.input(input_video)
    subtitle_input_stream = ffmpeg.input(subtitle_file)
    subtitle_track_title = subtitle_file.replace('.srt', '')

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


def strptime(time_str: str, format='%H:%M:%S,%f'):
    """
    Parse time str.
    Args:
        time_str: time string to parse(formatted)
        format: format of time string
    Returns:
        Total seconds of timedelta.
    """
    pattern = re.compile(
        r'(?P<hour>\d+):(?P<min>\d\d):(?P<sec>\d\d),(?P<ms>\d\d\d)'
    )
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

class CaptionData(TypedDict):
    index: int
    start: float
    end: float
    duration: float
    text: str


def convert_srt(file_path: str):
    """Convert srt to formatted list of dict."""
    with open(file_path, 'r') as f:
        srt_text = f.read()

    pattern = re.compile(
        r'(?P<index>^\d+$)\n(?P<start>^\d+:\d\d:\d\d,\d\d\d) --> (?P<end>\d+:\d\d:\d\d,\d\d\d$)\n(?P<text>^((.*)+\n)+?$)',
        re.MULTILINE,
    )

    result: list[CaptionData] = []
    for match in pattern.finditer(srt_text):
        start = strptime(match.group('start'))
        end = strptime(match.group('end'))
        text = match.group('text').replace(u'\xa0', u' ').replace('\n', '').strip()
        result.append(
            {
                'index': int(match.group('index')),
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
            converted_item['duration'] = round(item['end'] - converted_item['start'], 3)
            converted.append(converted_item)
            index += 1
            converted_item = {'text': ''}  # type: ignore
        else:
            continue

    return converted
