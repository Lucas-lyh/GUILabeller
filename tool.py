import os
def parse_img_paths_by_path(path):
    images_path = {} # category-> [image_paths]
    for root, dirs, files in os.walk(path):
        if "annotation" in root:
            continue
        for file in files:
            if not (file.lower().endswith('.png') or file.lower().endswith('.jpg')):
                continue
            cate = root.split('/')[-1].split("\\")[-1]
            if cate not in images_path:
                images_path[cate] = []
            images_path[cate].append(os.path.join(root, file))
    return images_path
