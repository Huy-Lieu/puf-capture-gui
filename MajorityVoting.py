from PyQt6 import QtWidgets
import sys
import win32com.client as win32
from pathlib import Path

class GUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("Majority Voting Final Response")
        self.resize(900, 200)

        self.btn = QtWidgets.QPushButton("Select file")
        self.btn.clicked.connect(self.pick)

        # Output box for final majority result (later)
        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Majority-voted result will appear here...")

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

        all_results = []

        for filename in filenames:
            file_path = Path(filename)
            # File Reading and Data Cleaning
            # Open and read the file content
            with open(file_path, "r") as file:
                puf_responses = file.readlines()

            # This filters out empty lines, removes all whitespace from the remaining lines
            puf_responses = ["".join(line.split()) for line in puf_responses if line.strip()]

            # --- This is where I suggested inserting the slice ---
            puf_responses = puf_responses[:100]  # 3. Slices the list

            # Majority Voting
            majority_result = self.bitwise_majority_voting(puf_responses)

            # Uniformity Calculation
            # Counter the number of '1's
            num_ones = majority_result.count('1')
            total_bits = 128
            uniformity = (num_ones / float(total_bits)) * 100.0
            # Include all necessary data fields: name, rows used, and the result.
            all_results.append({
                "Filename": file_path.name,
                "Majority Response": majority_result,
                "Uniformity": uniformity
            })

        self.display_all_results(all_results)
        self.create_Excel(all_results)

    def display_all_results(self, results):
        """
        Formats and displays the results of multiple file processes in the GUI output box.

        Args:
            results (list of dict): A list of structured dictionaries, where each
                                    dictionary contains the result for one file.
                                    Expected keys: "Filename", "Majority Response".
        """

        # 1. Clear the box once at the start to ensure a fresh display
        self.output_box.clear()

        # 2. Use append() to add each result sequentially
        for i, res in enumerate(results):
            # Display result for the current file
            self.output_box.append(f"### Result for File #{i + 1}: **{res['Filename']}**")

            # Display metadata
            self.output_box.append("Final Majority-Voted Response:")

            # Append the potentially long result string
            self.output_box.append(f"{res['Majority Response']}")

            # Uniformity
            # Display metadata
            self.output_box.append("Uniformity:")
            self.output_box.append(f"{res['Uniformity']}%")
            self.output_box.append("-" * 175)  # Separator between file results

    def create_Excel(self, results):
        excel = win32.Dispatch("Excel.Application")
        excel.Visible = True
        wb = excel.Workbooks.Add()
        sheet = wb.ActiveSheet

        # --- Get Headers (Now guaranteed to be ["File_Name", "Final_Response", "Uniformity"]) ---
        headers = list(results[0].keys())
        # Write Headers to the first row (Row 1)
        # This writes "File_Name" to A1 and "Final_Response" to B1
        for col_index, header in enumerate(headers):
            sheet.Cells(1, col_index + 1).Value = header

        # 3. Write Data starting from the second row (Row 2)
        for row_index, result_dict in enumerate(results):
            current_excel_row = row_index + 2

            # Write data for the current file
            for col_index, header in enumerate(headers):
                value = result_dict[header]
                sheet.Cells(current_excel_row, col_index + 1).NumberFormat = "@"
                sheet.Cells(current_excel_row, col_index + 1).Value = value

        sheet.Columns.AutoFit()
        print(f"Successfully exported results to a new Excel spreadsheet.")

    def bitwise_majority_voting(self, puf_responses):
        """
        Analyzes a list of bit strings and performs bit-wise majority voting,
        returning the result as a string of '0's and '1's.

        The majority bit is the one that strictly appears MORE than N/2 times.
        In the case of a tie (count equals N/2), the bit is defaulted to '0'.

        Args:
            puf_responses (list of str): A list of strings, e.g., ['101', '110', '001'].

        Returns:
            str: The aggregated result as a string of '0's and '1's.
        """

        # Define Constant
        # Total number of responses (rows)
        NUM_ROWS = 100
        # Length of each response (columns)
        NUM_BITS = 128
        # Majority Threshold (N/2)
        MAJORITY_THRESHOLD = NUM_ROWS / 2.0

        if not puf_responses: # Return a 128-bit zero string if input is empty
            return "0" * NUM_BITS

        final_puf_response = []

        # Iterate through each bit position (column) from 0 to 127
        for bit_position in range(NUM_BITS):

            # 1. Count the '1's in the current column
            one_count = 0
            for puf_response in puf_responses:
                # Check the bit at the current position
                if puf_response[bit_position] == '1':
                    one_count += 1

            # 2. Apply the Majority Rule (Count > N/2)
            if one_count > MAJORITY_THRESHOLD:
                final_puf_response.append('1')
            else:
                final_puf_response.append('0')

        return "".join(final_puf_response)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = GUI()
    w.show()
    # w.create_Excel() # Test Here
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
