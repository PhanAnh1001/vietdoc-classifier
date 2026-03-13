# Project: {project name}

## Context
- Solo founder, bootstrap
- SaaS: {describe your product}
- Stack: Next.js (Vercel) + FastAPI (Render) + PostgreSQL + Redis (AWS Lightsail)

## Glossary
{add domain terms here}

## Quy tắc cơ bản
- Luôn review lại trước khi trả kết quả cuối
- Trả lời tiếng Việt, comment code bằng tiếng Anh
- Thẳng thắn, không nói chung chung

## Testing (BẮT BUỘC)

**TDD flow**: RED (viết test fail) → GREEN (code tối thiểu) → REFACTOR

- Frontend unit: Vitest — `cd app && npm test`
- Frontend E2E: Playwright — `cd app && npm run test:e2e`
- Backend: `cd backend && uv run pytest tests/ -v`
- Test file đặt cạnh source: `foo.ts` → `foo.test.ts`
- **Test PHẢI pass trước khi commit**

## Session Workflow (BẮT BUỘC)

### Bắt đầu session
1. Đọc `plans/plan.md` — load context
2. Checkout đúng branch (không tạo mới nếu đã có)

### Kết thúc session
1. Commit + push tất cả thay đổi
2. Tạo PR vào `master` nếu branch chưa có PR
3. Cập nhật `plans/plan.md` (chỉ khi có thay đổi thực):
   - TODO: thêm/xóa tasks
   - Notes: cập nhật thông tin kỹ thuật quan trọng
   - Lịch sử: gộp session mới vào milestone tương ứng (1 dòng/milestone, KHÔNG liệt kê sub-tasks)
4. Commit + push `plans/plan.md`

### Format plan.md (tối ưu token)
```
## Trạng thái hiện tại   ← phase + branch hiện tại
## TODO                  ← flat list, ưu tiên cao lên trên
## Notes                 ← key technical refs, env vars, paths
## Lịch sử (milestone)  ← 1 dòng/milestone, KHÔNG sub-tasks
```
> File DUY NHẤT — không tạo thêm. Lịch sử chi tiết ở `git log`.

## Deploy Architecture
- **Frontend**: Next.js → Vercel (auto-deploy from `master`)
- **Backend**: FastAPI → Render (Docker, auto-deploy from `master`)
- **Database**: PostgreSQL on AWS Lightsail
- **Cache**: Redis on AWS Lightsail
