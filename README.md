# Ứng dụng tra cứu Mã số thuế cá nhân theo CCCD/CMND

Ứng dụng Python tự động đọc danh sách CCCD/CMND từ file Excel, tra cứu Mã số thuế (MST) trên trang của Tổng cục Thuế (`https://tracuunnt.gdt.gov.vn/tcnnt/mstcn.jsp`), tự động nhận dạng CAPTCHA bằng OCR, và xuất kết quả ra file Excel.

> Tài liệu yêu cầu nghiệp vụ: [ba-docs/thiet-ke-ung-dung-tra-cuu-mst.md](ba-docs/thiet-ke-ung-dung-tra-cuu-mst.md)
> Tài liệu thiết kế kỹ thuật: [docs/tai-lieu-thiet-ke-ky-thuat.md](docs/tai-lieu-thiet-ke-ky-thuat.md)
> Kế hoạch triển khai & nhật ký thực hiện: [docs/ke-hoach-trien-khai.md](docs/ke-hoach-trien-khai.md)

## 1. Yêu cầu hệ thống

- Windows, Python 3.10 trở lên.
- Trình duyệt Google Chrome đã cài trên máy (Selenium sẽ tự tải driver phù hợp qua `webdriver-manager`).
- Kết nối Internet.

## 2. Cài đặt

```powershell
# 1. Tạo và kích hoạt môi trường ảo
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Tạo file cấu hình từ mẫu (tuỳ chỉnh nếu cần)
Copy-Item .env.example .env
```

> Nếu cài `ddddocr` gặp lỗi (một số máy Windows cần thêm Visual C++ Redistributable), tham khảo phương án dự phòng `pytesseract` ghi trong tài liệu thiết kế kỹ thuật mục 6.

## 3. Chuẩn bị file đầu vào

Chuẩn bị file Excel chứa ít nhất 1 cột số CCCD/CMND, ví dụ `input/danh_sach_cccd.xlsx`:

| STT | CCCD |
|---|---|
| 1 | 001203000001 |
| 2 | 079123456789 |

- Số CCCD phải đúng 12 chữ số, hoặc CMND đúng 9 chữ số. Bản ghi sai định dạng sẽ được đánh dấu `Định dạng không hợp lệ`, không làm dừng chương trình.
- Có thể cấu hình tên file/sheet/cột qua tham số dòng lệnh hoặc file `.env` (xem mục 4).

## 4. Cấu hình

Có thể cấu hình qua file `.env` (khuyến nghị, xem `.env.example`) hoặc tham số dòng lệnh (ưu tiên cao hơn `.env`):

| Tham số CLI | Biến `.env` | Mặc định | Mô tả |
|---|---|---|---|
| `--input` | `INPUT_FILE` | `input/danh_sach_cccd.xlsx` | File Excel đầu vào |
| `--sheet` | `INPUT_SHEET` | `DanhSachCCCD` | Tên sheet |
| `--column` | `CCCD_COLUMN` | `CCCD` | Tên cột chứa CCCD/CMND |
| `--output` | `OUTPUT_FILE` | `output/ket_qua_tra_cuu.xlsx` | File Excel kết quả |
| `--delay` | `REQUEST_DELAY_SECONDS` | `4` | Số giây nghỉ giữa các lượt tra cứu (chống bị chặn IP) |
| `--max-retry-network` | `MAX_RETRY_NETWORK` | `2` | Số lần thử lại khi lỗi kết nối |
| `--max-retry-captcha` | `MAX_RETRY_CAPTCHA` | `3` | Số lần thử lại khi OCR đọc sai CAPTCHA |
| `--timeout` | `REQUEST_TIMEOUT_SECONDS` | `15` | Timeout chờ trang phản hồi (giây) |
| `--headless` | `HEADLESS_BROWSER` | `true` | Chạy Chrome ẩn (headless) hay hiển thị cửa sổ |
| `--log-file` | `LOG_FILE` | `tra_cuu.log` | Đường dẫn file log |
| `--captcha-engine` | `CAPTCHA_ENGINE` | `ddddocr` | `ddddocr` (tự động OCR) hoặc `manual` (mở ảnh CAPTCHA và gõ nhanh qua console) |
| `--rate-limit-max-retry` | `RATE_LIMIT_MAX_RETRY` | `5` | Số lần thử lại riêng khi bị máy chủ trả về "Too Many Requests" |
| `--rate-limit-backoff-seconds` | `RATE_LIMIT_BACKOFF_SECONDS` | `30` | Thời gian nghỉ ban đầu (giây) khi bị rate-limit, tăng gấp đôi mỗi lần thử lại (tối đa 300s) |

