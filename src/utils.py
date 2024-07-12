# https://stackoverflow.com/questions/63881088/how-to-merge-mp3-and-mp4-in-python-mute-a-mp4-file-and-add-a-mp3-file-on-it
import moviepy.editor as mpe  # type: ignore


def combine_audio(vidname: str, audname: str, outname: str, fps=60):
    if vidname == outname:
        raise ValueError(
            'using same outname as vidname causes combining bugs!'
        )
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname, fps=fps)


if __name__ == '__main__':
    combine_audio(
        'outputs/video/sample.mp4',
        'outputs/audio/sample.mp3',
        'outputs/video/sample_over.mp4',
    )
