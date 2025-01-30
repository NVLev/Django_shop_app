from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.core.files.uploadedfile import InMemoryUploadedFile


def validate_file_size(value):
    filesize = value

    if filesize > 1024:
        return False

    return True

def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and "virus" in file.name:
        raise ValidationError("file name should not contain 'virus")