### Chế độ nhập CAPTCHA nhanh bằng tay (`CAPTCHA_ENGINE=manual`)

Nếu OCR (`ddddocr`) đọc sai CAPTCHA quá nhiều lần trên thực tế khiến chương trình phải thử lại nhiều vòng mới lấy được kết quả, có thể chuyển sang chế độ nhập thủ công nhanh:

```powershell
# Trong .env: CAPTCHA_ENGINE=manual
# Hoặc truyền trực tiếp qua tham số:
.\.venv\Scripts\python.exe main.py --captcha-engine manual
```

### Lỗi "Too Many Requests" / trạng thái "Lỗi" hàng loạt

Nếu log báo `Máy chủ trả về 'Too Many Requests'` và nhiều bản ghi bị gán trạng thái `Lỗi`, nghĩa là máy chủ Tổng cục Thuế đang tạm chặn do gửi quá nhiều request trong thời gian ngắn (thường do chạy thử nhiều lần liên tiếp với `--delay` thấp). Cách khắc phục:

1. **Chờ một khoảng thời gian** (khuyến nghị vài phút đến vài chục phút) trước khi chạy lại — giới hạn này thường tự gỡ sau khi ngừng gửi request.
2. **Tăng `REQUEST_DELAY_SECONDS`** (ví dụ 8–10 giây) và **giảm số lượng CCCD mỗi lần chạy** để tránh kích hoạt lại giới hạn.
3. Chương trình đã tự động thử lại khi gặp lỗi này (`RATE_LIMIT_MAX_RETRY` lần, thời gian nghỉ tăng dần gấp đôi mỗi lần, tối đa 300 giây/lần) — nếu vẫn thất bại sau tất cả các lần thử, có thể tăng `RATE_LIMIT_MAX_RETRY` và `RATE_LIMIT_BACKOFF_SECONDS` trong `.env`, nhưng **ưu tiên chờ thực tế** vẫn hiệu quả hơn vì đây là giới hạn phía máy chủ, không phải lỗi trong ứng dụng.
4. Chạy lại lệnh cũ như bình thường sau khi chờ — cơ chế resume sẽ tự bỏ qua các bản ghi đã "Thành công", chỉ tra cứu lại các bản ghi "Lỗi"/"Không tìm thấy".

Ở chế độ này, mỗi lượt tra cứu chương trình sẽ tự mở ảnh CAPTCHA bằng trình xem ảnh mặc định của Windows và dừng lại chờ bạn gõ mã CAPTCHA vào cửa sổ dòng lệnh (terminal) rồi nhấn Enter — nhanh và chính xác hơn nhiều so với việc để OCR tự đoán sai rồi thử lại lặp lại. Chế độ này **không cần** bật cửa sổ trình duyệt (`--headless true` vẫn dùng được bình thường).

## 5. Chạy chương trình

> ⚠️ **Luôn chạy bằng Python trong `.venv`** (`.\.venv\Scripts\python.exe`), không dùng `python`/`python.exe` trực tiếp — nếu không sẽ gặp lỗi `ModuleNotFoundError: No module named 'selenium'` (đang dùng Python hệ thống, chưa cài các thư viện của dự án). Nếu muốn gõ `python` ngắn gọn, hãy kích hoạt venv trước: `.\.venv\Scripts\Activate.ps1`.

```powershell
.\.venv\Scripts\python.exe main.py
```

Hoặc tuỳ chỉnh tham số:

```powershell
.\.venv\Scripts\python.exe main.py --input "input/danh_sach_cccd.xlsx" --output "output/ket_qua.xlsx" --delay 5
```

Chương trình sẽ:
1. Đọc danh sách CCCD/CMND, kiểm tra định dạng.
2. Với mỗi số hợp lệ: mở trình duyệt, tự động điền form, tự đọc và điền CAPTCHA (OCR), submit, đọc kết quả.
3. Ghi kết quả ra file Excel (giữ nguyên CCCD gốc + các cột: MST, Họ tên, Cơ quan thuế quản lý, Trạng thái, Số lần thử CAPTCHA, Ghi chú).
4. Ghi log chi tiết từng lượt tra cứu vào file log.

