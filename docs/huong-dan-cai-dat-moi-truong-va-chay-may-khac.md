# Hướng dẫn cài đặt môi trường và chạy ứng dụng trên máy khác

## 1. Phạm vi tài liệu

Tài liệu hướng dẫn hai cách triển khai ứng dụng trên máy Windows khác:

- **Cách A - Chạy từ mã nguồn Python**: cần cài Python và các package trong `requirements.txt`.
- **Cách B - Chạy file `.exe`**: không cần cài Python/package, nhưng vẫn cần Google Chrome và Internet.

Ứng dụng đọc CCCD/CMND từ Excel, tự động tra cứu MST trên trang Tổng cục Thuế, nhận dạng CAPTCHA bằng OCR và xuất kết quả Excel.

## 2. Yêu cầu chung trên máy đích

- Windows 10/11, 64-bit.
- Kết nối Internet ổn định.
- Google Chrome đã cài đặt và có thể mở bình thường.
- Quyền ghi vào thư mục ứng dụng, đặc biệt là `input/`, `output/` và thư mục log.
- Người vận hành có quyền hợp pháp đối với dữ liệu CCCD/CMND được sử dụng.

> Ứng dụng không đóng gói kèm Chrome. Selenium sẽ điều khiển Chrome cài sẵn trên máy đích.

## 3. Chuẩn bị mã nguồn

Có thể lấy mã nguồn bằng Git:

```powershell
git clone https://github.com/tuanhung-cv2/TraCuuMst.git
Set-Location TraCuuMst
```

Hoặc sao chép toàn bộ thư mục dự án từ máy phát triển, bao gồm:

```text
main.py
src/
tests/
requirements.txt
requirements-build.txt
.env.example
build_exe.ps1
input/
output/
```

Không sao chép các thư mục/file tạm sau:

```text
.venv/
__pycache__/
build/
dist/
*.log
output/*.xlsx
.env
```

## 4. Cách A: Cài Python và package để chạy từ mã nguồn

### 4.1. Cài Python

1. Tải Python 3.10 trở lên từ `https://www.python.org/downloads/windows/`.
2. Khi cài đặt, chọn **Add Python to PATH**.
3. Mở PowerShell mới và kiểm tra:

```powershell
python --version
python -m pip --version
```

Khuyến nghị dùng Python 3.10 đến 3.13 để tương thích tốt với các package hiện tại.

### 4.2. Tạo virtual environment

Tại thư mục gốc dự án:

```powershell
python -m venv .venv
```

Nếu PowerShell chặn việc kích hoạt script, chỉ cần dùng trực tiếp Python trong `.venv` như các lệnh bên dưới. Nếu muốn kích hoạt:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Kiểm tra Python đang dùng:

```powershell
.\.venv\Scripts\python.exe --version
```

### 4.3. Cài package runtime

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Các package chính:

| Package | Mục đích |
|---|---|
| `pandas` | Đọc và xử lý dữ liệu Excel |
| `openpyxl` | Ghi Excel và định dạng cột dạng Text |
| `selenium` | Điều khiển trình duyệt Chrome |
| `webdriver-manager` | Tải ChromeDriver phù hợp |
| `beautifulsoup4` | Bóc tách HTML kết quả |
| `ddddocr` | Nhận dạng CAPTCHA bằng OCR |
| `python-dotenv` | Đọc cấu hình từ `.env` |

`ddddocr` có thể kéo theo `onnxruntime`, `opencv-python`, `Pillow` và các thư viện phụ thuộc. Đây là các package bình thường của chức năng OCR.

### 4.4. Cài package build `.exe` (chỉ dành cho máy phát triển)

Nếu máy đích chỉ chạy mã nguồn thì không cần bước này. Nếu cần build lại file `.exe`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
```

## 5. Cấu hình ứng dụng

Tạo file `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Mở `.env` và điều chỉnh tối thiểu các giá trị sau:

```dotenv
INPUT_FILE=input/danh_sach_cccd.xlsx
INPUT_SHEET=DanhSachCCCD
CCCD_COLUMN=CCCD
OUTPUT_FILE=output/ket_qua_tra_cuu.xlsx
REQUEST_DELAY_SECONDS=4
MAX_RETRY_NETWORK=2
MAX_RETRY_CAPTCHA=5
REQUEST_TIMEOUT_SECONDS=15
HEADLESS_BROWSER=true
LOG_FILE=tra_cuu.log
```

Ý nghĩa các biến quan trọng:

- `INPUT_FILE`: đường dẫn file Excel đầu vào.
- `INPUT_SHEET`: tên sheet Excel.
- `CCCD_COLUMN`: tên cột chứa CCCD/CMND.
- `OUTPUT_FILE`: đường dẫn file Excel kết quả.
- `REQUEST_DELAY_SECONDS`: thời gian nghỉ giữa các lượt tra cứu. Không nên đặt quá thấp.
- `MAX_RETRY_CAPTCHA`: số lần OCR và submit CAPTCHA tối đa cho một CCCD.
- `MAX_RETRY_NETWORK`: số lần thử lại khi gặp lỗi mạng hoặc timeout.
- `HEADLESS_BROWSER`: `true` để chạy Chrome ẩn, `false` để hiện cửa sổ Chrome.

Không sao chép `.env` lên GitHub vì file này có thể chứa cấu hình riêng của máy vận hành. Chỉ commit `.env.example`.

## 6. Chuẩn bị file Excel đầu vào

Tạo thư mục nếu chưa có:

```powershell
New-Item -ItemType Directory -Force input, output | Out-Null
```

File Excel phải có cột đúng với `CCCD_COLUMN`, ví dụ:

