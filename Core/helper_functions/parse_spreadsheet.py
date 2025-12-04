from openpyxl import load_workbook
import shutil
import os
from datetime import datetime
import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):  # PyInstaller sets this for onefile builds
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent  # or your project root
    return base_path / relative_path

def format_and_export_to_excel(row_general, row_supine, duplicate_file='python_coverage.xlsx', last_block_cols=8, patient_age=8, patient_sex=5):
    """
    Unified workflow:
      1) Duplicate the original Excel file.
      2) Write:
         - row_general -> Tab 1 B3:AH3 (33 cells)
         - row_supine  -> Tab 1 B8:BU8 (72 cells)
      3) Prompt for tab selection (5 or 6), then copy age-based block:
         - A..E (two rows) -> Tab 2 A7:E8; A formatted as '<value or age>yoM/F'
         - F..M (or F..N)  -> Tab 3 R9..Y10 (or R..Z)
    """

    #original_file = 'EXAMPLE_Data_07-02-24.xlsx'
    original_file = resource_path('EXAMPLE_Data_07-02-24.xlsx')
    row_general = row_general[1:]

    # ---------- Helpers ----------
    def excel_col_range(start_col, end_col):
        """Return list of column letters from start_col to end_col inclusive."""
        def col_to_num(col):
            n = 0
            for ch in col:
                n = n * 26 + (ord(ch.upper()) - 64)
            return n
        def num_to_col(n):
            s = []
            while n:
                n, r = divmod(n - 1, 26)
                s.append(chr(r + 65))
            return ''.join(reversed(s))
        start_n, end_n = col_to_num(start_col), col_to_num(end_col)
        return [num_to_col(i) for i in range(start_n, end_n + 1)]

    def write_row(ws, start_col, row_idx, values, max_end_col):
        cols = excel_col_range(start_col, max_end_col)
        if len(values) > len(cols):
            raise ValueError(f"Too many values ({len(values)}) for range {start_col}:{max_end_col} ({len(cols)} cells).")
        for i, v in enumerate(values):
            ws[f"{cols[i]}{row_idx}"] = v

    def format_age_cell(value, gender_suffix, age_hint=None):
        """Format A cell as '<base>yoM/F'. If source A is empty, fall back to age_hint."""
        base = None
        if value is not None:
            try:
                num = float(value)
                base = str(int(num)) if num.is_integer() else str(num)
            except Exception:
                base = str(value)
        elif age_hint is not None:
            base = str(age_hint)
        return f"{base}yo{gender_suffix}" if base is not None else None

    # ---------- Prompt for tab selection (keep this interactive) ----------
    option = patient_sex
    if option not in {5, 6}:
        raise ValueError("Please enter 5 or 6.")
    tab_option = int(option)
    gender_suffix = "F" if tab_option == 5 else "M"

    if not (8 <= patient_age <= 18):
        raise ValueError("Age must be between 8 and 18.")

    # ---------- Prepare destination filename ----------
    if duplicate_file is None:
        base, ext = os.path.splitext(original_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        duplicate_file = f"{base}_COPY_{timestamp}{ext}"

    # ---------- Duplicate the file ----------
    shutil.copy(original_file, duplicate_file)

    # ---------- Load workbooks ----------
    wb_src = load_workbook(original_file, data_only=True)
    wb_dst = load_workbook(duplicate_file)

    # ---------- Validations ----------
    if len(wb_src.sheetnames) < 6:
        raise ValueError("Source workbook must have at least 6 sheets (to access tabs 5 and 6).")
    if len(wb_dst.sheetnames) < 3:
        raise ValueError("Destination workbook must have at least 3 sheets (tabs 1, 2, and 3).")
    if not (8 <= patient_age <= 18):
        raise ValueError("Age must be between 8 and 18.")
    if len(row_general) > 33:
        raise ValueError("row_general exceeds 33 columns (B..AH).")
    if len(row_supine) > 72:
        raise ValueError("row_supine exceeds 72 columns (B..BU).")

    # ---------- Resolve sheets ----------
    tab1_ws = wb_dst[wb_dst.sheetnames[0]]             # Tab 1
    tab2_ws = wb_dst[wb_dst.sheetnames[1]]             # Tab 2
    tab3_ws = wb_dst[wb_dst.sheetnames[2]]             # Tab 3
    src_ws = wb_src[wb_src.sheetnames[tab_option - 1]] # Tab 5 or 6 from source

    # ---------- 1) Write to Tab 1 ----------
    write_row(tab1_ws, start_col="B", row_idx=3, values=row_general, max_end_col="AH")  # B3:AH3
    write_row(tab1_ws, start_col="B", row_idx=8, values=row_supine,  max_end_col="BU")  # B8:BU8

    # ---------- 2) Age-based row mapping ----------
    # Age 8 -> rows 3 & 4; Age 9 -> 7 & 8; Age 10 -> 11 & 12; ...
    start_row = 3 + (patient_age - 8) * 4
    src_rows = [start_row, start_row + 1]

    # ---------- 3) Copy A..E -> Tab 2 A7:E8 (A formatted as '<value or age>yoM/F') ----------
    cols_A_to_E = excel_col_range("A", "E")
    for i, r in enumerate(src_rows):
        values = [src_ws[f"{c}{r}"].value for c in cols_A_to_E]
        values[0] = format_age_cell(values[0], gender_suffix, age_hint=patient_age)  # modify A with fallback
        write_row(tab2_ws, start_col="A", row_idx=7 + i, values=values, max_end_col="E")

    # ---------- 4) Copy F..M (or F..N) -> Tab 3 R9..Y10 (or R..Z) ----------
    src_end = "M" if last_block_cols == 8 else "N"
    dst_end = "Y" if last_block_cols == 8 else "Z"
    cols_src = excel_col_range("F", src_end)   # F..M or F..N
    cols_dst = excel_col_range("R", dst_end)   # R..Y or R..Z

    if len(cols_src) != len(cols_dst):
        raise RuntimeError("Source and destination block sizes do not match.")

    for i, r in enumerate(src_rows):
        values = [src_ws[f"{c}{r}"].value for c in cols_src]
        for j, v in enumerate(values):
            tab3_ws[f"{cols_dst[j]}{9 + i}"] = v

    # ---------- Save ----------
    wb_dst.save(duplicate_file)

    return {
        "duplicate_file": duplicate_file,
        "source_tab": src_ws.title,
        "gender_suffix": gender_suffix,
        "age_rows": src_rows,
        "tab1_written": {"B3:AH3": len(row_general), "B8:BU8": len(row_supine)},
        "tab2_written_rows": [7, 8],
        "tab3_written_rows": [9, 10],
        "last_block_cols": last_block_cols
    }