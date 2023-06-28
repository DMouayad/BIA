from io import TextIOWrapper
import os
import shutil
import zipfile
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from bia.services.algo import executeAlgorithm


def index(request: WSGIRequest):
    optimal_sol_file, all_sol_file = executeAlgorithm()
    print(optimal_sol_file)
    return render(request, "index.html")


def downloadOptimalSolutionsFile(request: WSGIRequest):
    temp_dir = "/tmp/download_files"
    file_path = temp_dir + "/optimal_results_steps.txt"
    file_content = open(file_path, "r").read()

    response = HttpResponse(file_content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="optimal_results_steps.txt"'
    return response


def downloadAllSolutions(request):
    temp_dir = "/tmp/download_files"
    file_path = temp_dir + "/all_results_steps.txt"
    file_content = open(file_path, "r").read()

    response = HttpResponse(file_content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="all_results_steps.txt"'
    return response


def downloadResultFiles(request, files: list[TextIOWrapper]):
    temp_dir = "/tmp/download_files"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    zip_file_path = f"{temp_dir}/result.zip"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, "a") as zip_file:
        for file in files:
            with open(file.name, "r") as file_object:
                zip_file.write(file_object.name, arcname=file_object.name)
        print(zip_file.filelist)
        # response = HttpResponse(
        #     FileWrapper(open(zip_file_path, "rb")), content_type="application/zip"
        # )
        # response["Content-Disposition"] = f"attachment; filename={zip_file.filename}"
    result_file = open(zip_file_path, "rb")
    response = FileResponse(result_file, zip_file.filename)
    # os.remove(zip_file_path)
    # os.rmdir(temp_dir)
    #     FileWrapper(open(zip_file_path, "rb")), content_type="application/zip"
    # )
    # response["Content-Disposition"] = f"attachment; filename={zip_file.filename}"

    return response
