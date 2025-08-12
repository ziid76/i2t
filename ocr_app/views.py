from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import ImageUploadForm
from .models import OCRResult
from .utils import upload_to_s3, call_naver_ocr_api, save_ocr_result_to_file
import json
from io import BytesIO

def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            up = request.FILES.get('image_file')
            if not up:
                messages.error(request, '파일이 없습니다.')
                return redirect('index')

            # 업로드 스트림 → 메모리 복사(한 번만 read)
            blob = up.read()
            buf = BytesIO(blob)

            # S3 업로드 (file-like 사용)
            buf.seek(0)
            s3_url = upload_to_s3(buf, up.name)
            if not s3_url:
                messages.error(request, 'S3 업로드에 실패했습니다.')
                return redirect('index')

            # 모델 저장 (image_file은 비워둠)
            ocr_result = form.save(commit=False)
            ocr_result.image_file = None
            ocr_result.s3_url = s3_url

            # OCR 호출
            ocr_response = call_naver_ocr_api(s3_url)
            if not ocr_response:
                messages.error(request, 'OCR API 호출에 실패했습니다.')
                return redirect('index')

            ocr_result.ocr_result = ocr_response
            ocr_result.save()

            save_ocr_result_to_file(ocr_response)
            messages.success(request, 'OCR 처리가 완료되었습니다.')
            return redirect('ocr_result', pk=ocr_result.pk)
    else:
        form = ImageUploadForm()
    return render(request, 'ocr_app/index.html', {'form': form})

def ocr_result(request, pk):
    """OCR 결과 페이지"""
    try:
        ocr_result = OCRResult.objects.get(pk=pk)
        table_data = ocr_result.get_table_data()
        bounding_boxes = ocr_result.get_bounding_boxes()
        
        context = {
            'ocr_result': ocr_result,
            'table_data': table_data,
            'bounding_boxes': json.dumps(bounding_boxes),
            'image_url': ocr_result.image_file.url if ocr_result.image_file else ocr_result.s3_url
        }
        
        return render(request, 'ocr_app/result.html', context)
    
    except OCRResult.DoesNotExist:
        messages.error(request, '결과를 찾을 수 없습니다.')
        return redirect('index')

def get_ocr_results(request):
    """OCR 결과 목록 API"""
    results = OCRResult.objects.all().order_by('-created_at')[:10]
    data = []
    
    for result in results:
        data.append({
            'id': result.id,
            'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': result.image_file.url if result.image_file else result.s3_url,
            'has_result': bool(result.ocr_result)
        })
    
    return JsonResponse({'results': data})
