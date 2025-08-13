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

                # 테이블 구조 정규화
                normalized_table = self._normalize_table_structure(table_matrix)
                if normalized_table:
                    tables_out.append(normalized_table)

        return tables_out

    def _normalize_table_structure(self, table_matrix):
        """테이블 구조를 정규화하여 DataTable 호환성 향상"""
        if not table_matrix:
            return None
        
        # 최대 컬럼 수 찾기
        max_cols = max(len(row) for row in table_matrix) if table_matrix else 0
        if max_cols == 0:
            return None
        
        # 모든 행을 동일한 컬럼 수로 맞춤
        normalized_table = []
        for row in table_matrix:
            normalized_row = row[:max_cols]  # 초과 컬럼 제거
            
            # 부족한 컬럼 채우기
            while len(normalized_row) < max_cols:
                normalized_row.append("")
            
            normalized_table.append(normalized_row)
        
        # 빈 행 제거 (모든 셀이 비어있는 경우)
        filtered_table = []
        for row in normalized_table:
            # 적어도 하나의 셀에 의미있는 내용이 있으면 유지
            if any(str(cell).strip() for cell in row):
                filtered_table.append(row)
        
        # 테이블이 완전히 비어있지 않으면 반환
        if filtered_table:
            return filtered_table
        
        # 모든 행이 비어있더라도 원본 구조는 유지 (최소 1행)
        return normalized_table[:1] if normalized_table else [[""] * max_cols]
        
    def debug_table_structure(self):
        """테이블 구조 디버깅 정보 반환"""
        table_data = self.get_table_data()
        debug_info = []
        
        for i, table in enumerate(table_data):
            table_info = {
                'table_index': i + 1,
                'total_rows': len(table),
                'total_cols': len(table[0]) if table else 0,
                'row_details': []
            }
            
            for j, row in enumerate(table):
                row_info = {
                    'row_index': j + 1,
                    'col_count': len(row),
                    'cells': row,
                    'empty_cells': sum(1 for cell in row if not cell.strip())
                }
                table_info['row_details'].append(row_info)
            
            debug_info.append(table_info)
        
    def get_table_data_with_confidence(self):
        """OCR 결과에서 테이블 2차원 배열과 신뢰도 정보를 함께 추출"""
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

                # 텍스트와 신뢰도를 별도로 저장
                table_matrix = [[""] * max_col for _ in range(max_row)]
                confidence_matrix = [[1.0] * max_col for _ in range(max_row)]

                # 앵커 위치에 텍스트와 신뢰도 채움
                for cell in cells:
                    r = int(cell.get("rowIndex", 0) or 0)
                    c = int(cell.get("columnIndex", 0) or 0)
                    if r < 0 or c < 0 or r >= max_row or c >= max_col:
                        continue
                    
                    text = self._safe_cell_text(cell)
                    table_matrix[r][c] = text
                    
                    # 신뢰도 정보 추출
                    confidence = cell.get("inferConfidence", 1.0)
                    cell_text_lines = cell.get("cellTextLines") or []
                    if cell_text_lines:
                        line_confidence = cell_text_lines[0].get("inferConfidence", confidence)
                        confidence = min(confidence, line_confidence)
                    
                    confidence_matrix[r][c] = confidence

                # 테이블 구조 정규화
                normalized_table = self._normalize_table_structure(table_matrix)
                normalized_confidence = self._normalize_table_structure(confidence_matrix)
                
                if normalized_table and len(normalized_table) > 0:
                    tables_out.append({
                        'data': normalized_table,
                        'confidence': normalized_confidence
                    })

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
                        # 셀의 신뢰도 정보 추출
                        confidence = cell.get("inferConfidence", 1.0)
                        
                        # cellTextLines에서 신뢰도 정보도 확인
                        cell_text_lines = cell.get("cellTextLines") or []
                        if cell_text_lines:
                            # 첫 번째 텍스트 라인의 신뢰도 사용
                            line_confidence = cell_text_lines[0].get("inferConfidence", confidence)
                            confidence = min(confidence, line_confidence)
                        
                        boxes.append({
                            "vertices": vertices,
                            "text": self._safe_cell_text(cell),
                            "confidence": confidence
                        })
        return boxes