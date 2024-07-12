import pytube

url = 'https://www.youtube.com/watch?v=Za8CrPqQxpA'

yt = pytube.YouTube(url)
yt.bypass_age_gate()
print(yt.caption_tracks)
assert 'a.en' in yt.captions.keys()
caption = yt.captions['a.en']


# XXX: KeyError: 'start'
# issue still open: https://github.com/pytube/pytube/issues/1625
print(caption.generate_srt_captions())
