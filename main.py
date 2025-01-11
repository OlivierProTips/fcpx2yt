import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QTextEdit, QPushButton, QFileDialog,
                              QLabel, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtGui import QGuiApplication

class ChapterViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chapter Viewer")
        self.setMinimumSize(600, 400)
        
        # Set up the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Style settings
        self.setStyle()
        
        # Create widgets
        self.create_widgets(layout)
        
    def setStyle(self):
        # Set dark theme palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #2a82da;
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
        """
        
    def create_widgets(self, layout):
        # Title label
        title_label = QLabel("FCPXML Chapter Viewer")
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Create text edit widget instead of table
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)  # Make it read-only
        self.text_display.setFont(QFont('Courier New', 15))  # Use monospace font
        layout.addWidget(self.text_display)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Create load button
        load_button = QPushButton("Load FCPXML")
        load_button.setStyleSheet(self.get_button_style())
        load_button.clicked.connect(self.load_xml)
        button_layout.addWidget(load_button)
        
        # Create copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.setStyleSheet(self.get_button_style())
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
        
    def copy_to_clipboard(self):
        # Get the text from the display
        text = self.text_display.toPlainText()
        
        # Copy to clipboard
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        
        # Optional: Flash the copy button or show a status message
        self.statusBar().showMessage("Copied to clipboard!", 2000)

    def find_fcpxml_in_directory(self, directory):
        """Find the first .fcpxml file in the given directory."""
        for file in os.listdir(directory):
            if file.endswith('.fcpxml'):
                return os.path.join(directory, file)
        return None
        
    def parse_time(self, time_str):
        # Remove 's' suffix if present
        time_str = time_str.replace('s', '')
        
        # Handle fraction format (e.g., "1579/25")
        if '/' in time_str:
            num, den = map(int, time_str.split('/'))
            seconds = float(Fraction(num, den))
        else:
            seconds = float(time_str)
        
        # Convert to minutes and seconds
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        # Format as MM:SS
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    def process_xml_file(self, filename):
        """Process the XML file and return formatted text."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Find all chapter-marker elements
            chapter_markers = root.findall('.//chapter-marker')
            
            # Create formatted text output
            output_text = "TIME     CHAPTER\n"
            output_text += "-------------------\n"
            
            # Add chapters to text display
            for marker in chapter_markers:
                start = self.parse_time(marker.get('start'))
                value = marker.get('value')
                output_text += f"{start} - {value}\n"
            
            return output_text
            
        except ET.ParseError:
            return "Error: Invalid XML file"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def load_xml(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select FCPXML File or Directory",
            "",
            "FCPXML Files (*.fcpxml *.fcpxmld);;All Files (*)"
        )
        
        if not filename:
            return
            
        self.text_display.clear()
        
        if filename.endswith('.fcpxmld'):
            # Handle directory
            if os.path.isdir(filename):
                xml_file = self.find_fcpxml_in_directory(filename)
                if xml_file:
                    output_text = self.process_xml_file(xml_file)
                else:
                    output_text = "Error: No .fcpxml file found in directory"
            else:
                output_text = "Error: Selected .fcpxmld is not a directory"
        else:
            # Handle direct .fcpxml file
            output_text = self.process_xml_file(filename)
            
        self.text_display.setText(output_text)

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle('Fusion')
    
    viewer = ChapterViewer()
    viewer.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()