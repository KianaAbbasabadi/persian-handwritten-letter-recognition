from pathlib import Path
import argparse
import hashlib
import json
import itertools
import numpy as np
import pandas as pd
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, features
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
CHARACTERS = list("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")
NAMES = ["alef", "be", "pe", "te", "se", "jim", "che", "he_jimi", "khe",
         "dal", "zal", "re", "ze", "zhe", "sin", "shin", "sad", "zad",
         "ta", "za", "eyn", "gheyn", "fe", "ghaf", "kaf", "gaf", "lam",
         "mim", "nun", "vav", "he", "ye"]
BASE_FONT_SIZE = 48
ANGLES = [-5, 0, 5]
SCALES = [0.80, 11/12, 1.0, 13/12, 1.15]
SHIFTS = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, 1), (1, -1)]

import shutil

def prepare_image(image):
    # اصلاح جهت عکس و تبدیل به خاکستری
    image = ImageOps.exif_transpose(image)
    image = image.convert('L')
    image.thumbnail((1200, 1200))

    if np.ptp(np.array(image)) < 12:
        raise ValueError('تصویر خالی است یا کنتراست کافی ندارد.')

    image = ImageOps.autocontrast(image)
    pixels = np.array(image)

    # اگر زمینه روشن باشد، رنگ‌ها را برعکس می‌کنیم
    border = np.concatenate([pixels[0], pixels[-1], pixels[:, 0], pixels[:, -1]])

    if np.median(border) > 127:
        pixels = 255 - pixels

    # محدوده همه قسمت‌های حرف، از جمله نقطه‌ها
    rows, columns = np.where(pixels > 90)

    if len(rows) < 3:
        raise ValueError('حرف مشخصی در تصویر پیدا نشد.')

    top = rows.min()
    bottom = rows.max() + 1
    left = columns.min()
    right = columns.max() + 1

    cropped = pixels[top:bottom, left:right]
    letter = Image.fromarray(cropped)
    letter.thumbnail((21, 21), Image.Resampling.LANCZOS)

    # قرار دادن حرف در مرکز تصویر
    result = Image.new('L', (32, 32), color=0)
    x = (32 - letter.width) // 2
    y = (32 - letter.height) // 2
    result.paste(letter, (x, y))

    return np.array(result) / 255.0
def render_base(path, char):
    # HarfBuzz/RAQM is required for Nastaliq dot positioning and OpenType shaping.
    if not features.check_feature('raqm'):
        raise RuntimeError('Pillow with RAQM is required. Run: pip install --upgrade Pillow')
    font = ImageFont.truetype(str(path), BASE_FONT_SIZE * 4,
                              layout_engine=ImageFont.Layout.RAQM)
    box = font.getbbox(char, direction='rtl', language='fa')
    left, top, right, bottom = box
    image = Image.new('L', (right-left+32, bottom-top+32), 0)
    ImageDraw.Draw(image).text((16-left, 16-top), char, font=font, fill=255,
                              direction='rtl', language='fa')
    if image.getbbox() is None:
        raise ValueError(f'Empty glyph: {path.name} / {char}')
    # One normalization BEFORE augmentation. Never recenter augmented samples.
    return Image.fromarray(np.uint8(np.rint(prepare_image(image) * 255)))


def augment(base, bold, angle, scale, dx, dy):
    # Supersampling permits mild synthetic bold without merging all nearby dots.
    image = base.resize((128, 128), Image.Resampling.LANCZOS)
    if bold:
        image = image.filter(ImageFilter.MaxFilter(3))
    # One affine operation: scaling/rotation around the center + translation.
    a = np.deg2rad(angle)
    c, s = np.cos(a)/scale, np.sin(a)/scale
    center = 63.5
    tx, ty = dx*4, dy*4
    matrix = (c, s, center-c*(center+tx)-s*(center+ty),
              -s, c, center+s*(center+tx)-c*(center+ty))
    image = image.transform((128, 128), Image.Transform.AFFINE, matrix,
                            resample=Image.Resampling.BICUBIC, fillcolor=0)
    return image.resize((32, 32), Image.Resampling.LANCZOS)


