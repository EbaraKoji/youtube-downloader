from pytube.innertube import _default_clients  # type: ignore


def setup_default_clients():
    """
    Deal with 400:Bad Request.
    see https://github.com/pytube/pytube/issues/1973#issuecomment-2232578734.
    """
    _default_clients['ANDROID']['context']['client']['clientVersion'] = '19.08.35'
    _default_clients['IOS']['context']['client']['clientVersion'] = '19.08.35'
    _default_clients['ANDROID_EMBED']['context']['client']['clientVersion'] = (
        '19.08.35'
    )
    _default_clients['IOS_EMBED']['context']['client']['clientVersion'] = (
        '19.08.35'
    )
    _default_clients['IOS_MUSIC']['context']['client']['clientVersion'] = '6.41'
    _default_clients['ANDROID_MUSIC'] = _default_clients['ANDROID_CREATOR']