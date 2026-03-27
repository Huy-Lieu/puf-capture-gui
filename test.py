import win32com.client
import time
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- DEFAULTS (used only to pre-fill the GUI) ---
DEFAULT_FPGA_INDEX = 5
DEFAULT_EXTENSION = ".txt"
DEFAULT_AUTO_DELAY = 5

DEFAULT_BASE_DIR = r"D:\All_SelfLearning\Prj\1_\PUF_Experimental_Results\Full_Test\InitialValues\Raw"


def get_config_gui():
    """
    Mode A:
      User selects BASE_DIR, FPGA_INDEX, EXTENSION, AUTO_DELAY.
      SAVE_DIR is auto-generated: BASE_DIR\\FPGA{FPGA_INDEX}
    Returns a dict: {FPGA_INDEX, EXTENSION, AUTO_DELAY, SAVE_DIR}
    """
    root = tk.Tk()
    root.title("PUF Capture Config")
    root.resizable(False, False)

    # Variables
    fpga_var = tk.IntVar(value=DEFAULT_FPGA_INDEX)
    ext_var = tk.StringVar(value=DEFAULT_EXTENSION)
    delay_var = tk.DoubleVar(value=DEFAULT_AUTO_DELAY)
    base_var = tk.StringVar(value=DEFAULT_BASE_DIR)

    # --- UI layout ---
    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frm, text="FPGA Index:").grid(row=0, column=0, sticky="w", pady=4)
    fpga_spin = ttk.Spinbox(frm, from_=1, to=999, textvariable=fpga_var, width=10)
    fpga_spin.grid(row=0, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Extension:").grid(row=1, column=0, sticky="w", pady=4)
    ext_entry = ttk.Entry(frm, textvariable=ext_var, width=14)
    ext_entry.grid(row=1, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Auto Delay (sec):").grid(row=2, column=0, sticky="w", pady=4)
    delay_spin = ttk.Spinbox(frm, from_=0, to=9999, increment=0.5, textvariable=delay_var, width=10)
    delay_spin.grid(row=2, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Base Save Folder:").grid(row=3, column=0, sticky="w", pady=4)
    base_entry = ttk.Entry(frm, textvariable=base_var, width=55)
    base_entry.grid(row=3, column=1, sticky="w", pady=4)

    def browse_base():
        folder = filedialog.askdirectory(title="Select Base Folder")
        if folder:
            base_var.set(folder)

    ttk.Button(frm, text="Browse...", command=browse_base).grid(row=3, column=2, padx=8, pady=4)

    # Live preview of SAVE_DIR
    preview_var = tk.StringVar()

    def update_preview(*_):
        try:
            idx = int(fpga_var.get())
        except Exception:
            idx = 0
        preview_var.set(os.path.join(base_var.get(), f"FPGA{idx}"))

    fpga_var.trace_add("write", update_preview)
    base_var.trace_add("write", update_preview)
    update_preview()

    ttk.Label(frm, text="Save Dir Preview:").grid(row=4, column=0, sticky="w", pady=(10, 4))
    ttk.Label(frm, textvariable=preview_var).grid(row=4, column=1, columnspan=2, sticky="w", pady=(10, 4))

    # Buttons
    result = {}

    def validate_and_run():
        # Validate FPGA index
        try:
            idx = int(fpga_var.get())
            if idx < 1:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid Input", "FPGA Index must be a positive integer.")
            return

        # Validate extension
        ext = ext_var.get().strip()
        if not ext:
            messagebox.showerror("Invalid Input", "Extension cannot be empty (e.g., .txt).")
            return
        if not ext.startswith("."):
            ext = "." + ext  # auto-fix

        # Validate delay
        try:
            dly = float(delay_var.get())
            if dly < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid Input", "Auto Delay must be a number >= 0.")
            return

        base = base_var.get().strip()
        if not base:
            messagebox.showerror("Invalid Input", "Base folder cannot be empty.")
            return
        if not os.path.isdir(base):
            messagebox.showerror("Invalid Input", "Base folder does not exist. Please choose a valid folder.")
            return

        save_dir = os.path.join(base, f"FPGA{idx}")
        os.makedirs(save_dir, exist_ok=True)

        result.update({
            "FPGA_INDEX": idx,
            "EXTENSION": ext,
            "AUTO_DELAY": dly,
            "SAVE_DIR": save_dir
        })
        root.destroy()

    def cancel():
        root.destroy()

    btn_row = ttk.Frame(frm)
    btn_row.grid(row=5, column=0, columnspan=3, sticky="e", pady=(12, 0))

    ttk.Button(btn_row, text="Cancel", command=cancel).grid(row=0, column=0, padx=6)
    ttk.Button(btn_row, text="Run", command=validate_and_run).grid(row=0, column=1, padx=6)

    root.mainloop()
    return result if result else None


# ---------------------
# Your patterns stay the same
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


def main(cfg):
    FPGA_INDEX = cfg["FPGA_INDEX"]
    EXTENSION = cfg["EXTENSION"]
    SAVE_DIR = cfg["SAVE_DIR"]
    AUTO_DELAY = cfg["AUTO_DELAY"]

    print("Connecting to RealTerm...")
    try:
        rt = win32com.client.GetActiveObject("Realterm.RealtermIntf")
    except:
        rt = win32com.client.Dispatch("Realterm.RealtermIntf")

    rt.Visible = True
    rt.Caption = "RealTerm - Python Controller"
    rt.DisplayAs = 10
    rt.Baud = 115200

    print(f"\n--- FPGA Index set to: {FPGA_INDEX} ---")
    print(f"Save Dir: {SAVE_DIR}")
    print(f"Total files to capture: {len(FILE_PATTERNS)}")

    print("\n--- SELECT MODE ---")
    print("[1] Manual Mode (Press Enter to start each capture)")
    print(f"[2] Auto Mode   (Starts automatically every {AUTO_DELAY} seconds)")
    mode = input(">> Type 1 or 2: ")

    try:
        for i, pattern in enumerate(FILE_PATTERNS):
            clean_name = pattern.format(index=FPGA_INDEX)
            file_name = f"{clean_name}{EXTENSION}"
            full_path = os.path.join(SAVE_DIR, file_name)

            print(f"\n--- File {i + 1} of {len(FILE_PATTERNS)} ---")
            print(f"Name: {file_name}")

            if mode == '2':
                print(f"Waiting {AUTO_DELAY} seconds...")
                time.sleep(AUTO_DELAY)
            else:
                input("Press [Enter] to START 5s capture...")

            rt.ClearTerminal()
            rt.CaptureFile = full_path
            rt.Capture = 1
            print(">> Capture STARTED... (Waiting for RealTerm to finish)")

            while rt.Capture == 1:
                time.sleep(0.5)

            print(">> Capture FINISHED automatically.")

    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    cfg = get_config_gui()
    if cfg is None:
        print("Canceled.")
    else:
        main(cfg)
