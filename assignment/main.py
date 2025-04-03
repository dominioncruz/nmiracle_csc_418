import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pages.LoginPage import LoginPage


def main():
    app = Application();
    app.mainloop();
    

#App is a ttk instance as it extends ttk.Window
class Application(ttk.Window):
    def __init__(self):
        super().__init__(themename="lumen");
        LoginPage(self);
    
    
if __name__== "__main__":
    main();