# Database Schema — VietDoc Classifier

## documents

| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID |
| filename | VARCHAR(500) | tên file gốc |
| file_type | VARCHAR(20) | jpg/png/pdf |
| ocr_text | TEXT | raw OCR output |
| doc_type | VARCHAR(100) | predicted class |
| confidence | FLOAT | 0.0–1.0 |
| metadata | JSONB | extracted fields per doc type |
| ground_truth | VARCHAR(100) | label thực tế (cho evaluate) |
| batch_job_id | VARCHAR(36) FK | nullable, refs batch_jobs.id |
| status | VARCHAR(20) | pending/processing/done/failed |
| error_msg | TEXT | nullable |
| created_at | TIMESTAMP | |

Indexes: `idx_documents_batch_job_id`, `idx_documents_status`, `idx_documents_doc_type`

---

## batch_jobs

| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID |
| status | VARCHAR(20) | pending/processing/done/failed |
| total | INTEGER | số file trong batch |
| processed | INTEGER | số file đã xong (done hoặc failed) |
| failed | INTEGER | số file lỗi |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

---

## Document Types (12 categories)

| doc_type | Tên tiếng Việt |
|----------|----------------|
| hoa_don_vat_dau_vao | Hóa đơn VAT đầu vào |
| hoa_don_vat_dau_ra | Hóa đơn VAT đầu ra |
| phieu_chi | Phiếu chi |
| phieu_thu | Phiếu thu |
| sao_ke_ngan_hang | Sao kê ngân hàng |
| giay_uy_quyen | Giấy ủy quyền |
| thong_bao_cong_no | Thông báo công nợ |
| thong_bao_ghi_co | Thông báo ghi có |
| bien_lai | Biên lai |
| hop_dong | Hợp đồng |
| phieu_ke_toan | Phiếu kế toán |
| bang_luong | Bảng lương |
| khac | Khác |
