import json
import os.path
import tkinter
from PIL import ImageTk,Image
from tkinter import filedialog

from PIL.EpsImagePlugin import EpsImageFile


# image_path = 'screenshots/android/1-2-1-v12.0.0.jpg'
# anno_path = 'pre_annotation/annotations.json'
class GUILabeller(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.canvas = None
        self.current_target_box_ids = []
        self.control = False

    def init(self, imagepath, annopath):
        self.annopath = annopath
        self.canvas = tkinter.Canvas(self)
        self.save = tkinter.Button(self, text="保存")
        self.load_unvisited_button = tkinter.Button(self, text="加载未二次标记文件",
                                                    command=lambda : self.load_unvisited())
        self.reload = tkinter.Button(self, text="选择加载")
        self.status = tkinter.StringVar()
        self.status.set("选择删除")
        self.status_label = tkinter.Label(self, textvariable=self.status)
        self.save_image = tkinter.Button(self, text="保存图像文件")

        self.canvas.pack()
        self.save.pack()
        self.load_unvisited_button.pack()
        self.reload.pack()
        self.save_image.pack()
        self.status_label.pack()
        self.load_json()
        self.load_img(imagepath)
        self.bind_all_event()
        self.control = False
        self.past_point = None
        self.flash()

    def load_unvisited(self):
        for cate in self.anno:
            for k in self.anno[cate]:
                if not self.anno[cate][k]['edited']:
                    self.load_img(k)
                    self.flash()
                    return
        tkinter.messagebox.showinfo("提示", "没有未二次标记文件")

    def flash(self):
        self.canvas.delete("all")
        self.draw_image()
        self.draw_all_bbox()

    def _release_delete(self, event):
        # print("delete: {}".format(self.current_target_box_ids))
        for k in self.current_target_box_ids:
            del self.element_anno[k]
        self.current_target_box_ids = []
        self.flash()

    def _press_Control(self, event):
        self.control = not self.control
        # print("control is {}".format(self.control))
        if self.control:
            self.status.set( "添加选框")
        else:
            self.status.set( "选择删除")

    def _reload_file(self):
        path = filedialog.askopenfilename()
        if os.path.isfile(path):
            self.load_img(path)
            self.flash()

    def _move(self, event):
        xpos = float(event.x) / self.w
        ypos = float(event.y) / self.h
        x, y = (event.x), (event.y)
        self.flash()
        self.canvas.create_line(x,0,x,self.h)
        self.canvas.create_line(0,y,self.w,y)

    def _save_image_to(self, path):
        self.update()
        self.canvas.postscript(file="test.ps",colormode="color", height = self.h, width = self.w)
        tmp = Image.open("test.ps")
        wh = [x for x in tmp._size]
        wh = [x*2 for x in wh]
        tmp._size = (wh[0],wh[1])
        tmp.save(path, "PNG", quality=100)



    def bind_all_event(self):
        self.canvas.bind("<Button-1>", lambda event: self._click(event))
        self.bind("<Delete>", lambda  event:self._release_delete(event))
        self.bind("<BackSpace>", lambda  event:self._release_delete(event))
        self.save.bind("<Button-1>" , lambda event: self.set_anno_element(event))
        self.reload.bind("<Button-1>" , lambda event: self._reload_file())
        self.canvas.bind("<Leave>", lambda event: self.flash())

        self.save_image.bind("<Button-1>" , lambda event: self._save_image_to("./test.png"))
        self.bind("<Control_L>", lambda event: self._press_Control(event))
        self.bind("<Motion>", lambda  event: self._move(event))

    def load_img(self, path):
        self.current_img_path = path
        self.image = Image.open(path)

        self.image = self.image.resize((int(self.image.width * 800.0 / self.image.height), 800))
        self.w, self.h = self.image.width, self.image.height
        path = path.replace("\\", '/')
        self.current_cate = path.split('/')[-2]
        self.current_filename = path.split('/')[-1]
        self.element_anno = self.getanno_element(self.anno, self.current_cate, self.current_filename)

    def draw_all_bbox(self):
        for k in self.element_anno:
            if not self.element_anno[k]["interactivity"]:
                continue
            bb = self.element_anno[k]["bbox"]
            self.canvas.create_rectangle(bb[0] * self.w,
                                    bb[1] * self.h,
                                    bb[2] * self.w,
                                    bb[3] * self.h, outline='green')
            self.canvas.create_rectangle(bb[0] * self.w,
                                         bb[1] * self.h,
                                         bb[0] * self.w+10,
                                         bb[1] * self.h-10, fill="green", outline="green")
            self.canvas.create_text(bb[0] * self.w+5, bb[1] * self.h-5, text=k, fill="white",font=("Purisa", 8))

        for k in self.current_target_box_ids:
            bb = self.element_anno[k]["bbox"]
            self.canvas.create_rectangle(bb[0] * self.w,
                                         bb[1] * self.h,
                                         bb[2] * self.w,
                                         bb[3] * self.h, outline='red')

    def draw_image(self):
        self.image1 = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.image1, anchor=tkinter.NW)
        self.canvas.config(width=self.w, height=self.h)

    def load_json(self, path = None):
        with open(self.annopath if path == None else path, "r") as f:
            self.anno = json.load(f)
        annotated_count = 0
        for cate in self.anno:
            for k in self.anno[cate]:
                if "edited" not in self.anno[cate][k]:
                    self.anno[cate][k]["edited"] = False
                if self.anno[cate][k]['edited']:
                    annotated_count +=1
                for idx in self.anno[cate][k]:
                    if idx == "edited":
                        continue
                    self.anno[cate][k][idx]["bbox"] = [max(0, min(1, self.anno[cate][k][idx]["bbox"][i])) for i in range(4)]
        print("from now on, {} images has been manual annotated".format(annotated_count))

    def getanno_element(self, anno, cate, filename):
        tmp = anno[cate]
        for k in tmp:
            if filename in k:
                ret = {t:tmp[k][t] for t in tmp[k] if t != "edited"}
                return ret

    def set_anno_element(self, event):
        print("anno_saved")
        tmpdict = {k:self.element_anno[k] for k in self.element_anno}
        tmpdict['edited'] = True
        tmp = self.anno[self.current_cate]
        for k in tmp:
            if self.current_filename in k:
                self.anno[self.current_cate][k] = tmpdict
        with open(self.annopath, "w") as f:
            # 格式化输出json
            json.dump(self.anno , f, indent=4)

    def get_pointed_box(self, anno_ele, xpos, ypos):
        target_keys = []
        for k in anno_ele:
            bb = anno_ele[k]["bbox"]
            if xpos >= bb[0] and xpos <= bb[2] and ypos >= bb[1] and ypos <= bb[3]:
                target_keys.append(k)
        return target_keys

    def _click(self, event):
        xpos:float = float(event.x) / self.w
        xpos = min(1, max(0, xpos))
        ypos = float(event.y) / self.h
        ypos = min(1, max(0, ypos))
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        if not self.control:
            self.past_point = None
            # event.x 鼠标左键的横坐标
            # event.y 鼠标左键的纵坐标
            boxkeys = self.get_pointed_box(self.element_anno, xpos, ypos)
            # print(boxkeys)
            self.current_target_box_ids = boxkeys
        else:
            self.current_target_box_ids = []
            if not self.past_point:
                self.past_point = [xpos, ypos]
            else:
                start = 1
                while str(start) in self.element_anno:
                    start+=1
                xmin = min(xpos, self.past_point[0])
                xmax = max(xpos, self.past_point[0])
                ymin = min(ypos, self.past_point[1])
                ymax = max(ypos, self.past_point[1])
                self.element_anno[str(start)] = {"bbox":[xmin, ymin, xmax, ymax], "content":"", "interactivity":True,
                                                 "Type": "icon"}
                self.past_point = None

        self.flash()
        self.canvas.create_oval(x1, y1, x2, y2, fill='red')
if __name__ == '__main__':

    test = GUILabeller()
    test.init('screenshots/android/1-2-1-v12.0.0.jpg','pre_annotation/annotations.json')
    test.mainloop()