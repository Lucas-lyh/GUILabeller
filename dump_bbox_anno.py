import os.path

from tool import parse_img_paths_by_path
from main import GUILabeller
anno_dir = "./pre_annotation"
img_dict = parse_img_paths_by_path("./screenshots")
for cate in img_dict:
    catedir = os.path.join(anno_dir, cate)
    if not os.path.exists(catedir):
        os.mkdir(catedir)
    for img in img_dict[cate]:
        Labeller = GUILabeller()
        Labeller.init(img, os.path.join(anno_dir, "annotations.json"))
        Labeller._save_image_to(os.path.join(catedir, img.split("\\")[-1]))
        Labeller.destroy()
        del Labeller