**Chạy lại (resume)**: nếu chương trình bị dừng giữa chừng, chạy lại lệnh cũ — các bản ghi đã có trạng thái `Thành công` ở lần chạy trước sẽ tự động được bỏ qua và giữ nguyên trong file kết quả.

## 6. Chạy kiểm thử (unit test)

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## 7. Lưu ý quan trọng

- **Giới hạn tốc độ**: máy chủ Tổng cục Thuế có giới hạn số request (đã xác nhận qua thực tế phản hồi "Too Many Requests"). Không giảm `--delay` xuống quá thấp và không chạy nhiều tiến trình song song.
- **Giới hạn kỹ thuật đã biết**: trang tra cứu không phân biệt được "CAPTCHA sai" và "không có dữ liệu" trong phản hồi. Vì vậy khi OCR đọc sai CAPTCHA liên tục, chương trình sẽ gán trạng thái `Không tìm thấy` (không phải `Lỗi`) — xem chi tiết tại `docs/ke-hoach-trien-khai.md` (Phase 5).
- **Dữ liệu cá nhân**: CCCD/CMND là dữ liệu nhạy cảm. Chỉ sử dụng với danh sách có thẩm quyền hợp pháp, không chia sẻ file kết quả ra ngoài phạm vi cho phép.
- **Cấu trúc trang có thể thay đổi**: nếu Tổng cục Thuế thay đổi giao diện/form, cần cập nhật lại các selector trong `src/tracuumst/gdt_client.py` và `src/tracuumst/result_parser.py`.

## 8. Đóng gói thành file .exe chạy độc lập (không cần cài Python)

Có thể đóng gói ứng dụng thành 1 file `.exe` duy nhất bằng PyInstaller — đã build và kiểm thử thành công (Selenium mở Chrome, OCR `ddddocr` đọc CAPTCHA, ghi Excel đều hoạt động đúng trong bản đóng gói).

```powershell
.\build_exe.ps1
```

Kết quả: `dist\tra_cuu_mst.exe`. Chạy trực tiếp không cần môi trường ảo:

```powershell
.\dist\tra_cuu_mst.exe --input "input\danh_sach_cccd.xlsx" --output "output\ket_qua.xlsx"
```

**Lưu ý khi mang `.exe` sang máy khác**:
- **Máy đích vẫn phải cài Google Chrome** (Selenium chỉ điều khiển Chrome có sẵn, không đóng gói kèm trình duyệt).
- **Máy đích cần Internet** ở lần chạy đầu để `webdriver-manager` tự tải driver Chrome phù hợp với phiên bản Chrome trên máy đó.
- Mang kèm thư mục `input/` (file Excel mẫu) và file `.env` (hoặc dùng tham số dòng lệnh) — file `.exe` không tự tạo các file này.
- File `.exe` khá nặng (do đóng gói cả `onnxruntime`, `opencv`, `numpy`, `pandas`...) — đây là điều bình thường với ứng dụng có OCR.
- Nếu Tổng cục Thuế đổi cấu trúc trang, cần build lại `.exe` sau khi sửa `gdt_client.py`/`result_parser.py`.

## 9. Cấu trúc dự án

```
TraCuuMaSoThue/
├── ba-docs/                    # Tài liệu yêu cầu nghiệp vụ (BRD)
├── docs/                       # Tài liệu thiết kế kỹ thuật & kế hoạch triển khai
├── input/                      # File Excel đầu vào
├── output/                     # File Excel kết quả (tự tạo khi chạy)
├── src/tracuumst/              # Mã nguồn ứng dụng
│   ├── models.py                # Kiểu dữ liệu: LookupRecord, LookupResult, TrangThai
│   ├── config.py                 # Đọc cấu hình (CLI + .env)
│   ├── validators.py            # Kiểm tra định dạng CCCD/CMND
│   ├── excel_io.py               # Đọc input, ghi output, resume
│   ├── captcha_solver.py        # Tự động đọc CAPTCHA bằng OCR
│   ├── gdt_client.py             # Điều khiển trình duyệt, tra cứu, retry
│   ├── result_parser.py         # Bóc tách HTML kết quả
│   └── logger.py                 # Cấu hình logging
├── tests/                       # Unit test + fixture
├── main.py                      # Điểm chạy chính
├── build_exe.ps1                # Script đóng gói .exe (PyInstaller)
├── requirements.txt
├── requirements-build.txt       # Thư viện chỉ cần khi đóng gói (pyinstaller)
└── .env.example
```

