from django import forms
from .models import OCRResult

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = OCRResult
        fields = ['image_file']
        widgets = {
            'image_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png',
                'id': 'imageFile'
            })
        }
    
    def clean_image_file(self):
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            # 파일 크기 체크 (10MB 제한)
            if image_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("파일 크기는 10MB를 초과할 수 없습니다.")
            
            # 파일 확장자 체크
            allowed_extensions = ['.jpg', '.jpeg', '.png']
            file_extension = image_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError("JPG, JPEG, PNG 파일만 업로드 가능합니다.")
        
        return image_file
