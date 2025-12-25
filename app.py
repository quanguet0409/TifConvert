import rasterio
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for threading
import matplotlib.pyplot as plt
from scipy import ndimage
import geopandas as gpd
from rasterio.mask import mask
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
from PIL import Image, ImageTk
import io
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, arr_data, vmin, vmax, output_path, settings, data_stats):
        super().__init__(parent)
        
        self.arr_data = arr_data
        self.original_vmin = vmin
        self.original_vmax = vmax
        self.vmin = vmin
        self.vmax = vmax
        self.output_path = output_path
        self.settings = settings
        self.save_confirmed = False
        self.data_stats = data_stats
        
        self.update_timer = None
        self.update_pending = False
        
        self.colormap_options = {
            "Auto": "auto",
            "Viridis": "viridis",
            "Terrain": "terrain",
            "YlGn (Vegetation)": "YlGn",
            "RdYlGn": "RdYlGn",
            "Spectral": "Spectral",
            "Jet": "jet",
            "Hot": "hot",
            "Cool": "cool",
            "Rainbow": "rainbow",
            "Turbo": "turbo",
            "Plasma": "plasma",
            "Inferno": "inferno",
            "Magma": "magma",
            "Cividis": "cividis"
        }
        
        self.current_cmap = settings.get('cmap', 'viridis')
        
        self.title("Preview - Raster Export")
        self.geometry("1000x900")
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.update_preview()
        
    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="Preview Result",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        settings_text = f"DPI: {self.settings['dpi']} | Format: {self.settings['format']}"
        ctk.CTkLabel(
            header_frame,
            text=settings_text,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(side="right")
        
        stats_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray85", "gray25"))
        stats_frame.pack(pady=5, padx=20, fill="x")
        
        stats_text = (f"Data Range: Min={self.data_stats['min']:.4f} | "
                     f"Max={self.data_stats['max']:.4f} | "
                     f"Mean={self.data_stats['mean']:.4f} | "
                     f"StdDev={self.data_stats['std']:.4f}")
        ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray20", "gray80")
        ).pack(pady=8, padx=10)
        
        controls_frame = ctk.CTkFrame(self, corner_radius=10)
        controls_frame.pack(pady=10, padx=20, fill="x")
        
        colormap_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        colormap_row.pack(pady=8, padx=15, fill="x")
        
        ctk.CTkLabel(
            colormap_row,
            text="Color Scheme:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120
        ).pack(side="left", padx=(0, 10))
        
        self.colormap_var = ctk.StringVar(value="Auto")
        colormap_menu = ctk.CTkOptionMenu(
            colormap_row,
            values=list(self.colormap_options.keys()),
            variable=self.colormap_var,
            command=self.on_colormap_change,
            width=200,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        colormap_menu.pack(side="left", padx=5)
        
        range_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        range_row.pack(pady=8, padx=15, fill="x")
        
        ctk.CTkLabel(
            range_row,
            text="Value Range:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            range_row,
            text="Min:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(5, 5))
        
        self.vmin_entry = ctk.CTkEntry(
            range_row,
            width=100,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.vmin_entry.pack(side="left", padx=5)
        self.vmin_entry.insert(0, f"{self.vmin:.4f}")
        self.vmin_entry.bind("<Return>", lambda e: self.apply_range())
        self.vmin_entry.bind("<FocusOut>", lambda e: self.apply_range())
        
        ctk.CTkLabel(
            range_row,
            text="Max:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(15, 5))
        
        self.vmax_entry = ctk.CTkEntry(
            range_row,
            width=100,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.vmax_entry.pack(side="left", padx=5)
        self.vmax_entry.insert(0, f"{self.vmax:.4f}")
        self.vmax_entry.bind("<Return>", lambda e: self.apply_range())
        self.vmax_entry.bind("<FocusOut>", lambda e: self.apply_range())
        
        ctk.CTkButton(
            range_row,
            text="Apply",
            command=self.apply_range,
            width=80,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            range_row,
            text="Reset",
            command=self.reset_range,
            width=80,
            height=35,
            corner_radius=8,
            fg_color="gray40",
            hover_color="gray30",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)
        
        image_container = ctk.CTkFrame(self, corner_radius=10)
        image_container.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.canvas_frame = ctk.CTkFrame(image_container, fg_color="gray20")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="gray40",
            hover_color="gray30",
            corner_radius=10
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Save Image",
            command=self.save_image,
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        ).pack(side="right", padx=10)
        
        ctk.CTkLabel(
            button_frame,
            text="Values auto-update when you press Enter or click away",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(side="left", expand=True)
    
    def apply_range(self):
        try:
            new_vmin = float(self.vmin_entry.get())
            new_vmax = float(self.vmax_entry.get())
            
            if new_vmin >= new_vmax:
                return
            
            self.vmin = new_vmin
            self.vmax = new_vmax
            self.schedule_update()
        except ValueError:
            pass
    
    def reset_range(self):
        self.vmin = self.original_vmin
        self.vmax = self.original_vmax
        self.vmin_entry.delete(0, 'end')
        self.vmin_entry.insert(0, f"{self.vmin:.4f}")
        self.vmax_entry.delete(0, 'end')
        self.vmax_entry.insert(0, f"{self.vmax:.4f}")
        self.schedule_update()
    
    def on_colormap_change(self, choice):
        selected_cmap = choice
        if selected_cmap == "Auto":
            if self.vmax <= 1.5 and self.vmin >= -1:
                self.current_cmap = "YlGn"
            elif self.vmax - self.vmin > 500:
                self.current_cmap = "terrain"
            else:
                self.current_cmap = "viridis"
        else:
            self.current_cmap = self.colormap_options[selected_cmap]
        
        self.schedule_update()
    
    def schedule_update(self):
        """Debounce preview updates to avoid UI freezing"""
        if self.update_timer:
            self.after_cancel(self.update_timer)
        self.update_timer = self.after(300, self.update_preview_threaded)
    
    def update_preview_threaded(self):
        """Run preview update in background thread"""
        if self.update_pending:
            return
        
        self.update_pending = True
        thread = threading.Thread(target=self._generate_preview, daemon=True)
        thread.start()
    
    def _generate_preview(self):
        """Generate preview image in background thread"""
        try:
            fig = plt.figure(figsize=(10, 10))
            masked_data = np.ma.masked_invalid(self.arr_data)
            plt.imshow(masked_data, cmap=self.current_cmap, vmin=self.vmin, vmax=self.vmax)
            cbar = plt.colorbar()
            cbar.ax.tick_params(labelsize=10)
            plt.axis("off")
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            pil_image = Image.open(buf).copy()
            plt.close(fig)
            
            max_width = 950
            max_height = 500
            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            self.after(0, lambda: self._display_preview(pil_image))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Preview Error", f"Failed to update preview:\n{str(e)}"))
        finally:
            self.update_pending = False
    
    def _display_preview(self, pil_image):
        """Display preview image on main thread"""
        try:
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            self.photo = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=pil_image.size
            )
            
            image_label = ctk.CTkLabel(
                self.canvas_frame,
                image=self.photo,
                text=""
            )
            image_label.pack(expand=True, pady=20, padx=20)
        except Exception as e:
            messagebox.showerror("Display Error", f"Failed to display preview:\n{str(e)}")
    
    def update_preview(self):
        """Initial preview load - use threaded version"""
        self.update_preview_threaded()
    
    def save_image(self):
        try:
            fig = plt.figure(figsize=(10, 10))
            # Use masked array to make NaN transparent
            masked_data = np.ma.masked_invalid(self.arr_data)
            plt.imshow(masked_data, cmap=self.current_cmap, vmin=self.vmin, vmax=self.vmax)
            plt.colorbar()
            plt.axis("off")
            
            fig.savefig(
                self.output_path,
                dpi=self.settings['dpi'],
                bbox_inches='tight',
                transparent=True
            )
            plt.close(fig)
            
            self.save_confirmed = True
            self.settings['cmap'] = self.current_cmap
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image:\n{str(e)}")
    
    def cancel(self):
        self.save_confirmed = False
        self.destroy()


class RasterExportApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Raster Export Tool")
        self.geometry("600x700")
        self.resizable(False, False)
        
        self.tif_path = None
        self.shp_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Raster Export Tool",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()

        
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(pady=10)
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12)
        )
        self.theme_switch.pack()
        self.theme_switch.select()
        
        content_frame = ctk.CTkFrame(self, corner_radius=15)
        content_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        file_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_section.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            file_section,
            text="Input Files",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        tif_frame = ctk.CTkFrame(file_section, fg_color="transparent")
        tif_frame.pack(fill="x", pady=5)
        
        self.tif_label = ctk.CTkLabel(
            tif_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.tif_label.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            tif_frame,
            text="Select Raster File",
            command=self.select_tif,
            width=150,
            height=35,
            corner_radius=8
        ).pack(side="right")
        
        shp_frame = ctk.CTkFrame(file_section, fg_color="transparent")
        shp_frame.pack(fill="x", pady=5)
        
        self.shp_label = ctk.CTkLabel(
            shp_frame,
            text="Optional",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.shp_label.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            shp_frame,
            text="Select Shapefile",
            command=self.select_shp,
            width=150,
            height=35,
            corner_radius=8,
            fg_color="gray40",
            hover_color="gray30"
        ).pack(side="right")
        
        settings_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        settings_section.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            settings_section,
            text="Export Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        dpi_frame = ctk.CTkFrame(settings_section, fg_color="transparent")
        dpi_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            dpi_frame,
            text="Resolution (DPI):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        self.dpi_var = ctk.StringVar(value="300")
        dpi_menu = ctk.CTkSegmentedButton(
            dpi_frame,
            values=["250", "300", "400"],
            variable=self.dpi_var,
            corner_radius=8
        )
        dpi_menu.pack(side="right")
        
        format_frame = ctk.CTkFrame(settings_section, fg_color="transparent")
        format_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            format_frame,
            text="Output Format:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        self.format_var = ctk.StringVar(value="PNG")
        format_menu = ctk.CTkSegmentedButton(
            format_frame,
            values=["PNG", "JPG"],
            variable=self.format_var,
            corner_radius=8
        )
        format_menu.pack(side="right")
        
        self.progress = ctk.CTkProgressBar(content_frame, mode="indeterminate")
        self.progress.pack(pady=20, padx=20, fill="x")
        self.progress.pack_forget()
        
        self.export_btn = ctk.CTkButton(
            content_frame,
            text="Preview & Export",
            command=self.export_image,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10
        )
        self.export_btn.pack(pady=20, padx=20, fill="x")
        
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        info_text = "• Live color preview with adjustable range\n• Auto ROI detection with hole filling\n• Multiple color schemes available"
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            justify="left"
        ).pack(anchor="w")
        
    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Light Mode")
    
    def select_tif(self):
        path = filedialog.askopenfilename(
            title="Select Raster File",
            filetypes=[("GeoTIFF", "*.tif"), ("All Files", "*.*")]
        )
        if path:
            self.tif_path = path
            filename = Path(path).name
            self.tif_label.configure(text=filename, text_color="white")
    
    def select_shp(self):
        path = filedialog.askopenfilename(
            title="Select Shapefile",
            filetypes=[("Shapefile", "*.shp"), ("All Files", "*.*")]
        )
        if path:
            self.shp_path = path
            filename = Path(path).name
            self.shp_label.configure(text=filename, text_color="white")
    
    def export_image(self):
        if not self.tif_path:
            messagebox.showwarning("Warning", "Please select a raster file first.")
            return
        
        out_path = filedialog.asksaveasfilename(
            defaultextension=f".{self.format_var.get().lower()}",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("All Files", "*.*")]
        )
        
        if not out_path:
            return
        
        self.export_btn.configure(state="disabled")
        self.progress.pack(pady=20, padx=20, fill="x")
        self.progress.start()
        
        self.after(100, lambda: self.process_export(out_path))
    
    def process_export(self, out_path):
        try:
            dpi = int(self.dpi_var.get())
            
            if self.shp_path:
                gdf = gpd.read_file(self.shp_path)
                
                with rasterio.open(self.tif_path) as src:
                    if gdf.crs != src.crs:
                        gdf = gdf.to_crs(src.crs)
                    
                    out_img, _ = mask(src, gdf.geometry, crop=True)
                    arr = out_img[0].astype(float)
                    nodata = src.nodata
                
                if nodata is not None:
                    arr[arr == nodata] = np.nan
            else:
                with rasterio.open(self.tif_path) as src:
                    arr = src.read(1).astype(float)
                    nodata = src.nodata
                
                if nodata is not None:
                    arr[arr == nodata] = np.nan
                
                # Create mask of valid (non-NaN) data
                valid_mask = ~np.isnan(arr)
                
                # Apply morphological operations to clean up the mask
                from scipy.ndimage import binary_erosion, binary_dilation
                valid_mask = binary_erosion(valid_mask, iterations=2)
                valid_mask = binary_dilation(valid_mask, iterations=2)
                
                # Find connected components
                labels, num = ndimage.label(valid_mask)
                if num == 0:
                    raise ValueError("Unable to detect ROI")
                
                # Get the largest component
                sizes = ndimage.sum(valid_mask, labels, range(1, num + 1))
                roi_label = sizes.argmax() + 1
                roi = labels == roi_label
                
                # Fill holes in the ROI
                roi = ndimage.binary_fill_holes(roi)
                
                # Find bounding box of ROI
                rows = np.any(roi, axis=1)
                cols = np.any(roi, axis=0)
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                
                # Crop array to bounding box
                arr = arr[rmin:rmax+1, cmin:cmax+1]
                roi = roi[rmin:rmax+1, cmin:cmax+1]
                
                # Apply ROI mask
                arr = np.where(roi, arr, np.nan)
            
            data_stats = {
                'min': np.nanmin(arr),
                'max': np.nanmax(arr),
                'mean': np.nanmean(arr),
                'std': np.nanstd(arr)
            }
            
            vmin, vmax = np.nanpercentile(arr, (5, 95))
            
            if vmax <= 1.5 and vmin >= -1:
                default_cmap = "YlGn"
            elif vmax - vmin > 500:
                default_cmap = "terrain"
            else:
                default_cmap = "viridis"
            
            self.progress.stop()
            self.progress.pack_forget()
            self.export_btn.configure(state="normal")
            
            settings = {
                'dpi': dpi,
                'format': self.format_var.get(),
                'cmap': default_cmap
            }
            
            preview = PreviewWindow(self, arr, vmin, vmax, out_path, settings, data_stats)
            self.wait_window(preview)
            
            if preview.save_confirmed:
                messagebox.showinfo(
                    "Success",
                    f"Image exported successfully!\n\nResolution: {dpi} DPI\nFormat: {self.format_var.get()}\nColormap: {preview.current_cmap}"
                )
            
        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            self.export_btn.configure(state="normal")
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")


if __name__ == "__main__":
    app = RasterExportApp()
    app.mainloop()
