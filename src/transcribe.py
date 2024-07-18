import whisper  # type: ignore
from captions import CaptionData, caption_to_srt


def generate_caption(
    audio_path: str,
    model_name='base',
    translate_to: str | None = None,
):
    model = whisper.load_model(model_name)
    if translate_to is None:
        result = model.transcribe(audio_path)
    else:
        # XXX: Whisper cannot translate English to other language
        result = model.transcribe(
            audio_path, task='translate', language=translate_to
        )

    segments = result['segments']

    caption: list[CaptionData] = [
        {
            'index': i + 1,
            'start': round(item['start'], 3),
            'end': round(item['end'], 3),
            'duration': round(item['end'] - item['start'], 3),
            'text': item['text'].strip(),
        }
        for (i, item) in enumerate(segments)
    ]

    return caption


def generate_srt(
    audio_path: str,
    save_path: str,
    model_name='base',
    translate_to: str | None = None,
):
    caption = generate_caption(audio_path, model_name, translate_to)
    caption_to_srt(caption, save_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        help='path for audio file and output srt file',
    )
    args = parser.parse_args()

    generate_srt(
        f'outputs/{args.path}/audio.mp3',  # default download file_name
        f'outputs/{args.path}/whisper.srt',
    )
