import win32com.client
import time
import os

# --- CONFIGURATION ---
FPGA_INDEX = 5
EXTENSION = ".txt"
SAVE_DIR = fr"D:\All_SelfLearning\Prj\1_\PUF_Experimental_Results\Full_Test\InitialValues\Raw\FPGA{FPGA_INDEX}"
AUTO_DELAY = 5  # Seconds to wait in Auto Mode

# The list of filename patterns you provided
# The script will replace "{index}" with the FPGA_INDEX variable defined above.
FILE_PATTERNS = [
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_1111_AAAA",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_2222_5555",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_4444_8888",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_4444_AAAA",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_5555_2222",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_5555_8888",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_8888_4444",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_8888_5555",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_AAAA_1111",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_AAAA_4444",
    "FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_AAAA_5555"
]
# ---------------------
def main():

    print("Connecting to RealTerm...")
    try:
        # Try to attach to an OPEN Realterm first (Fixes 'Ghost' instances)
        rt = win32com.client.GetActiveObject("Realterm.RealtermIntf")
    except:
        # If not open, launch a new one
        rt = win32com.client.Dispatch("Realterm.RealtermIntf")

    rt.Visible = True
    rt.Caption = "RealTerm - Python Controller"

    # Set Display to Binary (Bit view)
    rt.DisplayAs = 10

    # Set Baudrate (e.g., 9600, 115200, 921600)
    rt.Baud = 115200

    # --- MODE SELECTION ---
    print(f"\n--- FPGA Index set to: {FPGA_INDEX} ---")
    print(f"Total files to capture: {len(FILE_PATTERNS)}")
    print("-" * 30)
    print("\n--- SELECT MODE ---")
    print("[1] Manual Mode (Press Enter to start each capture)")
    print(f"[2] Auto Mode   (Starts automatically every {AUTO_DELAY} seconds)")
    mode = input(">> Type 1 or 2: ")
    # ----------------------

    try:
        for i, pattern in enumerate(FILE_PATTERNS):

            # 1. Prepare Filename
            clean_name = pattern.format(index=FPGA_INDEX)
            file_name = f"{clean_name}{EXTENSION}"
            full_path = os.path.join(SAVE_DIR, file_name)

            print(f"\n--- File {i + 1} of {len(FILE_PATTERNS)} ---")
            print(f"Name: {file_name}")

            # 2. WAIT LOGIC (Enter or Timer)
            if mode == '2':
                print(f"Waiting {AUTO_DELAY} seconds...")
                time.sleep(AUTO_DELAY)
            else:
                input("Press [Enter] to START 5s capture...")

            # 3. Clear Screen & Start
            # We clear NOW (after the wait) so you can see previous data while waiting
            rt.ClearTerminal()

            # 3. Set filename and Start
            rt.CaptureFile = full_path
            rt.Capture = 1  # Start Capture
            print(">> Capture STARTED... (Waiting for RealTerm to finish)")

            # 4. SMART WAIT: Loop until RealTerm stops itself
            # We check the status every 0.5 seconds
            while rt.Capture == 1:
                time.sleep(0.5)

            # 5. RealTerm finished (10s passed), so we move to next
            print(">> Capture FINISHED automatically.")

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()