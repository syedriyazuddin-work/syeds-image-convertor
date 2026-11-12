"""
Quick converter for Windows Explorer right-click context menu.
Converts one or more files in place and displays a floating notification.
Run with pythonw.exe to prevent any console window from showing.
"""

import sys
import os
from pathlib import Path
from converter import convert_image, format_bytes, is_image_file, SUPPORTED_FORMATS
from toast import show_toast


def main():
    if len(sys.argv) < 3:
        show_toast("Syed's Image Convertor", "Usage: quick_convert.py <format> <file1> [file2...]", is_success=False)
        return

    target_format = sys.argv[1].upper()
    if target_format not in SUPPORTED_FORMATS:
        show_toast("Syed's Image Convertor Error", f"Unsupported target format: {target_format}", is_success=False)
        return

    raw_paths = sys.argv[2:]
    files_to_convert = []

    for item in raw_paths:
        p = Path(item)
        if p.is_file() and is_image_file(p):
            files_to_convert.append(p)
        elif p.is_dir():
            for child in p.iterdir():
                if child.is_file() and is_image_file(child):
                    files_to_convert.append(child)

    if not files_to_convert:
        show_toast("Syed's Image Convertor", "No valid image files found.", is_success=False)
        return

    success_count = 0
    total_original_bytes = 0
    total_new_bytes = 0
    last_output = None
    first_error = None

    for img_path in files_to_convert:
        res = convert_image(
            input_path=str(img_path),
            output_format=target_format,
            quality=85,
            lossless=False,
            resize_mode='original'
        )
        if res['success']:
            success_count += 1
            total_original_bytes += res['original_size']
            total_new_bytes += res['new_size']
            last_output = res['output_path']
        else:
            if not first_error:
                first_error = res.get('error', 'Unknown conversion error')

    if success_count > 0:
        savings = 0.0
        if total_original_bytes > 0:
            savings = round(((total_original_bytes - total_new_bytes) / total_original_bytes) * 100.0, 1)

        savings_str = f" ({savings}% saved)" if savings > 0 else ""

        if success_count == 1:
            out_name = Path(last_output).name
            msg = f"Converted to {out_name}\n{format_bytes(total_original_bytes)} ➔ {format_bytes(total_new_bytes)}{savings_str}"
        else:
            msg = f"Converted {success_count} images to {target_format}\n{format_bytes(total_original_bytes)} ➔ {format_bytes(total_new_bytes)}{savings_str}"

        show_toast(f"Syed's Image Convertor ➔ {target_format}", msg, file_to_reveal=last_output, is_success=True)
    else:
        show_toast("Conversion Failed", first_error or "Failed to convert image.", is_success=False)


if __name__ == '__main__':
    main()
