# Đóng gói ứng dụng thành file .exe độc lập bằng PyInstaller.
# Chạy: .\build_exe.ps1
# Kết quả: dist\tra_cuu_mst.exe

.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt

.\.venv\Scripts\pyinstaller.exe --noconfirm --onefile --name tra_cuu_mst `
    --paths src `
    --collect-all ddddocr `
    --collect-all onnxruntime `
    --collect-all cv2 `
    --collect-all selenium `
    --collect-all webdriver_manager `
    --collect-all openpyxl `
    main.py

Write-Host "`nDa build xong: dist\tra_cuu_mst.exe" -ForegroundColor Green
Write-Host "Nho copy kem file .env (hoac sua truc tiep bang tham so dong lenh) va thu muc input\ khi mang sang may khac." -ForegroundColor Yellow
