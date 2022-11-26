import time
import random
import json

from typing import Optional
from abc import ABC, abstractmethod
from enum import Enum

from werkzeug.exceptions import NotFound


class TaskType(Enum):
    ATTENTION_FLOW = 0
    SCORE_FRAMES = 1


class VideoType(Enum):
    YOUTUBE = 0
    DIRECT_LINK = 1


class Loader(ABC):
    @abstractmethod
    def load(self):
        pass

    def filter_tasks(self, process_timeout=100):
        now = int(time.time())
        return [
            key
            for key in self.train_data
            if now - self.train_data[key].get("processing_time", 0) > process_timeout
        ]

    def get_task(self, task_type: TaskType, id: Optional[str], new=True):
        if id:
            if id not in self.train_data:
                raise NotFound("Item Not Found!")
            return self.train_data[id]

        train_keys = self.filter_tasks()
        if new:
            result_keys = self.result_data[task_type.name].keys()
            candidate_keys = [key for key in train_keys if key not in result_keys]
        else:
            candidate_keys = train_keys
        task_key = random.choice(candidate_keys)
        self.train_data[task_key]["processing_time"] = int(time.time())
        return self.train_data[task_key]

    def update(self, task_type: TaskType, id: str, result):
        if id not in self.result_data[task_type.name]:
            self.result_data[task_type.name][id] = {}
        self.result_data[task_type.name][id]["result"] = result

        with open(self.result_file_path, "w") as f:
            json.dumps(self.result_data, f, indent=2)
