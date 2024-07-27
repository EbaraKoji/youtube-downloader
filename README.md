# Youtube Downloader

Command-line youtube downloader for watching high-resolution videos with captions offline.
Audio(mp3) and captions(srt) files can be also downloaded.

## Setup

To edit videos you need to install ffmpeg.

```
$ brew install ffmpeg
```

First you need to install dependencies.

```
$ pip install -r requirements.lock
```

You can also use [Rye](https://rye.astral.sh/).

```
$ rye sync
```

### Dealing with pytube Error
[issues](https://github.com/pytube/pytube/issues/1954#issuecomment-2218293021)


revise .venv/lib/python3.12/site-packages/pytube/cipher.py in line 264 to the following code.
```
function_patterns = [
        # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
        # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
        # var Bpa = [iha];
        # ...
        # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
        # Bpa.length || iha("")) }};
        # In the above case, `iha` is the relevant function name
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
```


## Usage

### Downloading video(with audio and captions)

```
$ python src/main.py <YOUTUBE_ID>
```

### Specifing resolution

```
$ python src/main.py <YOUTUBE_ID> -r 720p
```

### Downloading audio

```
$ python src/main.py <YOUTUBE_ID> -m audio -o music --srt 0 --metadata false -f favorite_song
```

This command saves the audio data of <YOUTUBE_ID> to `outputs/music/favorite_song.mp3`. No video, captions, or url.txt.
