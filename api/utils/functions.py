
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(uploaded_image, quality=20):
    """
    Compresses an uploaded image file in JPEG format.

    This function takes an `uploaded_image` object, which is assumed to be a Django 
    `UploadedFile` instance, and compresses it using Pillow (PIL Fork). 

    **Arguments:**
    * uploaded_image (UploadedFile): The image file to be compressed.
    * quality (int, optional): The JPEG quality (0-100), with higher values resulting in 
        less compression and larger file sizes. Defaults to 85.

    **Returns:**
    An `InMemoryUploadedFile` object containing the compressed image data. This 
    object can be used directly with Django model fields that expect an image file.

    **Raises:**
    * ValueError: If the uploaded_image format is not supported by Pillow.

    **Note:**
    This function opens the uploaded image in memory, which might not be suitable 
    for very large images. Consider alternative approaches for handling large files.
    """
    image = Image.open(uploaded_image)
    output = BytesIO()
    image.save(output, format='JPEG', quality=quality)
    output.seek(0)

    return InMemoryUploadedFile(output, 'ImageField', uploaded_image.name, 'image/jpeg', output.tell(), None)