| STT | CCCD |
|---:|---|
| 1 | 001203000001 |
| 2 | 079123456789 |

Lưu ý:

- Định dạng CCCD là 12 chữ số; CMND là 9 chữ số.
- Cột CCCD trong Excel nên được định dạng **Text** để không mất số `0` ở đầu.
- Không dùng dữ liệu mẫu hoặc dữ liệu cá nhân nếu chưa có quyền xử lý.
- File Excel đầu vào đang bị `.gitignore` loại khỏi repository để tránh đưa dữ liệu CCCD lên GitHub.

## 7. Chạy ứng dụng từ mã nguồn

Có thể chạy bằng cấu hình trong `.env`:

```powershell
.\.venv\Scripts\python.exe main.py
```

Hoặc ghi đè cấu hình bằng tham số dòng lệnh:

```powershell
.\.venv\Scripts\python.exe main.py `
    --input "input\danh_sach_cccd_v2.xlsx" `
    --sheet "DanhSachCCCD" `
    --column "CCCD" `
    --output "output\ket_qua_v2.xlsx" `
    --max-retry-captcha 5 `
    --delay 5
```

Sau khi chạy:

- Kết quả được ghi vào file trong `output/`.
- Log được ghi vào file được cấu hình bởi `LOG_FILE` và đồng thời in ra màn hình.
- Các cột CCCD/MST trong Excel đầu ra được lưu dạng Text.
- Chương trình hỗ trợ resume: bản ghi đã `Thành công` sẽ không bị tra cứu lại và vẫn được giữ trong file kết quả.

## 8. Kiểm tra môi trường trước khi chạy thật

Chạy unit test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Kiểm tra Selenium có mở được Chrome và truy cập trang tra cứu:

```powershell
.\.venv\Scripts\python.exe -c "from src.tracuumst.gdt_client import tao_driver; d=tao_driver(True); d.get('https://tracuunnt.gdt.gov.vn/tcnnt/mstcn.jsp'); print(d.title); d.quit()"
```

Nếu kết quả in ra tiêu đề `Cục Thuế - Bộ Tài Chính`, môi trường trình duyệt cơ bản đã hoạt động.

## 9. Cách B: Chạy file `.exe`

Trên máy phát triển, build file `.exe`:

```powershell
.\build_exe.ps1
```

File tạo ra:

```text
dist\tra_cuu_mst.exe
```

Sao chép sang máy đích:

```text
tra_cuu_mst.exe
.env                    # tùy chọn, nếu muốn dùng cấu hình riêng
input\                  # chứa file Excel đầu vào
output\                 # thư mục ghi kết quả
```

Chạy:

```powershell
.\tra_cuu_mst.exe --input "input\danh_sach_cccd_v2.xlsx" --output "output\ket_qua_v2.xlsx"
```

Máy đích chạy `.exe` **không cần cài Python hoặc package Python**, nhưng vẫn cần:

- Google Chrome.
- Internet.
- Quyền ghi file vào thư mục ứng dụng.
- `.env` hoặc tham số dòng lệnh phù hợp.

Nếu Chrome trên máy đích khác phiên bản, `webdriver-manager` cần Internet để tải driver tương ứng ở lần chạy đầu.

## 10. Xử lý lỗi thường gặp

### `ModuleNotFoundError: No module named ...`

Đang chạy nhầm Python hệ thống. Dùng đúng interpreter:

```powershell
.\.venv\Scripts\python.exe main.py
```

Hoặc kích hoạt môi trường:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

### `ddddocr` hoặc `onnxruntime` cài lỗi

Thử cập nhật pip và cài lại:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install --force-reinstall ddddocr
```

Nếu Windows thiếu runtime, cài Microsoft Visual C++ Redistributable phù hợp rồi thử lại.

### Không tải được ChromeDriver

- Kiểm tra Chrome đã cài và mở được.
- Kiểm tra Internet/proxy/firewall.
- Chạy lại với Chrome không headless để quan sát:

```powershell
.\.venv\Scripts\python.exe main.py --headless false
```

### `Too Many Requests` hoặc nhiều bản ghi bị `Lỗi`

- Dừng chương trình và chờ vài phút.
- Tăng `REQUEST_DELAY_SECONDS` lên 8 hoặc 10.
- Không chạy nhiều instance song song.
- Giảm số lượng CCCD trong mỗi lần chạy.
- Kiểm tra log để biết thời điểm rate-limit.

### File kết quả không ghi được

- Đóng file Excel kết quả đang mở.
- Kiểm tra quyền ghi thư mục `output/`.
- Không đặt output trùng với file đang mở bởi Excel.

### PowerShell không cho chạy `.ps1`

Chỉ cần chạy trực tiếp Python trong `.venv`, hoặc dùng lệnh một lần:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 11. Checklist bàn giao máy khác

- [ ] Đã cài Google Chrome.
- [ ] Đã kiểm tra kết nối Internet.
- [ ] Đã sao chép mã nguồn hoặc `tra_cuu_mst.exe`.
- [ ] Đã tạo file `.env` hoặc chuẩn bị tham số CLI.
- [ ] Đã đặt file Excel đầu vào trong `input/`.
- [ ] Đã kiểm tra đúng tên sheet và tên cột CCCD.
- [ ] Đã chạy unit test nếu triển khai từ mã nguồn.
- [ ] Đã chạy thử với số lượng nhỏ trước khi chạy danh sách lớn.
- [ ] Đã xác nhận quyền hợp pháp đối với dữ liệu CCCD/CMND.
- [ ] Đã kiểm tra file output và log sau khi chạy.
