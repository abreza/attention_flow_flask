from flask import Flask, request, jsonify

from random import shuffle

from app.Loader.base import TaskType
from app.Loader.activitynet200 import Activitynet200Loader


app = Flask(__name__)

loaders = {"activitynet200": Activitynet200Loader()}
task_types = {
    "attention_flow": TaskType.ATTENTION_FLOW,
    "score_frames": TaskType.SCORE_FRAMES,
}


@app.route("/get-task/<task_type>", methods=["GET"])
def get_task(task_type):
    dataset = request.args.get("dataset")
    id = request.args.get("id")
    new = request.args.get("new", True)

    if not task_type or task_type not in task_types.keys():
        return "Invalid task type!", 400
    task_type = task_types[task_type]
    if dataset:
        if dataset not in loaders.keys():
            return "Dataset Not Found!", 404
        datasets = [dataset]
    else:
        datasets = loaders.keys()
    shuffle(datasets)
    for dataset in datasets:
        task = loaders[dataset].get_task(task_type, id, new)
        if task:
            task["dataset"] = dataset
            return jsonify(task)
    return "No Task Found!", 404


@app.route("/set-result/<dataset>/<id>/<task_type>", methods=["POST"])
def set_result(dataset, id, task_type):
    if not task_type or task_type not in task_types.keys():
        return "Invalid task type!", 400
    task_type = task_types[task_type]

    if dataset not in loaders:
        return "Dataset Not Found!", 404
    loaders[dataset].update(task_type, id, request.json["results"])

    return "No Task Found!", 404
