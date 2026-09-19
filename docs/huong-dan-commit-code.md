# Hướng dẫn commit & đẩy code lên GitHub (tài khoản tuanhung-cv2)

| Thông tin | Nội dung |
|---|---|
| Tài khoản GitHub | `tuanhung-cv2` |
| Repository | `https://github.com/tuanhung-cv2/TraCuuMst.git` |
| Nhánh chính | `main` |
| Ngày cập nhật | 2026-09-19 |

## 1. Trạng thái hiện tại của repo cục bộ

Đã kiểm tra: thư mục dự án **đã được khởi tạo git** (`git init`) và **đã gắn sẵn remote** trỏ tới repo GitHub:

```powershell
git remote -v
# origin  https://github.com/tuanhung-cv2/TraCuuMst.git (fetch)
# origin  https://github.com/tuanhung-cv2/TraCuuMst.git (push)
```

Chưa có commit nào (`nothing added to commit but untracked files present`). Toàn bộ file trong workspace đang ở trạng thái **untracked**.

## 2. Yêu cầu trước khi commit

1. Đã cài Git trên máy (`git --version`).
2. Đã đăng nhập/authenticate với GitHub bằng 1 trong các cách:
   - **Git Credential Manager** (mặc định trên Windows khi cài Git for Windows) — sẽ tự bật popup đăng nhập trình duyệt ở lần `push` đầu tiên.
   - Hoặc **Personal Access Token (PAT)** dùng làm mật khẩu khi được hỏi.
   - Hoặc **GitHub CLI** (`gh auth login`) nếu đã cài `gh` (hiện máy này chưa cài `gh`, có thể bỏ qua và dùng Git thường).
3. Đã có quyền push vào repo `tuanhung-cv2/TraCuuMst` (là chủ repo hoặc được thêm làm collaborator).

## 3. Kiểm tra trước khi commit — KHÔNG commit dữ liệu nhạy cảm

Trước khi `git add`, rà soát lại các mục sau (đã cấu hình sẵn trong `.gitignore` nhưng nên kiểm tra thủ công 1 lần):

| Mục | Có nên commit? | Ghi chú |
|---|---|---|
| `.venv/` | ❌ Không | Đã có trong `.gitignore` |
| `.env` | ❌ Không | Đã có trong `.gitignore` — chỉ commit `.env.example` (không chứa giá trị nhạy cảm) |
| `output/*.xlsx` | ❌ Không | Kết quả tra cứu có thể chứa MST/họ tên thật — đã loại trừ trong `.gitignore` |
| `build/`, `dist/`, `*.spec` | ❌ Không | Sản phẩm build tạm thời của PyInstaller, có thể tạo lại bằng `build_exe.ps1` |
| `input/danh_sach_cccd.xlsx` | ❌ Không | **Đã xác nhận thực tế**: ít nhất 1 CCCD trong file này là dữ liệu thật (trả về tên người thật khi kiểm thử ở Phase 2). Đã bổ sung vào `.gitignore` — **không được gỡ dòng này** trừ khi thay toàn bộ nội dung file bằng dữ liệu giả lập. |
| `tra_cuu.log`, `nghiem_thu.log` | ❌ Không | Log có thể chứa CCCD/MST đã tra cứu — đã loại trừ `tra_cuu.log` trong `.gitignore`, cần bổ sung các file log khác nếu phát sinh |
| Mã nguồn (`src/`, `main.py`, `tests/`) | ✅ Có | An toàn, không chứa dữ liệu cá nhân |
| Tài liệu (`ba-docs/`, `docs/`) | ✅ Có | An toàn |

> **Quan trọng**: repo là **public** theo mặc định trên GitHub trừ khi tạo ở chế độ private. Vì dự án xử lý CCCD/CMND (dữ liệu cá nhân nhạy cảm theo BR-05 trong tài liệu BA), khuyến nghị đặt repo ở chế độ **Private** nếu chưa chắc chắn về việc đã loại bỏ hết dữ liệu thật.

