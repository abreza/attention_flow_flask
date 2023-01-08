import os
import json

from .base import Loader, VideoType


class Activitynet200Loader(Loader):
    def __init__(self) -> None:
        super().__init__()
        self.data_file_path = os.path.abspath("app/datasets/activitynet200/train.json")
        self.result_dir_path = os.path.abspath("app/results/activitynet200")
        self.result_file_path = os.path.abspath("app/results/activitynet200/data.json")
        self.load()

    def load(self):
        with open(self.data_file_path, "r") as f:
            self.train_data = json.load(f)
        for video_id in self.train_data:
            item = self.train_data[video_id]
            item["id"] = video_id
            item["video"] = {"type": VideoType.YOUTUBE.name, "id": video_id[2:]}
            del item["duration"]
            item["segments"] = [
                {"cap": cap, "time": time}
                for cap, time in zip(item["sentences"], item["timestamps"])
            ]
            del item["sentences"]
            del item["timestamps"]
        with open(self.result_file_path, "r") as f:
            self.result_data = json.load(f)
