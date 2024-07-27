import spacy


def test_en_core_web_sm_installed():
    assert spacy.load('en_core_web_sm')
