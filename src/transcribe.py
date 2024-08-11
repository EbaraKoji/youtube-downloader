from itertools import chain

import whisper  # type: ignore
from captions import CaptionData, WordTimestamp, save_caption


def generate_transcribed_caption(
    audio_path: str,
    model_name='base',
    translate_to: str | None = None,
    save_path: str | None = None,
    verbose=True,
):
    model = whisper.load_model(model_name)
    if translate_to is None:
        result = model.transcribe(
            audio_path,
            verbose=verbose,
            word_timestamps=True,
        )
    else:
        # XXX: Whisper cannot translate English to other language
        result = model.transcribe(
            audio_path,
            task='translate',
            language=translate_to,
            verbose=verbose,
            word_timestamps=True,
        )

    segments = result['segments']
    word_timestamps: list[WordTimestamp] = list(
        chain(*[item['words'] for item in result['segments']])
    )

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

    if save_path is not None:
        save_caption(caption, save_path)

    return caption, word_timestamps


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dir',
        '-d',
        help='target dir of audio file and output caption file',
    )
    parser.add_argument(
        'audio',
        '-a',
        help='audio file name',
        default='audio.mp3',
    )
    parser.add_argument(
        '--model',
        help='model name',
        default='base',
    )
    args = parser.parse_args()

    generate_transcribed_caption(
        f'{args.dir}/{args.audio}',  # default download file_name
        model_name=args.model,
        save_path=f'{args.dir}/whisper.vtt',
    )
