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

### Specifing resolution and output directory
```
$ python src/main.py <YOUTUBE_ID> -r 720p -o Download
```

### Downloading audio(with captions)
```
$ python src/main.py <YOUTUBE_ID> -m audio
```

