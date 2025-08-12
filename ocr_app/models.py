from django.db import models
import json

class OCRResult(models.Model):
    image_file = models.ImageField(upload_to='uploads/', blank=True, null=True)  # ← 추가
    s3_url = models.URLField(max_length=500)
    ocr_result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OCR Result {self.id} - {self.created_at}"
    
def _safe_cell_text(self, cell: dict) -> str:
    """셀에서 텍스트를 안전하게 추출 (빈 리스트/누락 key에 견고)"""
    parts = []
    for line in (cell.get("cellTextLines") or []):
        for w in (line.get("cellWords") or []):
            t = w.get("inferText")
            if t:
                parts.append(str(t))
    # 일부 엔진은 셀 레벨 inferText만 있을 수 있음
    if not parts:
        t = cell.get("inferText")
        if t:
            parts.append(str(t))
    return " ".join(parts).strip()

def get_table_data(self):
    """OCR 결과에서 테이블 2차원 배열 목록을 추출"""
    if not self.ocr_result or not isinstance(self.ocr_result, dict):
        return []

    tables_out = []
    images = self.ocr_result.get("images") or []

    for image in images:
        for table in (image.get("tables") or []):
            cells = table.get("cells") or []

            # rowSpan/colSpan 감안하여 테이블 크기 산정
            max_row = 0
            max_col = 0
            for cell in cells:
                r = int(cell.get("rowIndex", 0) or 0)
                c = int(cell.get("columnIndex", 0) or 0)
                rspan = int(cell.get("rowSpan", 1) or 1)
                cspan = int(cell.get("columnSpan", 1) or 1)
                max_row = max(max_row, r + rspan)
                max_col = max(max_col, c + cspan)

            if max_row <= 0 or max_col <= 0:
                continue

            table_matrix = [[""] * max_col for _ in range(max_row)]

            # 앵커 위치에만 텍스트를 채움(스팬 확장은 필요시 추가로 구현)
            for cell in cells:
                r = int(cell.get("rowIndex", 0) or 0)
                c = int(cell.get("columnIndex", 0) or 0)
                if r < 0 or c < 0 or r >= max_row or c >= max_col:
                    continue
                text = self._safe_cell_text(cell)
                table_matrix[r][c] = text

            tables_out.append(table_matrix)

    return tables_out

def get_bounding_boxes(self):
    """OCR 결과에서 바운딩 박스 정보 추출 (빈 값 안전 처리)"""
    if not self.ocr_result or not isinstance(self.ocr_result, dict):
        return []

    boxes = []
    images = self.ocr_result.get("images") or []
    for image in images:
        for table in (image.get("tables") or []):
            for cell in (table.get("cells") or []):
                bp = cell.get("boundingPoly") or {}
                vertices = bp.get("vertices") or []
                if isinstance(vertices, list) and len(vertices) >= 4:
                    boxes.append({
                        "vertices": vertices,
                        "text": self._safe_cell_text(cell)
                    })
    return boxes