## 4. Các bước commit & push

```powershell
# 1. Xem lại danh sách file sẽ được add (đối chiếu với bảng ở mục 3)
git status

# 2. Add toàn bộ file (đã được .gitignore lọc bớt các file không nên commit)
git add .

# 3. Kiểm tra lại lần cuối những gì SẼ được commit trước khi xác nhận
git status

# 4. Commit với message rõ ràng
git commit -m "feat: ung dung tra cuu MST theo CCCD/CMND (OCR tu dong CAPTCHA)"

# 5. Đặt tên nhánh chính là main (nếu chưa đúng)
git branch -M main

# 6. Đẩy code lên GitHub (lần đầu dùng -u để gắn upstream)
git push -u origin main
```

Nếu Git yêu cầu đăng nhập, một cửa sổ trình duyệt sẽ tự mở để đăng nhập tài khoản `tuanhung-cv2` (qua Git Credential Manager). Nếu dùng PAT, dán token vào ô mật khẩu khi được hỏi.

## 5. Quy ước commit message (khuyến nghị)

Theo [Conventional Commits](https://www.conventionalcommits.org/) để dễ theo dõi lịch sử:

| Loại | Khi nào dùng | Ví dụ |
|---|---|---|
| `feat:` | Thêm tính năng mới | `feat: them co che resume khi chay lai` |
| `fix:` | Sửa lỗi | `fix: sua loi mat du lieu khi resume` |
| `docs:` | Chỉ thay đổi tài liệu | `docs: cap nhat huong dan dong goi exe` |
| `refactor:` | Tái cấu trúc code, không đổi hành vi | `refactor: tach ham _cho_trang_san_sang` |
| `test:` | Thêm/sửa test | `test: them test cho gdt_client retry` |
| `chore:` | Việc vặt (cấu hình, dependency...) | `chore: them requirements-build.txt` |

## 6. Các lần commit tiếp theo

```powershell
git add .
git commit -m "<loai>: <mo ta ngan gon>"
git push
```

## 7. Nếu cần tạo repo mới thay vì dùng repo đã có sẵn

Nếu `tuanhung-cv2/TraCuuMst` chưa tồn tại trên GitHub, cần tạo trước trên web (`https://github.com/new`) rồi mới `push` được, hoặc dùng lệnh này nếu đã cài GitHub CLI (`gh`):

```powershell
gh repo create tuanhung-cv2/TraCuuMst --private --source=. --remote=origin --push
```

## 8. Xử lý sự cố thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `remote origin already exists` | Đã có remote `origin` gắn sẵn (đúng như trạng thái hiện tại) | Dùng `git remote set-url origin <url>` nếu cần đổi, hoặc bỏ qua bước `git remote add` |
| `Updates were rejected` khi push | Repo trên GitHub đã có commit khác (README do GitHub tự tạo) | Chạy `git pull origin main --allow-unrelated-histories` rồi giải quyết conflict (nếu có) trước khi push lại |
| Yêu cầu nhập username/password liên tục | Chưa cấu hình Credential Manager hoặc PAT hết hạn | Cài Git Credential Manager hoặc tạo PAT mới tại `https://github.com/settings/tokens` |
| Push bị từ chối do file quá lớn | File `.exe` trong `dist/` hoặc file Excel lớn bị add nhầm | Kiểm tra lại `.gitignore`, dùng `git rm --cached <file>` để bỏ khỏi staging |

---

**Lưu ý**: tài liệu này chỉ hướng dẫn các bước — việc thực thi `git add`/`commit`/`push` thực tế cần được người vận hành (hoặc trợ lý, nếu được yêu cầu rõ ràng) thực hiện sau khi đã rà soát kỹ mục 3 ở trên, vì đây là hành động đẩy dữ liệu lên hệ thống chia sẻ bên ngoài (GitHub).
