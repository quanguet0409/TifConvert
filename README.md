# Raster Export Tool - Hướng dẫn sử dụng

## Cài đặt và Chạy

### Cách 1: Chạy file .exe (Đơn giản nhất)
1. Mở thư mục `dist`
2. Double-click vào `RasterExportTool.exe`
3. Không cần cài đặt Python hay bất kỳ thư viện nào!

### Cách 2: Chạy từ source code
```bash
pip install -r requirements.txt
python app.py
```

## Tính năng

### 🎨 Giao diện hiện đại
- Dark/Light mode
- Preview trước khi lưu
- Live colormap selection
- Tùy chỉnh value range

### 📊 Xử lý dữ liệu
- Tự động phát hiện ROI (Region of Interest)
- Clip theo shapefile (tùy chọn)
- Auto bounding box crop
- Fill holes trong ROI

### 🎨 Colormap
15 thang màu chuyên nghiệp:
- Auto (tự động chọn)
- Viridis, Terrain, YlGn
- Spectral, Jet, Plasma
- Và nhiều hơn nữa...

### ⚙️ Cài đặt xuất
- DPI: 250, 300, 400
- Format: PNG, JPG
- Transparent background

## Hướng dẫn sử dụng

1. **Chọn file TIFF**: Click "Select Raster File"
2. **Chọn Shapefile** (tùy chọn): Nếu có file .shp để clip
3. **Chọn cài đặt**: DPI và format
4. **Preview & Export**: Click để xem preview
5. **Điều chỉnh màu**: Chọn colormap và điều chỉnh min/max
6. **Lưu**: Click "Save Image" khi hài lòng

## Tính năng nâng cao

### Auto-update Value Range
- Nhập giá trị Min/Max
- Nhấn Enter hoặc click ra ngoài
- Preview tự động cập nhật!

### Live Preview
- Thay đổi colormap → Xem ngay kết quả
- Không cần bấm Apply
- Debouncing 300ms để mượt mà

### Performance
- Background threading
- Không bị "not responding"
- UI luôn mượt mà

## File cấu trúc

```
Tool tiff/
├── dist/
│   └── RasterExportTool.exe  ← File .exe chạy trực tiếp
├── app.py                     ← Source code
├── requirements.txt           ← Dependencies
├── icon.ico                   ← App icon
└── README.md                  ← File này
```

## Yêu cầu hệ thống

- Windows 10/11
- Không cần cài đặt gì khi dùng file .exe
- Nếu chạy từ source: Python 3.11+

## Lưu ý

- File .exe có thể mất vài giây để khởi động lần đầu
- Kích thước file ~200MB do bundle tất cả dependencies
- Antivirus có thể cảnh báo - đây là bình thường với PyInstaller

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra file TIFF có hợp lệ không
2. Đảm bảo shapefile (nếu có) cùng CRS với raster
3. Thử giảm DPI nếu file quá lớn

---

**Version**: 1.0  
**Build date**: 2025-12-25  
**Built with**: Python 3.11, CustomTkinter, PyInstaller
