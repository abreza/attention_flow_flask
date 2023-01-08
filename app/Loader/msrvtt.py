import json

from .base import Loader, VideoType


class MSR_VTTLoader(Loader):
    def __init__(self) -> None:
        super().__init__()
        self.data_file_path = (
            "app/datasets/msr-vtt/train_val_annotation/train_val_videodatainfo.json"
        )
        self.result_file_path = "app/results/msr-vtt.json"
        self.load()

    def load(self):
        self.train_data = {}
        with open(self.data_file_path, "r") as f:
            train_file = json.load(f)
        for video in train_file["videos"]:
            video_id = video["video_id"]
            youtube_video_id = video["url"].replace(
                "https://www.youtube.com/watch?v=", ""
            )
            captions = [
                item["caption"]
                for item in train_file["sentences"]
                if item["video_id"] == video_id
            ]
            self.train_data[youtube_video_id] = {
                "id": video_id,
                "video": {"type": VideoType.YOUTUBE.name, "id": video_id},
                "segments": [
                    {"cap": cap, "time": [video["start time"], video["end time"]]}
                    for cap in captions
                ],
            }

        with open(self.result_file_path, "r") as f:
            self.result_data = json.load(f)
