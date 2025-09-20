import os, pickle, h5py, numpy as np, cv2, sys, time, argparse
from typing import Union

def pack(bg_dir: str, out_h5: str, limit: Union[int, None] = None) -> None:
    imnames_cp = os.path.join(bg_dir, "imnames.cp")
    bg_img_dir = os.path.join(bg_dir, "bg_img")
    depth_h5   = os.path.join(bg_dir, "depth.h5")
    seg_h5     = os.path.join(bg_dir, "seg.h5")

    for p in (imnames_cp, depth_h5, seg_h5):
        if not os.path.exists(p):
            print(f"[ERROR] Required file not found: {p}", file=sys.stderr)
            sys.exit(1)

    with open(imnames_cp, "rb") as f:
        imnames = pickle.load(f)

    start_time = time.time()
    depth_db = h5py.File(depth_h5, "r")
    seg_db   = h5py.File(seg_h5,   "r")
    seg_mask_group = seg_db['mask'] if 'mask' in seg_db else seg_db

    missing_depth = 0
    missing_seg = 0
    written = 0

    # ensure parent directory exists
    out_parent = os.path.dirname(os.path.abspath(out_h5))
    if out_parent and not os.path.exists(out_parent):
        os.makedirs(out_parent, exist_ok=True)

    if os.path.exists(out_h5):
        os.remove(out_h5)
    out = h5py.File(out_h5, "w")
    g_img   = out.create_group("image")
    g_depth = out.create_group("depth")
    g_seg   = out.create_group("seg")
    meta = out.create_group("meta")

    total_candidates = len(imnames) if limit is None else min(len(imnames), limit)
    print(f"Packing {total_candidates} images from {bg_img_dir} -> {out_h5}")

    for i, name in enumerate(imnames):
        if limit is not None and written >= limit:
            break
        img_path = os.path.join(bg_img_dir, name)
        bgr = cv2.imread(img_path)
        if bgr is None:
            print(f"[WARN] Cannot read image file: {name}")
            continue
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        if name not in depth_db:
            missing_depth += 1
            continue
        depth_data = depth_db[name][...]

        if name not in seg_mask_group:
            missing_seg += 1
            continue
        seg_data = seg_mask_group[name][...]

        # Store in legacy-compatible structure
        g_img.create_dataset(name, data=rgb, compression="gzip")
        g_depth.create_dataset(name, data=depth_data, compression="gzip")
        seg_ds = g_seg.create_dataset(name, data=seg_data, compression="gzip")
        # Copy attributes if present (area, label)
        seg_src = seg_mask_group[name]
        for attr in ("area", "label"):
            if attr in seg_src.attrs:
                seg_ds.attrs[attr] = seg_src.attrs[attr]
        written += 1
        if written % 500 == 0:
            elapsed = time.time() - start_time
            print(f"  wrote {written} entries (elapsed {elapsed:.1f}s)...")

    # Convert strings to bytes for compatibility with older h5py
    imnames_bytes = [name.encode('utf-8') for name in imnames]
    meta.create_dataset("original_imnames", data=np.array(imnames_bytes, dtype='S'))
    meta.attrs['missing_depth'] = missing_depth
    meta.attrs['missing_seg'] = missing_seg
    meta.attrs['source_bg_dir'] = os.path.abspath(bg_dir)
    meta.attrs['total_candidates'] = len(imnames)
    meta.attrs['written'] = written
    meta.attrs['limit_applied'] = -1 if limit is None else limit

    out.close(); depth_db.close(); seg_db.close()
    elapsed = time.time() - start_time
    print(f"DONE: wrote {written} entries (skipped depth-missing={missing_depth}, seg-missing={missing_seg}) -> {out_h5} in {elapsed:.1f}s")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pack background image, depth, segmentation datasets into a single HDF5 file."
    )
    parser.add_argument('-i', '--input', required=True, help='Input background data directory (e.g. downloads/bg_data)')
    parser.add_argument('-o', '--output', required=True, help='Output HDF5 path (e.g. data/dset_big.h5)')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of images (for quick test)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    pack(args.input, args.output, args.limit)