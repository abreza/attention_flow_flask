import os
import json

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

from random import shuffle

from app.Loader.base import TaskType
from app.Loader.activitynet200 import Activitynet200Loader
from app.Loader.msrvtt import MSR_VTTLoader


app = Flask(__name__)

loaders = {"activitynet200": Activitynet200Loader(), "msr-vtt": MSR_VTTLoader()}
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

    not_exist = request.args.get("not_exist")
    if not_exist:
        loaders[dataset].not_exist(task_type, id)
        return ""


    if "file" not in request.files:
        return "No file part!", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file!", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(loaders[dataset].result_dir_path, filename)
    file.save(file_path)

    meta = json.loads(request.form.get('meta', {}))
    loaders[dataset].update(task_type, id, meta, filename)
    return file_path

@app.route("/get-result/<dataset>/<id>/<task_type>", methods=["GET"])
def get_result(dataset, id, task_type):
    if not task_type or task_type not in task_types.keys():
        return "Invalid task type!", 400
    task_type = task_types[task_type]

    if dataset not in loaders:
        return "Dataset Not Found!", 404
    
    res = loaders[dataset].get_result(task_type, id)

    return jsonify(res)

@app.route("/get-file/<dataset>/<task_type>/<file_name>/", methods=["GET"])
def get_result_file(dataset, task_type, file_name):
    if not task_type or task_type not in task_types.keys():
        return "Invalid task type!", 400
    task_type = task_types[task_type]

    if dataset not in loaders:
        return "Dataset Not Found!", 404
    
    file_path = loaders[dataset].get_file_path(task_type, file_name)
    print(file_path)
    return send_file(file_path, as_attachment=True)
