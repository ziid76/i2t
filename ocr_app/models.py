from django.db import models
import json

class OCRResult(models.Model):
    image_file = models.ImageField(upload_to='uploads/')
    s3_url = models.URLField(max_length=500)
    ocr_result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OCR Result {self.id} - {self.created_at}"
    
    def get_table_data(self):
        """OCR 결과에서 테이블 데이터 추출"""
        if not self.ocr_result:
            return []
        
        tables = []
        images = self.ocr_result.get('images', [])
        
        for image in images:
            if 'tables' in image:
                for table in image['tables']:
                    table_data = []
                    cells = table.get('cells', [])
                    
                    # 셀을 행과 열로 정렬
                    max_row = max([cell.get('rowIndex', 0) for cell in cells]) + 1 if cells else 0
                    max_col = max([cell.get('columnIndex', 0) for cell in cells]) + 1 if cells else 0
                    
                    # 테이블 초기화
                    table_matrix = [[''] * max_col for _ in range(max_row)]
                    
                    # 셀 데이터 채우기
                    for cell in cells:
                        row_idx = cell.get('rowIndex', 0)
                        col_idx = cell.get('columnIndex', 0)
                        text = cell.get('cellTextLines', [{}])[0].get('cellWords', [{}])[0].get('inferText', '')
                        table_matrix[row_idx][col_idx] = text
                    
                    tables.append(table_matrix)
        
        return tables
    
    def get_bounding_boxes(self):
        """OCR 결과에서 바운딩 박스 정보 추출"""
        if not self.ocr_result:
            return []
        
        boxes = []
        images = self.ocr_result.get('images', [])
        
        for image in images:
            if 'tables' in image:
                for table in image['tables']:
                    cells = table.get('cells', [])
                    for cell in cells:
                        bounding_poly = cell.get('boundingPoly')
                        if bounding_poly:
                            vertices = bounding_poly.get('vertices', [])
                            if len(vertices) >= 4:
                                boxes.append({
                                    'vertices': vertices,
                                    'text': cell.get('cellTextLines', [{}])[0].get('cellWords', [{}])[0].get('inferText', '')
                                })
        
        return boxes
