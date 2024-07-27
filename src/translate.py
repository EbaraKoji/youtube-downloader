import math
import os
from typing import TypedDict

import requests  # type: ignore
from captions import (
    CaptionData,
    caption_to_sentences,
    load_caption_file,
    save_caption,
)
from dotenv import load_dotenv

load_dotenv()


class DeeplResponse(TypedDict):
    status_code: int
    translations: list[str] | None


# TODO: create args class for cleaner inheritance
def deepl_translate(
    text: str | list[str],
    source_lang='EN',
    target_lang='JA',
    api_key=os.environ.get('DEEPL_API_KEY'),
) -> DeeplResponse:
    res = requests.post(
        'https://api-free.deepl.com/v2/translate',
        headers={'Authorization': f'DeepL-Auth-Key {api_key}'},
        data={
            'text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
        },
    )

    # TODO: log errors
    if res.status_code != 200:
        return {
            'status_code': res.status_code,
            'translations': None,
        }

    return {
        'status_code': res.status_code,
        'translations': [item['text'] for item in res.json()['translations']],
    }


def translate_captions(
    caption: list[CaptionData],
    source_lang='EN',
    target_lang='JA',
    deepl_api_key=os.environ.get('DEEPL_API_KEY'),
    num_batches=500,
) -> list[CaptionData] | None:
    if num_batches < 1 or num_batches > 500:
        raise ValueError('num_batches should be between 1 and 500 integer.')

    translated: list[CaptionData] = []

    num_requests = math.ceil(len(caption) / num_batches)

    for i in range(num_requests):
        caption_batch = caption[i * num_batches : (i + 1) * num_batches]
        deepl_response = deepl_translate(
            text=[item['text'] for item in caption_batch],
            source_lang=source_lang,
            target_lang=target_lang,
            api_key=deepl_api_key,
        )

        # TODO: more sophisticated error handling
        if deepl_response['translations'] is None:
            break
        if len(deepl_response['translations']) != len(caption_batch):
            break

        new_captions: list[CaptionData] = [
            {**item, 'text': res_text}
            for (item, res_text) in zip(
                caption_batch, deepl_response['translations']
            )
        ]

        translated.extend(new_captions)

    return translated


def create_translated_caption(
    file_path: str,
    save_path: str,
    trim_caption_to_sentences=True,
    source_lang='EN',
    target_lang='JA',
    deepl_api_key=os.environ.get('DEEPL_API_KEY'),
    num_batches=500,
):
    caption = load_caption_file(file_path)
    if trim_caption_to_sentences is True:
        caption = caption_to_sentences(caption)

    translated_caption = translate_captions(
        caption, source_lang, target_lang, deepl_api_key, num_batches
    )

    if translated_caption is None:
        print('failed to translate caption.')
        return

    save_caption(translated_caption, save_path)


def combine_captions(cap_1: list[CaptionData], cap_2: list[CaptionData]):
    if len(cap_1) != len(cap_2):
        raise ValueError('both captions should be the same index length.')

    new_cap: list[CaptionData] = [
        {
            **item_1,
            'text': item_1['text'] + '\n' + item_2['text'],
        }
        for (item_1, item_2) in zip(cap_1, cap_2)
    ]

    return new_cap


def combine_translated_captions(
    raw_caption_path: str,
    translated_caption_path: str,
    save_path: str,
):
    raw_cap = load_caption_file(raw_caption_path)
    translated_cap = load_caption_file(translated_caption_path)
    new_cap = combine_captions(raw_cap, translated_cap)
    save_caption(new_cap, save_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        help='path for caption file and output translated caption file',
    )
    args = parser.parse_args()

    create_translated_caption(
        f'outputs/{args.path}/whisper.vtt',  # need srt file with puncts for caption_to_sentences!
        f'outputs/{args.path}/translated.vtt',
    )
