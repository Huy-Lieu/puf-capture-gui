from PyQt6 import QtWidgets
import sys
import win32com.client as win32
from pathlib import Path
import os

class GUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("Clean Data - Converter")
        self.resize(400, 100)

        self.btn = QtWidgets.QPushButton("Select file")
        self.btn.clicked.connect(self.pick)

        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Start the Conversion.....")

        # Layout: button on top, output below
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.btn)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

    def pick(self):
        # File dialog
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select PUF Response Files",  # Updated dialog title
            "",
            "Text files (*.txt *.csv);;All files (*.*)",
        )
        if not filenames:
            return

        for filename in filenames:
            file_path = Path(filename)

            # Create Output Path
            output_filename = f"{file_path.stem}_Clean{file_path.suffix}"
            output_path = file_path.with_name(output_filename)

            print(f"Processing: {file_path.name} -> {output_path.name}")

            # File Reading and Data Cleaning
            # Open and read the file content
            with open(file_path, "rb") as file:
                raw_data = file.read()

            clean_data = raw_data.rstrip(b'\r\n')

            # Convert
            with open(output_path, "w") as file_out:
                total_len = len(clean_data)

                for i in range(0, total_len, 16):
                    # Grab 16 bytes (or whatever is left)
                    chunk = clean_data[i : i + 16]

                    # Convert bytes to "11111111" strings
                    binary_list = [format(byte, '08b') for byte in chunk]

                    # Join with spaces
                    line_string = " ".join(binary_list)

                    # Write to file
                    file_out.write(line_string + "\n")
        self.output_box.clear()
        self.output_box.append("All selected files have been cleaned.")
        print("All selected files have been cleaned.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = GUI()
    w.show()
    # w.create_Excel() # Test Here
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
