# Sample srt is downloaded from https://www.youtube.com/watch?v=qWVTjMsv7AE.

from src.captions import convert_srt, CaptionData


def test_convert_srt() -> None:
    caption = convert_srt('tests/sample_caption.srt')
    expected_length = 92
    assert len(caption) == expected_length

    expected_dict: CaptionData = {
        'index': 3,
        'start': 7.200,
        'end': 13.680,
        'duration': 6.480,
        'text': '28 years after the web was conceived, Sir Tim Berners-Lee wrote about 3 trends that worried him.'
    }

    caption_item = caption[2]
    assert caption_item == expected_dict

