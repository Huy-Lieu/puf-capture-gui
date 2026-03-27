import win32com.client
import time
import os

# --- CONFIGURATION ---
FPGA_INDEX = 12
EXTENSION = ".txt"
SAVE_DIR = fr"D:\All_SelfLearning\Prj\1_\PUF_Experimental_Results\Full_Test\FF_Placement\Raw\FPGA{FPGA_INDEX}"
AUTO_DELAY = 5  # Seconds to wait in Auto Mode

# The list of filename patterns you provided
# The script will replace "{index}" with the FPGA_INDEX variable defined above.
FILE_PATTERNS = [

# MDIST 8
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_AFF",

# MDIST 7
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M1_M7_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M1_M7_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M1_M7_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M1_M7_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M0_M6_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M0_M6_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M0_M6_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST7_M0_M6_AFF",

# MDIST 6
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M2_M7_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M2_M7_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M2_M7_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M2_M7_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M1_M6_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M1_M6_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M1_M6_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M1_M6_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M0_M5_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M0_M5_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M0_M5_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST6_M0_M5_AFF",

# MDIST 5
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M3_M7_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M3_M7_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M3_M7_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M3_M7_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M2_M6_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M2_M6_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M2_M6_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M2_M6_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M1_M5_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M1_M5_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M1_M5_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M1_M5_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M0_M4_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M0_M4_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M0_M4_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST5_M0_M4_AFF",

# MDIST 4
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M3_M6_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M3_M6_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M3_M6_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M3_M6_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M2_M5_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M2_M5_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M2_M5_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M2_M5_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M1_M4_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M1_M4_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M1_M4_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST4_M1_M4_AFF",

# MDIST 3
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M3_M5_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M3_M5_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M3_M5_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M3_M5_AFF",

"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M2_M4_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M2_M4_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M2_M4_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST3_M2_M4_AFF",

# MDIST 2
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST2_M3_M4_DFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST2_M3_M4_CFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST2_M3_M4_BFF",
"FPGA{index}_LDIST6_DLUTA_ALUTB_MDIST2_M3_M4_AFF",

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