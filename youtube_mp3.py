#!/usr/bin/env python3
"""
Download YouTube videos and save each as an MP3, a 720p MP4, or both.

Requirements:
    pip install -U yt-dlp
    FFmpeg installed and on your PATH (https://ffmpeg.org/download.html)

Usage:
    python youtube_mp3.py urls.txt
    python youtube_mp3.py urls.txt --out downloads --quality 320
    python youtube_mp3.py urls.txt --out downloads --type both

The URL file should have one YouTube link per line. Blank lines and lines
starting with # are ignored, so you can add comments.
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    from yt_dlp import YoutubeDL
except ImportError:
    sys.exit("yt-dlp is not installed. Run: pip install -U yt-dlp")


def read_urls(path):
    file = Path(path)
    if not file.is_file():
        sys.exit(f"URL file not found: {path}")

    urls = []
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)

    if not urls:
        sys.exit(f"No URLs found in {path}")
    return urls


VIDEO_HEIGHT = 720

# Prefer H.264 video, which plays almost everywhere, with M4A audio so merging
# into MP4 needs no re-encoding. Fall back to other MP4 codecs (such as AV1), then anything.
VIDEO_FORMAT = (
    f"bv*[height<={VIDEO_HEIGHT}][vcodec^=avc1]+ba[ext=m4a]"
    f"/bv*[height<={VIDEO_HEIGHT}][ext=mp4]+ba[ext=m4a]"
    f"/b[height<={VIDEO_HEIGHT}][ext=mp4]"
    f"/bv*[height<={VIDEO_HEIGHT}]+ba"
    f"/b[height<={VIDEO_HEIGHT}]"
)


def build_common_options(out_dir, archive_name):
    return {
        "paths": {"home": str(out_dir)},
        "outtmpl": "%(title)s.%(ext)s",
        # Each type has its own archive, so an MP3 download doesn't skip the MP4
        "download_archive": str(Path(out_dir) / archive_name),
        "noplaylist": True,  # only grab the single video, even if the URL has &list=
        "writethumbnail": True,
    }


def build_audio_options(out_dir, quality):
    return {
        **build_common_options(out_dir, "archive.txt"),
        "format": "bestaudio/best",
        "postprocessors": [
            # YouTube thumbnails are usually WebP, which many players can't show as cover art
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            },
            {"key": "FFmpegMetadata"},  # write title/artist tags into the MP3
            {"key": "EmbedThumbnail"},  # embed the thumbnail as cover art, then delete the image file
        ],
    }


def build_video_options(out_dir):
    return {
        **build_common_options(out_dir, "archive_mp4.txt"),
        "format": VIDEO_FORMAT,
        "merge_output_format": "mp4",
        "postprocessors": [
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ],
    }


def download_all(urls, out_dir=".", quality="192", file_type="mp3"):
    if shutil.which("ffmpeg") is None:
        sys.exit("FFmpeg was not found on your PATH. Install it and try again.")

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    option_sets = []
    if file_type in ("mp3", "both"):
        option_sets.append(build_audio_options(out_dir, quality))
    if file_type in ("mp4", "both"):
        option_sets.append(build_video_options(out_dir))

    succeeded, failed = [], []
    total = len(urls)

    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{total}] {url}", flush=True)
        try:
            for options in option_sets:
                with YoutubeDL(options) as ydl:
                    ydl.download([url])
            succeeded.append(url)
        except Exception as e:
            print(f"  Failed: {e}")
            failed.append(url)

    print(f"\nFinished: {len(succeeded)} succeeded, {len(failed)} failed.")
    failed_file = Path(out_dir) / "failed_urls.txt"
    if failed:
        failed_file.write_text("\n".join(failed) + "\n", encoding="utf-8")
        print(f"Failed URLs saved to {failed_file} so you can retry them.")
        sys.exit(1)
    failed_file.unlink(missing_ok=True)  # clear the list left by an earlier run


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos as MP3 or MP4 from a list of URLs.")
    parser.add_argument("url_file", help="Text file with one YouTube URL per line")
    parser.add_argument("--out", default=".", help="Output folder (default: current folder)")
    parser.add_argument(
        "--type",
        default="mp3",
        choices=["mp3", "mp4", "both"],
        help=f"mp3 for audio, mp4 for {VIDEO_HEIGHT}p video, or both (default: mp3)",
    )
    parser.add_argument(
        "--quality",
        default="192",
        choices=["128", "192", "256", "320"],
        help="MP3 bitrate in kbps (default: 192)",
    )
    args = parser.parse_args()

    urls = read_urls(args.url_file)
    download_all(urls, args.out, args.quality, args.type)


if __name__ == "__main__":
    main()