import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pathlib import Path
from tkinter import PhotoImage
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pathlib import Path
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import cv2 as cv
from ttkbootstrap.dialogs import Messagebox
import numpy as np

base_url = 'assets/art'

traditional_dict = {
    os.path.splitext(filename)[0].replace('_', ' ').title(): filename
    for filename in os.listdir('{}/traditional'.format(base_url))
}
modern_dict = {
    os.path.splitext(filename)[0].replace('_', ' ').title(): filename
    for filename in os.listdir('{}/modern'.format(base_url))
}
contemporary_dict = {
    os.path.splitext(filename)[0].replace('_', ' ').title(): filename
    for filename in os.listdir('{}/contemporary'.format(base_url))
}
categories = {
    "traditional": traditional_dict,
    "modern": modern_dict,
    "contemporary": contemporary_dict,
}

supported_effects = [
    'color_space', 
    'addition', 
    'sharpen', 
    'brightness',
    'noise_reduction', 
    'scaling', 
    'inverse'
]

class DashboardPage(ttk.Frame):
    def __init__(self, parent: ttk.Window):
        super().__init__(parent, padding=10)

        # Configuration for root window
        parent.title("YSMA Home")
        parent.style.theme_use('darkly')
        parent.state('zoomed') 
        parent.minsize(960, 800) 
        parent.resizable(True, True)
        
        # Expand to fill entire window
        self.pack(fill=BOTH, expand=YES, pady=15)
        
        # Three columns, first and third fixed sizing
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.image_container = ImageContainer(self)
        self.image_container.grid(row=0, column=1, sticky=NSEW, padx=15)
        
        self.left_sidebar = EffectsToolBar(self)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        self.right_sidebar = EffectManager(self)
        self.right_sidebar.grid(row=0, column=2, sticky=NSEW, padx=(15, 0))

class EffectsToolBar(ttk.Frame): 
    def __init__(self, parent):
        super().__init__(parent)
        
        # Store for sample name
        self.sample_var = ttk.StringVar()
        
        # Expand inside DashboardPage
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        
        self.cbo_art_categories = ttk.Combobox(self, values=list(categories.keys()), state="readonly")
        self.cbo_art_categories.set(self.cbo_art_categories['values'][0])  
        self.cbo_art_categories.grid(row=0, column=0, sticky=EW, pady=(0, 20))
        self.cbo_art_categories.bind("<<ComboboxSelected>>", self.on_select_category)

        # Sample Combobox
        self.cbo_art_samples = ttk.Combobox(self, textvariable=self.sample_var, state="readonly")
        self.cbo_art_samples.grid(row=1, column=0, sticky=EW)
        self.sample_var.trace_add("write", self.on_select_sample)
        
        # Populate sample combobox
        self.on_select_category()
        
        # Effects container with primary Bootstrap theme
        self.effects_container = ttk.Labelframe(self, text="Effects and Transformations", bootstyle="primary")
        self.effects_container.grid(row=2, column=0, sticky=NSEW, pady=(20, 0))
        self.effects_container.columnconfigure(0, weight=1)

        # Create buttons in a vertical stack
        for index, effect_name in enumerate(supported_effects):
            self.effects_container.rowconfigure(index, weight=0)
            button = ttk.Button(
                self.effects_container, 
                text=effect_name.capitalize(), 
                bootstyle="primary-outline",
                padding=(0, 10),
                command=lambda name=effect_name: self.master.right_sidebar.show_controller(name)
            )
            button.grid(row=index, column=0, sticky=EW, padx=15, pady=(20, 0)) 

    def on_select_category(self, *args):
        self.cbo_art_samples['values'] = list(categories[self.cbo_art_categories.get()].keys())
        self.cbo_art_samples.set(self.cbo_art_samples['values'][0])

    def on_select_sample(self, *args):
        selected_category = self.cbo_art_categories.get()
        selected_sample = self.cbo_art_samples.get()
        self.master.image_container.change_selected_image(selected_category, selected_sample)
        
