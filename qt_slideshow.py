import random
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import requests
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QPixmap
from PIL import Image, ImageQt
from pillow_heif import register_heif_opener

load_dotenv()

# this is used to read heic files from iPhone; the program would be simpler w/o this support
register_heif_opener()
 
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".bmp", ".gif",".heic", ".HEIC")
# These are used to retrieve the current temp from HomeAssistant. Remove get_temp()
API_KEY = os.getenv('API_KEY')
TEMP_URL = os.getenv('TEMP_URL')

#PATH = Path(r'/Users/user/Documents') #Example path on macos
PATH = Path(r"Z:\General\Images\ImagesShared\Frame") #Windows path...for reasons I don't understand it shouldn't end in a final back slash

class Slideshow(QWidget):
    """Get a list of files and show them in a 1080p window"""
    def __init__(self):
        super().__init__()

        self.numFiles = 0
        self.files = self.get_image_files()
        self.current_index = -1
        self.paused = False
        
        self.setWindowTitle("Slideshow")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(1920, 1080)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setGeometry(0, 0, 1920, 1080)

        self.text_label = QLabel(self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setGeometry(10, 10, 100, 50)
        self.text_label.setFont(QFont('Arial', 16))
        self.text_label.setStyleSheet(
            'QLabel { color: white; background-color: black; padding: 10px; }')

        self.paused_label = QLabel(self)
        self.paused_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.paused_label.setGeometry(0, 75, 200, 100)
        self.paused_label.setText("Paused")
        self.paused_label.setStyleSheet("color: red; font-size: 50px;")
        self.paused_label.hide()
        
        self.qpixmap = QPixmap()

        self.setCursor(Qt.CursorShape.BlankCursor)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_image)
        self.speed = 10000
        self.timer.start(self.speed)

        self.pause_timer = QTimer(self)
        self.pause_timer.timeout.connect(self.show_pause)
        self.pause_timer.start(1000)

    def show_pause(self):
        """Flip the state of the paused variable"""
        if self.paused:
            self.paused_label.show()
        else:
            self.paused_label.hide()

    def get_image_files(self):
        """Get a list of files"""
        files = [str(file_path) for file_path in PATH.glob("*") if file_path.suffix in SUPPORTED_EXTENSIONS]
        #files = [os.path.join(PATH, f) for f in os.listdir(PATH) if f.endswith(SUPPORTED_EXTENSIONS)]
        if len(files) == 0:
            print("No files found.")
            sys.exit()
        random.shuffle(files)
        self.numFiles = len(files)
        print('number of file', self.numFiles)
        return files

    def get_pixmap(self, file):
        """Convert an image file to a QPixmap object
           This should be safe for any image in the SUPPORTED tuple"""
        #print('file to open: ', file)
        pimage = Image.open(file)
        qimage = ImageQt.ImageQt(pimage)
        self.qpixmap = QPixmap.fromImage(qimage).scaled(1920, 1080, Qt.AspectRatioMode.KeepAspectRatio)
        # use the following if no need for heic support
        #self.qpixmap = QPixmap(file).scaled(1920, 1080, Qt.AspectRatioMode.KeepAspectRatio)
        return self.qpixmap

    def show_image(self, index):
        """Show the image at the given index"""
        if not 0 <= index < self.numFiles:
            print("Error: index out of range ", self.numFiles )
            return
        file = self.files[index]
        qpixmap = self.get_pixmap(file)
        self.image_label.setPixmap(qpixmap)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        print(self.current_index)        
        self.text_label.setText(f"{get_temp()}\u00B0 F")

    def show_next_image(self):
        """Show the next image in the slideshow"""
        if self.paused:
            return
        self.current_index += 1
        if self.current_index >= len(self.files):
            self.current_index = 0
        self.show_image(self.current_index)

    def keyPressEvent(self, event):
        """Handle key presses"""
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
            return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Space):
            self.paused = not self.paused
            return
        if key == Qt.Key.Key_Space:
            self.paused = not self.paused
            return
        if key == Qt.Key.Key_Left:  
            self.current_index-= 1
            if self.current_index < 0:
                self.current_index = len(self.files) - 1
            self.show_image(self.current_index)
            return
        if key == Qt.Key.Key_Right:
            self.current_index += 1
            if self.current_index >= len(self.files):
                self.current_index = 0
            self.show_image(self.current_index)
            return
        if key == Qt.Key.Key_Up:
            self.speed += 1000
            self.timer.start(self.speed)
            return
        if key == Qt.Key.Key_Down:
            if self.speed >= 1:
                self.speed -= 1000
                self.timer.start(self.speed)
            return
        return

def get_temp():
    """Get temp from HomeAssistant"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(TEMP_URL, headers=headers, timeout=5.0)
        return response.json()['state']
    except requests.exceptions.Timeout:
        print('API call timed out.')
        return 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    slideshow = Slideshow()
    slideshow.show()
    sys.exit(app.exec())
