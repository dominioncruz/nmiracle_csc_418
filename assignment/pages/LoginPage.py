import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pathlib import Path
from tkinter import PhotoImage
from PIL import Image, ImageTk
from ttkbootstrap.dialogs import Messagebox
import re

from pages.DashboardPage import DashboardPage



class LoginPage(ttk.Frame):
    def __init__(self, parent: ttk.Window):
        super().__init__(parent)
        
        # Configuration for root window
        parent.title("YSMA Image Transformer")
        parent.geometry("800x600")  
        parent.resizable(False, False)

        # Pack the whole LoginPage to expand to full screen
        self.pack(fill=BOTH, expand=YES)
        
        # Column 1 - Form (packed side by side, with remaining space)
        self.col1 = InputForm(self)
        self.col1.pack(side=LEFT, fill=BOTH, expand=YES)

        # Column 2 - Right image (packed side by side)
        self.col2 = FormImage(self)
        self.col2.pack(side=RIGHT)
    


class FormImage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        img_path = Path(__file__).parent.parent / 'assets/login_img.jpeg'
        image = Image.open(img_path)
        
        # Resize the image to fit the specified width and height
        image = image.resize((400, 600), Image.LANCZOS)
        
        self.login_image = ImageTk.PhotoImage(image)
        self.media = ttk.Label(self, image=self.login_image)
        self.media.pack()

class InputForm(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(20, 0))
        
        style = ttk.Style()
        style.configure("LoginForm.TLabel",
            font=("Inter", 12),
            padding=(0, 0, 0, 10),
            
        ) 

        style.configure("LoginForm.TEntry",
            font=("Inter", 11),
            padding=(15, 15),
        )
        
        self.email = ttk.StringVar(value="")
        self.password = ttk.StringVar(value="")
            
        # Pack the form to fill the available space
        self.pack(side=TOP, fill=BOTH, expand=YES)
        
        # Top spacer (pushes content down)
        self.top_spacer = ttk.Frame(self, height=0)
        self.top_spacer.pack(side=TOP, fill=BOTH, expand=YES)
        
        # Content container (will be centered)
        self.content = ttk.Frame(self)
        self.content.pack(fill=X, expand=YES)

        # Title label
        self.header = ttk.Label(
            master=self.content,
            font="Inter 16",
            text="Welcome to YSMA"
        )
        self.header.pack(pady=(0, 40))
        
        #Username input container
        self.username_container = ttk.Frame(self.content)
        self.username_container.pack(side=TOP, fill=BOTH, expand=YES, pady=(0, 25))
        self.username_label = ttk.Label(self.username_container, text="Email Address:", style="LoginForm.TLabel")
        self.username_label.pack(side=TOP, anchor=W)  
        self.username_field = ttk.Entry(self.username_container, style="LoginForm.TEntry", textvariable=self.email)
        self.username_field.pack(side=TOP, fill=X)
        
        #Password input container
        self.password_container = ttk.Frame(self.content)
        self.password_container.pack(side=TOP, fill=BOTH, expand=YES, pady=(0, 40))
        self.password_label = ttk.Label(self.password_container, text="Password:", style="LoginForm.TLabel")
        self.password_label.pack(side=TOP, anchor=W)  
        self.password_field = ttk.Entry(self.password_container, show='*',  style="LoginForm.TEntry", textvariable=self.password)
        self.password_field.pack(side=TOP, fill=X)
        
        # Login button
        self.login_button = ttk.Button(
            self.content, 
            text="Login", 
            bootstyle="secondary-outline",
            padding=(0, 15),
            command=self.on_submit
        )
        self.login_button.pack(side=TOP, fill=X)
        
        # Top spacer (pushes content down)
        self.bottom_spacer = ttk.Frame(self, height=0)
        self.bottom_spacer.pack(side=TOP, expand=YES)
        
    def on_submit(self, *args):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, self.email.get(), re.IGNORECASE):
            Messagebox.show_error(title='Login Failed', message='Invalid email or password')
            self.email.set('')
            self.password.set("")
        else:
            parent = self.master.master
            for widget in parent.winfo_children():
                widget.destroy()
            DashboardPage(parent)
        self.email.set('')
        self.password.set('')