class EffectManager(ttk.Labelframe):
    def __init__(self, parent, title='Effect Manager'):
        super().__init__(parent, text=title, padding=15, bootstyle="primary")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Persistent channel toggle states
        self.show_red = ttk.BooleanVar(value=True)
        self.show_green = ttk.BooleanVar(value=True)
        self.show_blue = ttk.BooleanVar(value=True)
        #Persistent brightness
        self.brightness_scale_var = ttk.DoubleVar(value = 0)
        self.contrast_scale_var = ttk.DoubleVar(value = 1.0)
        self.sharpen_scale_var = ttk.IntVar(value = 0)
        self.blur_scale_var = ttk.IntVar(value = 1)
        self.resize_scale_var = ttk.DoubleVar(value = 1.0)
        self.invert_image = ttk.BooleanVar(value=True)
        self.image_opacity_1 = ttk.DoubleVar(value=0.5)
        self.image_opacity_2 = ttk.DoubleVar(value=0.5)
        # Reference to current frame
        self.current_frame = None
        self.original_image = None
        
        self.show_controller(supported_effects[0])
    
    def show_controller(self, effect_name):
        # Clear previous frame
        if self.current_frame:
            self.current_frame.destroy()
        self.current_effect = effect_name  
            
        self.current_frame = ttk.Frame(self)
        self.current_frame.grid(row=0, column=0, sticky=NSEW)
        
        # Store the original image when setting up a controller
        self.original_image = self.master.image_container.current_image.copy()
        
        if effect_name == 'color_space':
            self._setup_channel_toggles()
        elif effect_name == 'brightness':
            self._setup_brightness()
        elif effect_name == 'sharpen':
            self._setup_sharpen()
        elif effect_name == 'noise_reduction':
            self._setup_blur()
        elif effect_name == 'scaling':
            self._setup_resize()
        elif effect_name == 'inverse':
            self._setup_inverse()
        else:
            self._setup_addition()
    
    def on_image_changed(self, new_image):
        self.original_image = new_image.copy()
        # Reapply the current effect based on what's active
        if hasattr(self, 'current_effect'):
            if self.current_effect == 'color_space':
                self._update_channels()
            elif self.current_effect == 'brightness':
                self._update_brightness()
            elif self.current_effect == 'sharpen':
                self._update_sharpness()
            elif self.current_effect == 'noise_reduction':
                self._update_blur()
            elif self.current_effect == 'scaling':
                self._update_resize()
            elif self.current_effect == 'inverse':
                self._update_inverse()
            elif self.current_effect == 'addition':
                self._update_addition()
                
            
    def _setup_channel_toggles(self):
        # Red Channel
        ttk.Checkbutton(
            self.current_frame,
            text="Red Channel",
            variable=self.show_red,
            bootstyle="danger-round-toggle",
            command=self._update_channels
        ).pack(side=TOP, fill=X, pady=(0, 15))
        
        # Green Channel
        ttk.Checkbutton(
            self.current_frame,
            text="Green Channel",
            variable=self.show_green,
            bootstyle="success-round-toggle",
            command=self._update_channels
        ).pack(side=TOP, fill=X, pady=(0, 15))
        
        # Blue Channel
        ttk.Checkbutton(
            self.current_frame,
            text="Blue Channel",
            variable=self.show_blue,
            bootstyle="primary-round-toggle",
            command=self._update_channels
        ).pack(side=TOP, fill=X)
        
        # Initial update
        self._update_channels()
    
    def _setup_brightness(self):
        
        ttk.Label(
            self.current_frame,
            text="Brightness",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=-100,
            to=100,
            orient=HORIZONTAL,
            variable=self.brightness_scale_var,
            command=lambda v: self._update_brightness(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        
        ttk.Label(
            self.current_frame,
            text="Contrast",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=0.1,
            to=3.0,
            orient=HORIZONTAL,
            variable=self.contrast_scale_var,
            command=lambda v: self._update_brightness(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        # Initial update
        self._update_brightness()
        
    def _setup_sharpen(self):
        
        ttk.Label(
            self.current_frame,
            text="Degree",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=0,
            to=2,
            orient=HORIZONTAL,
            variable=self.sharpen_scale_var,
            command=lambda v: self._update_sharpness(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        self._update_sharpness()
    
    def _setup_blur(self):
        
        ttk.Label(
            self.current_frame,
            text="Degree",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=1,
            to=5,
            orient=HORIZONTAL,
            variable=self.blur_scale_var,
            command=lambda v: self._update_blur(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        self._update_sharpness()
    
    def _setup_resize(self):
        
        ttk.Label(
            self.current_frame,
            text="Scale factor",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=0.1,
            to=2.0,
            orient=HORIZONTAL,
            variable=self.resize_scale_var,
            command=lambda v: self._update_resize(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        self._update_resize()
    
    def _setup_inverse(self):
        ttk.Checkbutton(
            self.current_frame,
            text="Invert image",
            variable=self.invert_image,
            bootstyle="success-round-toggle",
            command=self._update_inverse
        ).pack(side=TOP, fill=X, pady=(0, 15))
        
        # Initial update
        self._update_inverse()
    
    def _setup_addition(self):
        self.open_image_file()
        ttk.Label(
            self.current_frame,
            text="Image one opacity",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=0,
            to=1.0,
            orient=HORIZONTAL,
            variable=self.image_opacity_1,
            command=lambda v: self._update_addition(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        
        ttk.Label(
            self.current_frame,
            text="Image two opacity",
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 10))
        
        # default Scale style
        ttk.Scale(
            self.current_frame,
            from_=0,
            to=1.0,
            orient=HORIZONTAL,
            variable=self.image_opacity_2,
            command=lambda v: self._update_addition(), 
            bootstyle="info"
        ).pack(side=TOP, fill=X, pady=(0, 15))
        self._update_addition()
    def open_image_file(self):
        filetypes = [
            ('JPEG files', '*.jpg;*.jpeg'),
            ('PNG files', '*.png'),
            ('All files', '*.*')
        ]
    
        file_path = filedialog.askopenfilename(
            title="Open image file",
            initialdir='.',
            filetypes=filetypes
        )
    
        if file_path:  # If a file is selected
            try:
                # Read the image using OpenCV
                image = cv.imread(file_path)
                if image is not None:
                    overlay = cv.resize(image, (self.original_image.shape[1], self.original_image.shape[0]))
                    self.master.image_container.overlay_image = overlay
                else:
                    Messagebox.show_error("Failed to load image", "Unsupported file format")
            except Exception as e:
                print(str(e))
                Messagebox.show_error("Error loading image", str(e))
        
    def _update_addition(self):
            
        original = self.original_image.copy()
        overlay = self.master.image_container.overlay_image.copy()
        addImage = cv.addWeighted(original, self.image_opacity_1.get(), overlay, self.image_opacity_2.get(), 0)
        # Update display
        self.master.image_container.current_image = addImage
        self.master.image_container.update_image()
        
    def _update_inverse(self):
            
        original = self.original_image.copy()
        # Update display
        self.master.image_container.current_image = 255 - original if self.invert_image.get() else original
        self.master.image_container.update_image()
    
    def _update_resize(self, *args):
        original = self.original_image.copy()
        scale_factor = self.resize_scale_var.get()
        scale_factor = max(0.1, min(2.0, scale_factor))
        interpolation = cv.INTER_AREA if scale_factor < 1 else cv.INTER_CUBIC
        resized = cv.resize(
            original,
            None, 
            fx=scale_factor, 
            fy=scale_factor,
            interpolation=interpolation
        )
        self.master.image_container.current_image = resized
        self.master.image_container.update_image()
        
    def _update_blur(self, *args):
        original = self.original_image.copy() 
        ksize = int(self.blur_scale_var.get())
        ksize = max(1, ksize)  # Ensure at least 1
        ksize = ksize + 1 if ksize % 2 == 0 else ksize  # Make odd since median blur only takes odd numbers
        self.master.image_container.current_image = cv.medianBlur(original, ksize)
        self.master.image_container.update_image()
        
    def _update_sharpness(self, *args):
        original = self.original_image.copy()  
        sharpness = self.sharpen_scale_var.get()
        
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        
        if sharpness > 0:
            # Normalize the kernel to maintain brightness
            center = 1 + sharpness * 4  # Center value scales with sharpness
            kernel = np.array([
                [ 0, -sharpness, 0],
                [-sharpness, center, -sharpness],
                [ 0, -sharpness, 0]
            ])
            
        sharpened = cv.filter2D(original, -1, kernel)
        self.master.image_container.current_image = np.clip(sharpened, 0, 255).astype(np.uint8)
        self.master.image_container.update_image()
    
    def _update_brightness(self, *args):
        original = self.original_image.copy()  
        # Update display
        self.master.image_container.current_image = cv.addWeighted(
            original, 
            self.contrast_scale_var.get(),
            np.zeros(original.shape, original.dtype),
            0,
            self.brightness_scale_var.get()
        )
        self.master.image_container.update_image()
    
    def _update_channels(self):
            
        original = self.original_image.copy()
        b, g, r = cv.split(original)
        
        # Apply channel toggles
        if not self.show_blue.get():
            b = np.zeros_like(b)
        if not self.show_green.get():
            g = np.zeros_like(g)
        if not self.show_red.get():
            r = np.zeros_like(r)
            
        # Update display
        self.master.image_container.current_image = cv.merge([b, g, r])
        self.master.image_container.update_image()
        
class ImageContainer(ttk.Frame): 
    def __init__(self, parent):
        super().__init__(parent)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Frame to hold the image at the top
        self.image_frame = ttk.Frame(self)
        self.image_frame.grid(row=0, column=0, sticky=NSEW)
        
        self.image_display = ttk.Label(self.image_frame)
        self.image_display.pack(side=TOP) 
        
        # Store for current cv image
        self.current_image = None
        self.overlay_image = None
        
    def update_image(self):
        # Convert from BGR to RGB, then convert to PIL format
        img_rgb = cv.cvtColor(self.current_image, cv.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        max_size = (800, 600)
        pil_img.thumbnail(max_size, Image.LANCZOS)
        
        self.tk_img = ImageTk.PhotoImage(pil_img)
        self.image_display.config(image=self.tk_img)
        
    def change_selected_image(self, category, sample):
        image_name = categories[category][sample]
        self.current_image = cv.imread('{}/{}/{}'.format(base_url, category, image_name))
        self.update_image()
        # Notify the right sidebar that the image has changed
        if hasattr(self.master, 'right_sidebar'):
            self.master.right_sidebar.on_image_changed(self.current_image.copy())