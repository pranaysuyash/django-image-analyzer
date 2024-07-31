from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .utils import analyze_image_with_openai
from django.conf import settings
from .models import Image
import os
from django.db.models import Q

def image_upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.save()
            image_full_path = os.path.join(settings.MEDIA_ROOT, image_instance.image.name)
            
            analysis_result = analyze_image_with_openai(image_full_path)
            if analysis_result['status'] == "success":
                image_instance.tags = analysis_result['tags']
                image_instance.save()
                return render(request, 'gallery/image_upload_success.html', {'image': image_instance})
            else:
                form.add_error(None, "Failed to analyze image: " + analysis_result['message'])
    else:
        form = ImageUploadForm()
    return render(request, 'gallery/image_upload.html', {'form': form})

def image_upload_success(request):
    return render(request, 'gallery/image_upload_success.html')

def image_search(request):
    query = request.GET.get('query', '').strip()
    matching_images = Image.objects.none()
    if query:
        query_tags = query.split(' ')
        q_objects = Q()
        for tag in query_tags:
            q_objects |= Q(tags__contains=tag)
        matching_images = Image.objects.filter(q_objects).distinct()
    return render(request, 'gallery/image_search.html', {'query': query, 'matching_images': matching_images})