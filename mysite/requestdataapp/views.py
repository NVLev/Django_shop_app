from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .validators import validate_file_size, validate_file_name
from .forms import UserBioForm, UploadFileForm


def process_get_view(request:HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)

def user_form(request:HttpRequest)-> HttpResponse:
    context = {
            "form": UserBioForm(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            your_file = form.cleaned_data["file"]
            fs = FileSystemStorage()
            filenname = fs.save(your_file.name, your_file)
            print(f"saved file, {filenname}")
        # else:
        #     return render(request, 'requestdataapp/size_error_handler.html')
    else:
        form = UploadFileForm()
    context = {
            "form": form
    }

    return render(request, 'requestdataapp/file-upload.html', context=context)


