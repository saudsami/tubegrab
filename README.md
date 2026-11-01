# tubegrab

`tubegrab.py` downloads a list of YouTube videos and saves each one as an
MP3 audio file, a 720p MP4 video file, or both. Each file includes title and
artist tags, and the video thumbnail as cover art.

## Before you begin

Install the following:

- Python 3.8 or later.
- yt-dlp:

  ```powershell
  pip install -U yt-dlp
  ```

- FFmpeg, available on your `PATH`:

  ```powershell
  winget install Gyan.FFmpeg
  ```

  After you install FFmpeg, restart your terminal so that it can find FFmpeg.

- Optional: Deno, which yt-dlp uses to read YouTube pages reliably:

  ```powershell
  winget install DenoLand.Deno
  ```

## Download audio

By default, the script saves the audio of each video as an MP3 file.

1. Add YouTube links to `urls.txt`, one per line. Blank lines and lines that
   start with `#` are ignored, so you can add comments:

   ```text
   # my playlist
   https://www.youtube.com/watch?v=nB8qiZ12Yrk
   https://www.youtube.com/watch?v=jPw0GVu_l-I
   ```

1. From the project folder, run the script:

   ```powershell
   python tubegrab.py urls.txt --out songs
   ```

The MP3 files are saved in the `songs` folder.

To download new songs later, add their links to `urls.txt` and run the same
command. The script skips videos that it already downloaded.

## Download videos

To save each video as an MP4 file instead of an MP3, add `--type mp4`. This
example saves the videos in a `videos` folder:

```powershell
python tubegrab.py urls.txt --out videos --type mp4
```

To save both an MP3 and an MP4 for each video in the same folder, use
`--type both`:

```powershell
python tubegrab.py urls.txt --out songs --type both
```

Videos are saved at 720p, or at the highest resolution available if the
video is smaller than 720p. The script prefers H.264 video, which plays on
almost any device.

## Options

| Option | Description | Default |
| --- | --- | --- |
| `--out FOLDER` | The folder to save the files in. | The current folder |
| `--type TYPE` | What to save: `mp3` for audio, `mp4` for 720p video, or `both`. | `mp3` |
| `--quality KBPS` | The MP3 bitrate: `128`, `192`, `256`, or `320`. This option doesn't affect MP4 files. | `192` |

For example, to save MP3 files at 320 kbps:

```powershell
python tubegrab.py urls.txt --out songs --quality 320
```

## Files the script creates

The script creates these files in the output folder:

- `archive.txt` and `archive_mp4.txt`: the IDs of videos that the script
  already downloaded as MP3 and MP4 files. To download every video again,
  delete the file for that type.
- `failed_urls.txt`: the links that failed to download, if any. To retry them,
  run the script with this file:

  ```powershell
  python tubegrab.py songs\failed_urls.txt --out songs
  ```

  If you used `--type`, add the same `--type` value to this command.

  The script deletes this file after a run in which every download succeeds.

## Troubleshooting

**"FFmpeg was not found on your PATH"**

Restart your terminal or VS Code after you install FFmpeg. If the error
persists, check that `ffmpeg -version` works in the same terminal.

**Downloads start failing**

YouTube changes often. Update yt-dlp, and then run the script again:

```powershell
pip install -U yt-dlp
```
