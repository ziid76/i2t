from django.contrib import admin
from .models import OCRResult

@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 's3_url', 'has_ocr_result']
    list_filter = ['created_at']
    search_fields = ['s3_url']
    readonly_fields = ['created_at']
    
    def has_ocr_result(self, obj):
        return bool(obj.ocr_result)
    has_ocr_result.boolean = True
    has_ocr_result.short_description = 'OCR 결과 있음'
