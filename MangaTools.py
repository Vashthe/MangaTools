from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QLabel
from PySide6.QtUiTools import QUiLoader
from PIL import Image
import os
import re
import shutil
import fitz

# 在QApplication之前先实例化
uiLoader = QUiLoader()


class MangaTools:
    def __init__(self):
        # 再加载界面
        self.ui = uiLoader.load(r'D:\PythonProject\MangaTools\ui\rename.ui')

        self.numbers = None
        self.last_number = None
        self.last_number_end = None
        self.last_number_start = None
        self.manga_name = None

        self.input_folder  = self.ui.lineEdit_1.text()
        self.output_folder = self.ui.lineEdit_2.text()

        validator = QtGui.QIntValidator()
        self.ui.lineEdit_4.setValidator(validator)
        self.ui.lineEdit_5.setValidator(validator)

        self.init_volume = int(self.ui.lineEdit_4.text()) if self.ui.lineEdit_4.text().isdigit() else self.ui.lineEdit_4.text()
        self.last_volume = int(self.ui.lineEdit_5.text()) if self.ui.lineEdit_5.text().isdigit() else self.ui.lineEdit_5.text()

        self.ui.pushButton_1.clicked.connect(self.set_input_path)
        self.ui.pushButton_2.clicked.connect(self.set_output_path)
        self.ui.pushButton_3.clicked.connect(self.tools_applied)

        self.label = QLabel(self.ui.label_4)  # 创建新QLabel，父控件为label_4

        self.ui.lineEdit_1.textChanged.connect(self.value)
        self.ui.lineEdit_2.textChanged.connect(self.value)
        self.ui.lineEdit_3.textChanged.connect(self.value)
        self.ui.lineEdit_4.textChanged.connect(self.value)
        self.ui.lineEdit_5.textChanged.connect(self.value)

        self.ui.checkBox_3.clicked.connect(self.add_name)
        self.ui.checkBox_4.stateChanged.connect(self.text_read_only)
        self.ui.checkBox_6.clicked.connect(self.hint)

    def hint(self):
        QMessageBox.about(self.ui, "提示", "请再次选择PDF文件！")

    def value(self):
        self.input_folder  = self.ui.lineEdit_1.text()
        self.output_folder = self.ui.lineEdit_2.text()
        self.manga_name = self.ui.lineEdit_3.text()
        self.init_volume = int(self.ui.lineEdit_4.text()) if self.ui.lineEdit_4.text().isdigit() else self.ui.lineEdit_4.text()
        self.last_volume = int(self.ui.lineEdit_5.text()) if self.ui.lineEdit_5.text().isdigit() else self.ui.lineEdit_5.text()

    def set_input_path(self):
        if self.ui.checkBox_6.isChecked():
            filepath = QFileDialog.getOpenFileName(self.ui, "选择PDF文件", "", "PDF 文件 (*.pdf)")
            if filepath:
                self.ui.lineEdit_1.setText(filepath[0])
                self.input_folder = self.ui.lineEdit_1.text()
                self.load_image()  # 主动触发加载预览图片
        else:
            filepath = QFileDialog.getExistingDirectory(self.ui, "选择输入路径")
            if filepath:
                self.ui.lineEdit_1.setText(filepath)
                self.input_folder = self.ui.lineEdit_1.text()
                self.load_image()  # 主动触发加载预览图片

    def set_output_path(self):
        filepath = QFileDialog.getExistingDirectory(self.ui, "选择输出路径")
        if filepath:
            self.ui.lineEdit_2.setText(filepath)
            self.output_folder = self.ui.lineEdit_2.text()

    def tools_applied(self):
        try:
            if self.ui.checkBox_1.isChecked() or self.ui.checkBox_2.isChecked():
                if self.init_volume <= self.last_volume:
                    if self.ui.checkBox_4.isChecked():
                        if self.ui.checkBox_1.isChecked():
                            self.batch(self.picture_rename)
                        else:
                            self.batch(self.picture_cut)
                    else:
                        if self.ui.checkBox_1.isChecked():
                            self.picture_rename(self.input_folder, self.output_folder)
                        else:
                            self.picture_cut(self.input_folder, self.output_folder, 1, 2)
                else:
                    QMessageBox.critical(self.ui, "问题", "初卷数必须小于末卷数！")
            elif self.ui.checkBox_5.isChecked():
                if self.ui.checkBox_4.isChecked():
                    self.batch(self.png_to_jpg)
                else:
                    self.png_to_jpg(self.input_folder, self.output_folder)
            elif self.ui.checkBox_6.isChecked():
                if self.ui.checkBox_4.isChecked():
                    self.batch(self.pdf_to_jpg)
                else:
                    self.pdf_to_jpg(self.input_folder, self.output_folder)
        except Exception as e:
            QMessageBox.critical(self.ui, "问题", f"错误：{e}")


    def picture_rename(self, input_folder, output_folder, rows=1, cols=2):
        """
        重命名函数rename
        """
        i = 1
        # 设置后缀，筛选特定文件以更改名称
        suffix = ('jpeg', 'webp')
        files = os.listdir(input_folder)
        files.sort(key=extract_number)

        # 如果输出文件夹不存在，则创建它
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in files:
            if file.endswith(suffix):
                try:
                    # 格式化输出名字，右对齐，0填充，总长度为5
                    new_name = file.replace(file, f"{i:0>5}.jpg")
                    shutil.copy(os.path.join(input_folder, file), os.path.join(output_folder, new_name))
                    i += 1
                    print(f"处理完成：{file}")
                except Exception as e:
                    print(f"处理失败：{file}，错误：{e}")
            else:
                file_name, file_extension = os.path.splitext(os.path.join(input_folder, file))
                try:
                    new_name = file.replace(file, f"{i:0>5}{file_extension}")
                    shutil.copy(os.path.join(input_folder, file), os.path.join(output_folder, new_name))
                    i += 1
                    print(f"处理完成：{file}")
                except Exception as e:
                    print(f"处理失败：{file}，错误：{e}")
        print("End")
        QMessageBox.about(self.ui, "结果", "重命名完成！")



    def picture_cut(self, input_folder, output_folder, rows, cols):
        """
        批量将文件夹中的所有图片等分成指定行数和列数的小块，并按顺序保存到输出文件夹。

        参数:
        - input_folder: 输入文件夹路径（字符串）
        - output_folder: 输出文件夹路径（字符串）
        - rows: 行数（整数）
        - cols: 列数（整数）
        """
        # 如果输出文件夹不存在，则创建它
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 获取输入文件夹中的所有图片文件
        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.bmp', '.gif', 'webp'))]

        # 按文件名排序（可选）
        image_files.sort()

        # 遍历所有图片文件并等分
        for num, filename in enumerate(image_files):
            try:
                # 构建输入图片路径
                image_path = os.path.join(input_folder, filename)

                # 调用 split_image 函数处理当前图片
                start_index = 2 * num + 1
                split_image(image_path, output_folder, rows, cols, start_index)
                print(f"处理完成：{filename}")
            except Exception as e:
                print(f"处理失败：{filename}，错误：{e}")
                QMessageBox.critical(self.ui, "问题", f"错误：{e}")
        QMessageBox.about(self.ui, "结果", "剪裁完成！")

    def png_to_jpg(self, input_folder, output_folder, rows=1, cols=2):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 获取输入文件夹中的所有图片文件
        png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]

        # 按文件名排序（可选）
        png_files.sort()

        for num, filename in enumerate(png_files):
            try:
                # 构建输入图片路径
                png_path = os.path.join(input_folder, filename)
                with Image.open(png_path) as png:
                    if png.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', png.size, (255, 255, 255))  # 白色背景
                        background.paste(png, mask=png.split()[-1])  # 合并透明层
                        jpg_image = background
                    else:
                        jpg_image = png.convert('RGB')
                    jpg_image.save(os.path.join(output_folder, f"{num+1:0>5}.jpg") , "JPEG", quality=95)
                    print(f"处理完成：{filename}")
            except Exception as e:
                print(f"PDF处理失败：{filename}，错误：{e}")
        QMessageBox.about(self.ui, "结果", "PNG转JPG完成！")

    def pdf_to_jpg(self, file_path, output_folder, rows=1, cols=2):
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            pdf_document = fitz.open(file_path)

            # 遍历 PDF 的每一页
            for page_number in range(len(pdf_document)):
                page = pdf_document.load_page(page_number)
                # 将页面渲染为图像
                pix = page.get_pixmap()
                # 生成输出的 JPG 文件路径
                output_path = f"{output_folder}/{page_number + 1:0>5}.jpg"
                # 保存图像为 JPG 格式
                pix.save(output_path)
                print(f"Page {page_number + 1:0>5} converted to {output_path}")

            # 关闭 PDF 文件
            QMessageBox.about(self.ui, "结果", f"{os.path.basename(file_path)}转JPG完成！")
            pdf_document.close()

        except Exception as e:
            QMessageBox.critical(self.ui, "问题", f"错误：{e}")

    def batch(self,func):
        """使工具批量化的方法"""
        for n in range(self.init_volume, self.last_volume + 1):
            self.replace_last_number(self.input_folder)
            self.input_folder = self.input_folder[:self.last_number_start] + f"{n:0>{len(self.numbers)}}" + self.input_folder[self.last_number_end:]
            self.replace_last_number(self.output_folder)
            self.output_folder = self.output_folder[:self.last_number_start] + f"{n:0>{len(self.numbers)}}" + self.output_folder[self.last_number_end:]
            func(self.input_folder, self.output_folder, rows=1, cols=2 )

    def load_image(self):
        """动态加载图片的核心方法"""
        if not self.input_folder:
            self.label.clear()  # 清空图片
            return
        try:
            if self.ui.checkBox_6.isChecked():  # 显示PDF封面
                try:
                    # 1. 打开 PDF 并加载第一页（高 DPI）
                    pdf_document = fitz.open(self.input_folder)
                    cover = pdf_document.load_page(0)
                    pix = cover.get_pixmap(dpi=300)  # 关键：提高 DPI

                    # 2. 转换为 QPixmap（确保 RGB 格式）
                    qimage = QtGui.QImage(
                        pix.samples,
                        pix.width,
                        pix.height,
                        pix.stride,
                        QtGui.QImage.Format_RGB888
                    )
                    pixmap = QtGui.QPixmap.fromImage(qimage)

                    # 3. 缩放（可选，尽量保持原始大小）
                    if pixmap.width() > 280:  # 如果图片较宽，才缩放
                        pixmap = pixmap.scaledToWidth(
                            310,
                            QtCore.Qt.TransformationMode.SmoothTransformation
                        )

                    # 4. 显示到 QLabel
                    self.label.setPixmap(pixmap)
                    self.label.resize(pixmap.size())  # 调整 QLabel 大小
                    pdf_document.close()

                except Exception as e:
                    print(f"加载失败: {e}")
                    QMessageBox.critical(self.ui, "问题", f"PDF封面加载失败:\n{str(e)}")
            else:
                try:
                    image_files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif','webp'))]
                    image_files.sort()
                    if not image_files:
                        raise FileNotFoundError("无有效图片文件")

                    first_image_path = os.path.join(self.input_folder, image_files[0])
                    if image_files[0].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif','webp')):
                        # 使用 with 语句确保文件资源释放
                        with Image.open(first_image_path) as img:
                            img.save("temp_preview.jpg")  # 临时保存为文件
                            # 1. 从文件路径创建QPixmap对象
                            pixmap = QtGui.QPixmap("temp_preview.jpg")
                            os.remove("temp_preview.jpg")  # 删除临时文件
                        # 2. 按宽度等比例缩放（高度自动计算）
                        pixmap = pixmap.scaledToWidth(
                            310,  # 目标宽度（像素）
                            QtCore.Qt.SmoothTransformation  # 平滑缩放模式
                        )

                        # 1. 在QLabel上设置图片
                        self.label.setPixmap(pixmap)

                        # 2. 调整QLabel尺寸匹配图片大小
                        self.label.resize(pixmap.width(), pixmap.height())
                except Exception as e:
                    QMessageBox.critical(self.ui, "问题", f"图片封面加载失败:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self.ui, "错误", f"封面加载失败:\n{str(e)}")

    def add_name(self):
        try:
            if self.ui.checkBox_3.isChecked():
                if self.ui.lineEdit_3.text():
                    if self.ui.lineEdit_2.text():
                            if self.ui.checkBox_4.isChecked():
                                    new_path = str(self.ui.lineEdit_2.text()) + "/" + self.manga_name + f"Vol.{self.ui.lineEdit_4.text():0>2}"
                            else:
                                    new_path = str(self.ui.lineEdit_2.text()) + "/" + self.manga_name
                            self.ui.lineEdit_2.setText(new_path)
                    else:
                        QMessageBox.critical(self.ui, "错误", "输出路径未添加")
                else:
                    QMessageBox.critical(self.ui, "错误", "作品名未添加")
        except Exception as e:
            QMessageBox.critical(self.ui, "问题", f"错误：{e}")

    def text_read_only(self):
        if self.ui.checkBox_4.isChecked():
            self.ui.lineEdit_4.setReadOnly(False)
            self.ui.lineEdit_5.setReadOnly(False)
        else:
            self.ui.lineEdit_4.setReadOnly(True)
            self.ui.lineEdit_5.setReadOnly(True)

    def replace_last_number(self, input_string):
        filename = os.path.basename(input_string)
        # 使用正则表达式找到所有的数字组
        self.numbers = re.findall(r'\d', filename)

        if not self.numbers:
            QMessageBox.about(self.ui, "提示", "路径中没有数字")

        # 找到最后一组数字的起始和结束位置
        if   len(self.numbers) == 2:
            self.last_number = self.numbers[-2]
            self.last_number_start = input_string.rfind(self.last_number)
            self.last_number_end = self.last_number_start + len(self.numbers)
        elif len(self.numbers) == 1:
            self.last_number = self.numbers[-1]
            self.last_number_start = input_string.rfind(self.last_number)
            self.last_number_end = self.last_number_start + len(self.numbers)



def extract_number(file_name):
    # +意味着会匹配连续的数字
    match = re.findall(r'\d+', file_name)
    return int(match[-1]) if match else float('inf')

def split_image(image_path, output_folder, rows, cols, start_index):
    """
        将单张图片等分成指定行数和列数的小块，并按顺序保存到输出文件夹。

        参数:
        - image_path: 输入图片路径（字符串）
        - output_folder: 输出文件夹路径（字符串）
        - rows: 行数（整数）
        - cols: 列数（整数）
        - start_index: 起始序号（整数）

        返回:
        - 下一个文件的起始序号
    """
    # 打开图片
    with Image.open(image_path) as img:
        width, height = img.size

        # 计算每个小块的宽度和高度
        tile_width = width // cols
        tile_height = height // rows
        if start_index == 1:
            """
            第一张图片序号不变
            设置为00001
            """
            img_filename = f"{start_index:0>5}.jpg"
            img_path = os.path.join(output_folder, img_filename)
            img.save(img_path)
            print(f"保存成功：{img_path}")
            start_index += 1
        else:
            for i in range(rows):
                for j in range(cols):
                    # 计算当前小块的左上角和右下角坐标
                    left  = j * tile_width
                    upper = i * tile_height
                    right = left + tile_width
                    lower = upper + tile_height

                    # 裁剪出当前小块
                    tile = img.crop((left, upper, right, lower))

                    # 生成输出文件名
                    output_filename = f"{start_index:0>5}.jpg"
                    output_path = os.path.join(output_folder, output_filename)

                    # 更新序号
                    start_index -= 1

                    # 保存裁剪后的小块
                    tile.save(output_path)
                    print(f"保存成功：{output_path}")
        return start_index




app = QApplication([])
manga_tools = MangaTools()
manga_tools.ui.show()
app.exec()
