# -*- coding: utf-8 -*-
"""
CLI detect face trong 1 file/folder, xuất CSV: filename, top, right, bottom, left
"""

import click
import os
import multiprocessing
from models import load_image_file, face_locations

# ===============================
# Hàm tiện ích in CSV
# ===============================
def print_result(filename, bbox):
    left, top, right, bottom = map(int, bbox)
    print(f"{filename},{top},{right},{bottom},{left}")

# ===============================
# Detect 1 ảnh
# ===============================
def test_image(image_path):
    img = load_image_file(image_path)
    bboxes = face_locations(img)
    if not bboxes:
        print(f"{image_path},no_person_found,0,0,0,0")
    for bbox in bboxes:
        print_result(image_path, bbox)

# ===============================
# Lấy danh sách ảnh trong folder
# ===============================
def image_files_in_folder(folder):
    exts = (".jpg", ".jpeg", ".png")
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]

# ===============================
# Xử lý multi-core
# ===============================
def process_images_in_process_pool(images, cpus):
    if cpus == -1:
        processes = None
    else:
        processes = cpus

    context = multiprocessing
    if "forkserver" in multiprocessing.get_all_start_methods():
        context = multiprocessing.get_context("forkserver")

    pool = context.Pool(processes=processes)
    pool.map(test_image, images)

# ===============================
# CLI
# ===============================
@click.command()
@click.argument('image_to_check')  # file hoặc folder
@click.option('--cpus', default=1, help='Number of CPU cores (-1 = all)')
def main(image_to_check, cpus):
    if os.path.isdir(image_to_check):
        files = image_files_in_folder(image_to_check)
        if cpus == 1:
            for f in files:
                test_image(f)
        else:
            process_images_in_process_pool(files, cpus)
    else:
        test_image(image_to_check)

if __name__ == "__main__":
    main()