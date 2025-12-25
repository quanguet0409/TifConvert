# 🗺️ Raster Export Tool

<div align="center">

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

**A modern, professional GUI application for GeoTIFF raster processing and export**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Download](#-download)

</div>

---

## ✨ Features

### 🎨 Modern User Interface
- **Dark/Light Mode** - Seamless theme switching
- **Live Preview** - See your results before saving
- **Real-time Updates** - Instant colormap and value range adjustments
- **Responsive Design** - Smooth, non-blocking UI with background threading

### 📊 Advanced Processing
- **Auto ROI Detection** - Intelligent region of interest identification
- **Shapefile Clipping** - Optional boundary-based cropping
- **Smart Bounding Box** - Automatic cropping to valid data region
- **Hole Filling** - Clean ROI extraction with morphological operations

### 🎨 Colormap Selection
Choose from **15 professional color schemes**:
- Auto (smart selection)
- Viridis, Terrain, YlGn (Vegetation)
- Spectral, Jet, Plasma, Inferno
- And more...

### ⚙️ Export Options
- **Resolution**: 250, 300, 400 DPI
- **Formats**: PNG, JPG
- **Transparent Background** support
- **Adjustable Value Range** for precise visualization

---

## 🚀 Installation

### Option 1: Run from Source

1. **Clone the repository**
```bash
git clone https://github.com/quanguet0409/TifConvert.git
cd TifConvert
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

### Option 2: Download Executable (Windows)

Download the standalone `.exe` file from [Releases](https://github.com/quanguet0409/TifConvert/releases) - no installation required!

---

## 📖 Usage

### Quick Start

1. **Select Raster File** - Choose your GeoTIFF file
2. **Select Shapefile** (Optional) - Add boundary for clipping
3. **Configure Settings** - Choose DPI and output format
4. **Preview & Export** - Click to see live preview
5. **Adjust Colors** - Select colormap and fine-tune value range
6. **Save** - Export when satisfied with the result

### Advanced Features

#### Auto-Update Value Range
- Enter Min/Max values
- Press `Enter` or click outside the field
- Preview updates automatically!

#### Live Colormap Preview
- Change color scheme from dropdown
- See instant preview updates
- No need to click Apply

---

## 🖼️ Screenshots

<div align="center">

### Main Interface (Dark Mode)
*Modern, clean interface with intuitive controls*

### Preview Window
*Live preview with colormap selection and value range controls*

### Light Mode
*Seamless theme switching for different preferences*

</div>

---

## 🛠️ Technical Details

### Built With
- **Python 3.11+** - Core language
- **CustomTkinter** - Modern GUI framework
- **Rasterio** - GeoTIFF file handling
- **GeoPandas** - Shapefile processing
- **Matplotlib** - Rendering and visualization
- **NumPy & SciPy** - Array operations and image processing

### Key Technologies
- **Background Threading** - Non-blocking UI operations
- **Debouncing** - Smooth preview updates (300ms delay)
- **Matplotlib Agg Backend** - Thread-safe rendering
- **Morphological Operations** - Clean ROI extraction

### Performance Optimizations
- ✅ Asynchronous preview generation
- ✅ Debounced user input handling
- ✅ Efficient memory management
- ✅ No UI freezing during heavy processing

---

## 📦 Requirements

### System Requirements
- **OS**: Windows 10/11
- **Python**: 3.11 or higher (for source)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: ~500MB for dependencies

### Python Dependencies
```
customtkinter==5.2.1
rasterio
numpy
matplotlib
scipy
geopandas
Pillow
```

---

## 📥 Download

### Latest Release
Download the standalone executable from the [Releases](https://github.com/quanguet0409/TifConvert/releases) page.

**File Size**: ~200MB (includes all dependencies)

**Note**: First launch may take a few seconds. Windows Defender might show a warning - this is normal for PyInstaller executables.

---

## 🎯 Use Cases

- **Remote Sensing** - Process satellite imagery and aerial photos
- **GIS Analysis** - Export rasters for presentations and reports
- **Environmental Studies** - Visualize vegetation indices (NDVI, EVI)
- **Terrain Analysis** - Create beautiful elevation maps
- **Academic Research** - Generate publication-ready figures

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Powered by [Rasterio](https://github.com/rasterio/rasterio)
- Icons and design inspired by modern GIS applications

---

## 📧 Contact

**Author**: quanguet0409

**GitHub**: [@quanguet0409](https://github.com/quanguet0409)

**Project Link**: [https://github.com/quanguet0409/TifConvert](https://github.com/quanguet0409/TifConvert)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the GIS community

</div>
