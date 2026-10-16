"""Read a YOLO dataset ZIP, check labels and draw examples without training.

Run: python inspect_dataset.py dataset.zip --output reports
Only Pillow is required: python -m pip install Pillow
The original ZIP is never modified or extracted.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
from statistics import median
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageOps

NAMES = ['Bacteria_Leaf_Blight', 'Brown_Spot', 'Leaf_smut']
COLORS = ['#ef4444', '#22c55e', '#3b82f6']


def run(archive, output):
    output.mkdir(parents=True, exist_ok=True)
    counts, sizes = {}, Counter()
    errors, edge_boxes, ambiguous = [], [], []
    hashes, source_groups = defaultdict(list), defaultdict(list)
    areas = defaultdict(list)
    candidates = defaultdict(list)
    with ZipFile(archive) as z:
        files = [n for n in z.namelist() if not n.endswith('/')]
        assert len(files) == len(set(files)), 'Archive contains duplicate member paths'
        image_files = sorted(n for n in files if n.startswith('images/') and n.lower().endswith(('.jpg', '.jpeg', '.png')))
        labels = [n for n in files if n.startswith('labels/') and n.endswith('.txt')]
        by_stem = defaultdict(list)
        for n in labels:
            by_stem[PurePosixPath(n).stem].append(n)
        used_labels = set()
        for split in ['train', 'val', 'test']:
            counts[split] = {'images': 0, 'boxes': 0, 'empty_labels': 0,
                             'class_boxes': {name: 0 for name in NAMES},
                             'missing_standard_path': 0, 'missing_label': 0}
        for number, n in enumerate(image_files):
            split = n.split('/')[1]
            if split not in counts:
                errors.append({'image': n, 'problem': 'unexpected split'})
                continue
            c = counts[split]
            c['images'] += 1
            expected = str(PurePosixPath(n).with_suffix('.txt')).replace('images/', 'labels/', 1)
            if expected not in files:
                c['missing_standard_path'] += 1
            matches = by_stem[PurePosixPath(n).stem]
            if len(matches) != 1:
                c['missing_label'] += 1
                errors.append({'image': n, 'problem': 'missing or ambiguous label', 'matches': matches})
                continue
            label = matches[0]
            used_labels.add(label)
            text = z.read(label).decode('utf-8-sig').strip()
            if not text:
                c['empty_labels'] += 1
            boxes = []
            for line_no, line in enumerate(text.splitlines(), 1):
                try:
                    values = line.split()
                    if len(values) != 5:
                        raise ValueError('expected five values per box')
                    cls = int(values[0])
                    x, y, w, h = map(float, values[1:])
                    if cls not in range(len(NAMES)):
                        raise ValueError('class ID outside 0..2')
                    if not all(math.isfinite(v) for v in (x, y, w, h)):
                        raise ValueError('non-finite coordinate')
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                        raise ValueError('normalised xywh outside allowed range')
                    if min(x-w/2, y-h/2) < -0.001 or max(x+w/2, y+h/2) > 1.001:
                        edge_boxes.append({'label': label, 'line': line_no})
                    boxes.append((cls, x, y, w, h))
                    areas[NAMES[cls]].append(w*h)
                    c['class_boxes'][NAMES[cls]] += 1
                    c['boxes'] += 1
                except ValueError as exc:
                    errors.append({'label': label, 'line': line_no, 'problem': str(exc)})
            raw = z.read(n)
            try:
                with Image.open(io.BytesIO(raw)) as opened:
                    opened.load()
                    picture = opened.convert('RGB')
                    sizes[str(picture.size)] += 1
                    digest = hashlib.sha256(str(picture.size).encode()+picture.tobytes()).hexdigest()
                    hashes[digest].append(n)
            except Exception as exc:
                errors.append({'image': n, 'problem': str(exc)})
                continue
            # A shared name before Roboflow's .rf. suffix is a clue, not proof,
            # that multiple exports came from the same source photograph.
            group = re.split(r'\.rf\.', PurePosixPath(n).stem)[0]
            source_groups[group].append(n)
            for cls in set(b[0] for b in boxes):
                if len(candidates[cls]) < 3:
                    candidates[cls].append((n, label, boxes))
            if number % 1000 == 0:
                print(f'Checked {number}/{len(image_files)} images', flush=True)

        tiles = []
        for cls in range(3):
            for n, label, boxes in candidates[cls]:
                with Image.open(io.BytesIO(z.read(n))) as opened:
                    pic = opened.convert('RGB')
                width, height = pic.size
                draw = ImageDraw.Draw(pic)
                for cid, x, y, w, h in boxes:
                    draw.rectangle(((x-w/2)*width, (y-h/2)*height,
                                    (x+w/2)*width, (y+h/2)*height),
                                   outline=COLORS[cid], width=3)
                    draw.text((max(0,(x-w/2)*width),max(0,(y-h/2)*height-13)),
                              NAMES[cid], fill=COLORS[cid])
                pic = ImageOps.contain(pic, (420, 330))
                tile = Image.new('RGB', (440, 390), 'white')
                tile.paste(pic, ((440-pic.width)//2, 15))
                td = ImageDraw.Draw(tile)
                td.text((10,350), NAMES[cls], fill='black')
                td.text((10,367), PurePosixPath(n).name[:57], fill='black')
                tiles.append(tile)
        sheet = Image.new('RGB', (1320, 390*((len(tiles)+2)//3)), '#e5e7eb')
        for i, tile in enumerate(tiles):
            sheet.paste(tile, ((i%3)*440,(i//3)*390))
        sheet.save(output/'sample_boxes.jpg', quality=92)
        overlaps = [v for v in hashes.values() if len({n.split('/')[1] for n in v}) > 1]
        name_overlaps = {k:v for k,v in source_groups.items() if len({n.split('/')[1] for n in v}) > 1}
        report = {
            'archive_filename': archive.name,
            'class_mapping_from_archive_yaml': NAMES,
            'raw_yaml': z.read('data.yaml').decode(),
            'splits': counts,
            'images_total':len(image_files), 'labels_total':len(labels),
            'orphan_labels': sorted(set(labels)-used_labels),
            'image_sizes': dict(sizes), 'errors':errors,
            'boxes_crossing_image_edge_count':len(edge_boxes),
            'boxes_crossing_image_edge_examples':edge_boxes[:10],
            'exact_pixel_duplicate_groups':sum(len(v)>1 for v in hashes.values()),
            'exact_pixel_cross_split_groups':len(overlaps),
            'exact_pixel_cross_split_examples':overlaps[:10],
            'filename_source_cross_split_groups':len(name_overlaps),
            'filename_source_cross_split_examples':dict(list(name_overlaps.items())[:10]),
            'box_area_fraction':{k:{'min':min(v),'median':median(v),'max':max(v)} for k,v in areas.items()},
            'notes':[
                'Class names are copied from supplied YAML, not biologically verified.',
                'Filename groups are clues about related images, not confirmed source identities.',
                'This checks exact pixel duplicates; visually similar images need further review.',
                'Previews are inspection examples, not an independent evaluation set.',
                'No training or source modification was performed.'
            ]
        }
        (output/'dataset_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps({k:report[k] for k in ['images_total','labels_total','splits','exact_pixel_cross_split_groups','filename_source_cross_split_groups']},indent=2))
        print('Errors:',len(errors),'orphan labels:',len(report['orphan_labels']))
        print('Preview:',output/'sample_boxes.jpg')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('--output',type=Path,default=Path('reports'))
    args = parser.parse_args()
    run(args.archive,args.output)
