import os

import magic
from django.core.exceptions import ValidationError


def validate_uploaded_file_extension(value, valid_mime_types, valid_file_extensions, error_message):
    file_mime_type = magic.from_buffer(value.read(1024), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError(error_message)

    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in valid_file_extensions:
        raise ValidationError(f"Unacceptable file extension. Expected one of {valid_file_extensions}")


def validate_uploaded_image_extension(value):
    valid_mime_types = ["image/svg+xml", "image/jpeg", "image/png"]
    valid_file_extensions = [".svg", ".jpg", ".png"]
    error_message = "Unsupported image file type."
    validate_uploaded_file_extension(value, valid_mime_types, valid_file_extensions, error_message)


def validate_uploaded_pdf_extension(value):
    valid_mime_types = ["image/jpeg", "application/pdf"]
    valid_file_extensions = [".pdf", ".jpg", ".jpeg"]
    error_message = "Unsupported upload file type."
    validate_uploaded_file_extension(value, valid_mime_types, valid_file_extensions, error_message)


def validate_uploaded_zip_extension(value):
    valid_mime_types = ["application/x-7z-compressed", "application/gzip", "application/zip"]
    valid_file_extensions = [".zip", ".7z", ".gz"]
    error_message = "Unsupported upload file type."
    validate_uploaded_file_extension(value, valid_mime_types, valid_file_extensions, error_message)
