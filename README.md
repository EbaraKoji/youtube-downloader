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
$ python src/main.py <YOUTUBE_ID> -m audio -o music -c 0 --metadata false -f favorite_song
```

This command saves the audio data of <YOUTUBE_ID> to `outputs/music/favorite_song.mp3`. No video, captions, or url.txt.
