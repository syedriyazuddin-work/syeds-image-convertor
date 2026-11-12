"""
Core image conversion engine for AnyWebP Local.
Supports high-performance batch conversions between WebP, PNG, JPG, AVIF, HEIC, GIF, ICO, BMP, TIFF, and PDF.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageSequence

# Register HEIC and AVIF openers if available
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

try:
    import pillow_avif
except ImportError:
    pass

SUPPORTED_FORMATS = {
    'WEBP': {'ext': '.webp', 'name': 'WebP Image', 'supports_lossless': True, 'supports_quality': True},
    'PNG':  {'ext': '.png',  'name': 'PNG Image',  'supports_lossless': True, 'supports_quality': False},
    'JPG':  {'ext': '.jpg',  'name': 'JPEG Image', 'supports_lossless': False, 'supports_quality': True},
    'JPEG': {'ext': '.jpeg', 'name': 'JPEG Image', 'supports_lossless': False, 'supports_quality': True},
    'AVIF': {'ext': '.avif', 'name': 'AVIF Image', 'supports_lossless': False, 'supports_quality': True},
    'GIF':  {'ext': '.gif',  'name': 'GIF Image',  'supports_lossless': True, 'supports_quality': False},
    'ICO':  {'ext': '.ico',  'name': 'Windows Icon', 'supports_lossless': True, 'supports_quality': False},
    'BMP':  {'ext': '.bmp',  'name': 'Bitmap Image', 'supports_lossless': True, 'supports_quality': False},
    'TIFF': {'ext': '.tiff', 'name': 'TIFF Image', 'supports_lossless': True, 'supports_quality': False},
    'PDF':  {'ext': '.pdf',  'name': 'PDF Document', 'supports_lossless': True, 'supports_quality': False},
}

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif',
    '.avif', '.heic', '.heif', '.ico', '.jfif', '.ppm', '.tga'
}


def is_image_file(path_str):
    """Check if the given file path has a recognized image extension."""
    return Path(path_str).suffix.lower() in IMAGE_EXTENSIONS


def format_bytes(size):
    """Format bytes into human readable string (KB, MB, GB)."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"


def get_image_info(image_path):
    """Retrieve metadata and thumbnail dimensions for an image."""
    try:
        path = Path(image_path)
        if not path.is_file():
            return None
        file_size = path.stat().st_size
        with Image.open(path) as img:
            width, height = img.size
            img_format = (img.format or path.suffix.strip('.')).upper()
            is_animated = getattr(img, "is_animated", False)
            return {
                'path': str(path.resolve()),
                'name': path.name,
                'extension': path.suffix.lower(),
                'size': file_size,
                'size_str': format_bytes(file_size),
                'width': width,
                'height': height,
                'dimensions_str': f"{width} × {height}",
                'format': img_format,
                'is_animated': is_animated
            }
    except Exception as e:
        return None


def calculate_new_dimensions(orig_w, orig_h, resize_mode='original', resize_scale=100,
                             custom_width=None, custom_height=None, keep_aspect_ratio=True):
    """Calculate target dimensions according to resize settings."""
    if resize_mode == 'original':
        return orig_w, orig_h

    if resize_mode == 'scale':
        scale = max(1, min(1000, resize_scale)) / 100.0
        new_w = max(1, int(round(orig_w * scale)))
        new_h = max(1, int(round(orig_h * scale)))
        return new_w, new_h

    if resize_mode == 'custom':
        tw = int(custom_width) if custom_width and int(custom_width) > 0 else orig_w
        th = int(custom_height) if custom_height and int(custom_height) > 0 else orig_h
        if keep_aspect_ratio:
            aspect = orig_w / float(orig_h)
            if custom_width and not custom_height:
                th = max(1, int(round(tw / aspect)))
            elif custom_height and not custom_width:
                tw = max(1, int(round(th * aspect)))
            else:
                # Both provided, fit within box maintaining aspect ratio
                ratio = min(tw / orig_w, th / orig_h)
                tw = max(1, int(round(orig_w * ratio)))
                th = max(1, int(round(orig_h * ratio)))
        return max(1, tw), max(1, th)

    return orig_w, orig_h


