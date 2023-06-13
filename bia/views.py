from io import TextIOWrapper
import os
import shutil
from wsgiref.util import FileWrapper
import zipfile
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from bia.services.algo import executeAlgorithm
from .forms import UploadFilesForm

downloading: bool = False


def index(request: WSGIRequest):
    global downloading
    if request.method == "POST" and not downloading:
        downloading = True
        optimal_sol_file, all_sol_file = executeAlgorithm(
            request.FILES["tasksFile"].file, request.FILES["linksFile"].file
        )
        response = downloadResultFiles(request, [optimal_sol_file, all_sol_file])
        return response
        # form = UploadFilesForm(data=request.FILES)
    else:
        downloading = False
        form = UploadFilesForm(data={"tasksFile": "", "linksFile": ""})
    context = {"form": form}
    return render(request, "index.html", context)


def downloadResultFiles(request, files: list[TextIOWrapper]):
    temp_dir = "/tmp/download_files"
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
