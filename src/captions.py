import traceback

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