def generate(output=None):
    output = Path(output) if output else ROOT/'dataset_augmented'
    marker = output/'.generated_augmented_dataset'
    if output.exists():
        if not marker.is_file():
            raise ValueError('Output folder already exists and is not recognized.')
        shutil.rmtree(output)
    output.mkdir(parents=True)
    marker.write_text('Generated images only. Do not store personal files here.')
    font_paths = sorted(p for p in (ROOT/'fonts').iterdir()
                        if p.suffix.lower() in {'.ttf', '.otf'})
    if len(font_paths) < 5:
        raise ValueError('At least five different font families are required.')
    rows, records, designs = [], [], set()
    all_bases = []
    for path in font_paths:
        with TTFont(path) as font:
            cmap = font.getBestCmap() or {}
            missing = [c for c in CHARACTERS if cmap.get(ord(c), '.notdef') == '.notdef']
            if missing:
                raise ValueError(f'{path.name}: missing letters {missing}')
            record = {'font': path.stem, 'file': path.name,
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'family': font['name'].getDebugName(1),
                      'copyright': font['name'].getDebugName(0),
                      'embedded_license': font['name'].getDebugName(13)}
        bases = [render_base(path, c) for c in CHARACTERS]
        signature = hashlib.sha256(b''.join(im.tobytes() for im in bases)).hexdigest()
        if signature in designs:
            raise ValueError(f'Duplicate font design: {path.name}')
        designs.add(signature)
        records.append(record)
        all_bases.append(bases)
        for label, base in enumerate(bases):
            folder = output/'images'/path.stem/f'{label:02d}_{NAMES[label]}'
            folder.mkdir(parents=True)
            specs = [(False, 0, 1.0, 0, 0, True)]
            # 30 combinations + the untouched original = 31 samples per letter/font.
            # Translation choices cycle over combinations to keep the data manageable.
            for i, (bold, angle, scale) in enumerate(itertools.product([False, True], ANGLES, SCALES)):
                dx, dy = SHIFTS[i % len(SHIFTS)]
                specs.append((bold, angle, scale, dx, dy, False))
            for i, (bold, angle, scale, dx, dy, original) in enumerate(specs):
                image = base.copy() if original else augment(base, bold, angle, scale, dx, dy)
                file = folder/f'{i:02d}.png'
                image.save(file)
                rows.append({'path': file.relative_to(output).as_posix(), 'label': label,
                             'char': CHARACTERS[label], 'font': path.stem,
                             'source_id': f'{path.stem}:{label}', 'is_original': original,
                             'base_font_size': BASE_FONT_SIZE, 'synthetic_bold': bold,
                             'angle': angle, 'scale': scale, 'shift_x': dx, 'shift_y': dy})
        print(path.stem, 'OK', flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(output/'metadata.csv', index=False)
    classes = [{'label': i, 'char': c, 'name': NAMES[i]} for i,c in enumerate(CHARACTERS)]
    (output/'classes.json').write_text(json.dumps(classes, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {'font_count': len(font_paths), 'class_count': 32, 'image_count': len(table),
              'samples_per_font_letter': 31, 'image_size': [32,32],
              'base_font_size': BASE_FONT_SIZE, 'angles': ANGLES, 'scales': SCALES,
              'translations': SHIFTS, 'fonts': records,
              'note': 'Synthetic font data; different weights/variants are not new writers.'}
    (output/'generation_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    # Inspect every font across the same 32 classes.
    preview = Image.new('RGB', (32*44+170, len(font_paths)*64+35), 'white')
    draw = ImageDraw.Draw(preview)
    for j, (path, bases) in enumerate(zip(font_paths, all_bases)):
        draw.text((3, 40+j*64), path.stem, fill='black')
        for k, im in enumerate(bases):
            x,y=170+k*44,35+j*64
            preview.paste(im.resize((40,40)), (x,y))
            draw.text((x,y+40), str(k), fill='black')
    preview.save(output/'font_preview.png')
    # Same letter/font shown before and after augmentation.
    files = table[(table.font == font_paths[0].stem) & (table.label == 16)]
    preview = Image.new('RGB', (8*128,4*150), 'white')
    draw = ImageDraw.Draw(preview)
    for i,r in enumerate(files.itertuples()):
        x,y=(i%8)*128,(i//8)*150
        with Image.open(output/r.path) as im: preview.paste(im.resize((112,112)), (x,y))
        draw.text((x,y+113), f'b{int(r.synthetic_bold)} a{r.angle} s{r.scale:.2f}', fill='black')
        draw.text((x,y+128), f'shift ({r.shift_x},{r.shift_y})', fill='black')
    preview.save(output/'augmentation_preview.png')
    print('Images:',len(table),'Fonts:',len(font_paths),flush=True)
    return table


if __name__ == '__main__':
    import shutil
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    generate(args.output)