def convert_image(
    input_path,
    output_format='WEBP',
    output_dir=None,
    quality=85,
    lossless=False,
    resize_mode='original',
    resize_scale=100,
    custom_width=None,
    custom_height=None,
    keep_aspect_ratio=True,
    overwrite=False,
    bg_color=(255, 255, 255)
):
    """
    Convert a single image with custom options.
    
    Returns a dict with:
    - success (bool)
    - input_path (str)
    - output_path (str)
    - original_size (int)
    - new_size (int)
    - savings_percent (float)
    - original_dims (tuple)
    - new_dims (tuple)
    - error (str or None)
    """
    input_p = Path(input_path).resolve()
    if not input_p.is_file():
        return {
            'success': False,
            'input_path': str(input_p),
            'output_path': None,
            'error': f"Input file not found: {input_path}"
        }

    fmt = output_format.upper().strip()
    if fmt == 'JPEG':
        fmt = 'JPG'
    if fmt not in SUPPORTED_FORMATS:
        return {
            'success': False,
            'input_path': str(input_p),
            'output_path': None,
            'error': f"Unsupported output format: {output_format}"
        }

    target_ext = SUPPORTED_FORMATS[fmt]['ext']

    # Determine destination directory
    dest_dir = Path(output_dir).resolve() if output_dir else input_p.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Determine output file path
    base_stem = input_p.stem
    target_path = dest_dir / f"{base_stem}{target_ext}"

    # Handle collisions if overwrite is False
    if not overwrite and target_path.exists():
        counter = 1
        while target_path.exists():
            target_path = dest_dir / f"{base_stem}_{counter}{target_ext}"
            counter += 1

    original_size = input_p.stat().st_size

    try:
        with Image.open(input_p) as img:
            # Auto-orient based on EXIF tag if present
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            orig_w, orig_h = img.size
            new_w, new_h = calculate_new_dimensions(
                orig_w, orig_h,
                resize_mode=resize_mode,
                resize_scale=resize_scale,
                custom_width=custom_width,
                custom_height=custom_height,
                keep_aspect_ratio=keep_aspect_ratio
            )

            is_animated = getattr(img, "is_animated", False)

            # Resize if needed
            if (new_w, new_h) != (orig_w, orig_h):
                if is_animated and fmt in ('GIF', 'WEBP'):
                    frames = []
                    durations = []
                    for frame in ImageSequence.Iterator(img):
                        durations.append(frame.info.get('duration', 100))
                        resized_frame = frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        frames.append(resized_frame.copy())
                    img = frames[0]
                    animated_frames = frames[1:]
                else:
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    animated_frames = None
            else:
                animated_frames = None

            # Prepare image mode and save options based on target format
            save_kwargs = {}

            if fmt == 'WEBP':
                # WebP supports RGBA in both lossy and lossless modes
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA' if 'A' in img.mode else 'RGB')
                
                save_kwargs['method'] = 6
                if lossless:
                    save_kwargs['lossless'] = True
                    save_kwargs['quality'] = 100
                else:
                    save_kwargs['lossless'] = False
                    save_kwargs['quality'] = max(1, min(100, int(quality)))

                if animated_frames:
                    save_kwargs['save_all'] = True
                    save_kwargs['append_images'] = animated_frames
                    save_kwargs['loop'] = getattr(img, "info", {}).get("loop", 0)

            elif fmt in ('JPG', 'JPEG'):
                # JPEG doesn't support alpha channel; composite over background
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    alpha_img = img.convert('RGBA')
                    bg = Image.new('RGB', alpha_img.size, bg_color)
                    bg.paste(alpha_img, mask=alpha_img.split()[3])
                    img = bg
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                save_kwargs['quality'] = max(1, min(100, int(quality)))
                save_kwargs['optimize'] = True
                save_kwargs['progressive'] = True

            elif fmt == 'PNG':
                # PNG supports RGBA, RGB, L
                if img.mode not in ('RGB', 'RGBA', 'L'):
                    img = img.convert('RGBA' if 'A' in img.mode else 'RGB')
                save_kwargs['optimize'] = True
                save_kwargs['compress_level'] = 9

            elif fmt == 'AVIF':
                # AVIF supports RGB and RGBA
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA' if 'A' in img.mode else 'RGB')
                save_kwargs['quality'] = max(1, min(100, int(quality)))

            elif fmt == 'GIF':
                if not animated_frames:
                    if img.mode != 'P':
                        img = img.convert('P', palette=Image.Palette.ADAPTIVE)
                else:
                    save_kwargs['save_all'] = True
                    save_kwargs['append_images'] = animated_frames
                    save_kwargs['loop'] = getattr(img, "info", {}).get("loop", 0)

            elif fmt == 'ICO':
                # Multi-resolution icon
                sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                # Filter sizes that are smaller or equal to current dimensions
                max_dim = max(new_w, new_h)
                sizes = [s for s in sizes if s[0] <= max_dim or s[0] == 256]
                if not sizes:
                    sizes = [(32, 32)]
                save_kwargs['sizes'] = sizes
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA')

            elif fmt == 'BMP':
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

            elif fmt == 'TIFF':
                save_kwargs['compression'] = 'tiff_deflate'

            elif fmt == 'PDF':
                if img.mode in ('RGBA', 'LA'):
                    alpha_img = img.convert('RGBA')
                    bg = Image.new('RGB', alpha_img.size, bg_color)
                    bg.paste(alpha_img, mask=alpha_img.split()[3])
                    img = bg
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                save_kwargs['resolution'] = 100.0

            # Save the file
            img.save(str(target_path), **save_kwargs)

        new_size = target_path.stat().st_size
        savings = 0.0
        if original_size > 0:
            savings = round(((original_size - new_size) / original_size) * 100.0, 1)

        return {
            'success': True,
            'input_path': str(input_p),
            'output_path': str(target_path),
            'original_size': original_size,
            'original_size_str': format_bytes(original_size),
            'new_size': new_size,
            'new_size_str': format_bytes(new_size),
            'savings_percent': savings,
            'original_dims': (orig_w, orig_h),
            'new_dims': (new_w, new_h),
            'format': fmt,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'input_path': str(input_p),
            'output_path': None,
            'error': str(e)
        }
