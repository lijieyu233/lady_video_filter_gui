import sys
import os
import shutil
import traceback

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider,
    QLabel, QFileDialog, QLineEdit, QMessageBox, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt, QTime, QTimer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from utils import config
from utils.client2 import ClientUtils
import logging

from utils.temp_utils import transform_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoPlayer(QWidget):
    def __init__(self):
        # todo 控件定义
        # 设置页面布局
        super().__init__()
        self.setWindowTitle("美女号筛选器") # 设置窗口标题
        self.resize(1200, 800)  #   设置窗口大小


        # 左侧文件目录部分
        ## 1.控制按钮
        self.openButton = QPushButton('选择文件夹')
        self.openButton.clicked.connect(self.open_folder)
        ## 2.文件夹树
        self.fileTreeWidget = QTreeWidget()
        self.fileTreeWidget.setHeaderLabel("文件夹")
        self.fileTreeWidget.setMinimumWidth(200)
        self.fileTreeWidget.itemClicked.connect(self.on_file_clicked)

        # 右侧部分
        ## 1.播放器
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  # 创建一个QMediaPlayer对象，并指定它播放视频
        self.videoWidget = QVideoWidget()  # 创建一个QVideoWidget对象，用于显示视频
        self.mediaPlayer.setVideoOutput(self.videoWidget)  # 将视频播放器的输出设置为视频显示窗口
        ## 2.进度条
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.set_position)
        self.mediaPlayer.positionChanged.connect(self.position_changed)  # 设置进度条到当前播放位置
        self.mediaPlayer.durationChanged.connect(self.duration_changed)  # 设置总时长

        # 3.时间显示
        self.timeLabel = QLabel("00:00 / 00:00")
        ## 4. 按钮
        self.dont_carry_button = QPushButton('不搬运')
        self.dont_carry_button.clicked.connect(self.not_carry_video)
        self.carry_button = QPushButton('搬运')
        self.carry_button.clicked.connect(self.carry_video)
        # self.carry_no_voice_button = QPushButton('搬运:不带声音')
        # self.carry_no_voice_button.clicked.connect(self.carry_video_without_voice)
        # self.carry_has_voice_male_button = QPushButton('搬运:带声音_男')
        # self.carry_has_voice_male_button.clicked.connect(self.carry_video_with_voice_male)
        # self.carry_has_voice_female_button = QPushButton('搬运:带声音_女')
        # self.carry_has_voice_female_button.clicked.connect(self.carry_video_with_voice_female)


        #todo  布局
        ## 1.左侧布局 文件夹按钮和文件夹目录
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.openButton) # 左侧边框增加选择文件夹按钮
        leftLayout.addWidget(self.fileTreeWidget) # 左侧边框增加文件目录

        ## 2.右侧布局（视频播放器和控件）
        rightLayout = QVBoxLayout()
        ### 2.1 播放器 进度条 时间现显示
        rightLayout.addWidget(self.videoWidget, 5) # 右侧边框增加视频播放器
        rightLayout.addWidget(self.positionSlider) # 右侧边框增加进度条
        rightLayout.addWidget(self.timeLabel) # 右侧边框增加时间显示

        ### 2.2 控制按钮布局
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.dont_carry_button)
        controlLayout.addWidget(self.carry_button)
        # controlLayout.addWidget(self.carry_has_voice_male_button)
        # controlLayout.addWidget(self.carry_has_voice_female_button)
        rightLayout.addLayout(controlLayout) # 右侧边框增加控制按钮布局
        ##  主体布局
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout, 1)
        mainLayout.addLayout(rightLayout, 3)

        ## 应用布局
        self.setLayout(mainLayout)

        # 定时器更新时间显示
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 属性
        self.current_click_video_path = None # 当前点击的视频文件路径
        self.current_item = None # 当前点击的QTreeWidgetItem对象

        # 2.水印标记
        self.is_carry = None
        # self.has_voice = None
        # self.has_watermark = None




        # 启动时自动打开默认文件夹
        if os.path.exists(config.default_open_folder):
            self.open_folder_auto()  # 新增一个方法避免弹出对话框
        else:
            self.open_folder()  # 如果默认路径不存在，则弹出对话框

    # 文件夹方法
    ## 1.打开文件资源管理器 选择文件夹
    def open_folder(self):
        default_path = config.default_open_folder
        os.makedirs(default_path, exist_ok=True)
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", default_path)
        if folder:
            self.fileTreeWidget.clear()
            # self.video_list.clear()
            folder_item = QTreeWidgetItem(self.fileTreeWidget)
            folder_item.setText(0, os.path.basename(folder)) # 设置显示文本 即文件名
            folder_item.setData(0, Qt.UserRole, folder)      # 设置用户自定义数据 全路径
            self.fileTreeWidget.addTopLevelItem(folder_item)
            folder_item.setExpanded(True)
            self.build_file_tree(folder_item, folder)
        # 点击文件列表中的视频

    ## 2.点击文件列表中的视频 播放
    def on_file_clicked(self, item):
        try:
            file_path = item.data(0, Qt.UserRole).replace('\\', '/')
            self.current_click_video_path = file_path
            self.current_item = item
            if file_path and file_path.endswith('.mp4'):
                self.play_video()
        except Exception as e:
            traceback.print_exc()  # 直接输出到控制台
            # 或者获取错误栈字符串
            error_msg = traceback.format_exc()
            QMessageBox.critical(self, "错误", str(e.__traceback__))

    ## 3 新增方法：自动打开默认文件夹（不弹出对话框）
    def open_folder_auto(self):
        folder = config.default_open_folder
        if folder:
            self.fileTreeWidget.clear()
            # self.video_list.clear()
            folder_item = QTreeWidgetItem(self.fileTreeWidget)
            folder_item.setText(0, os.path.basename(folder))
            folder_item.setData(0, Qt.UserRole, folder)
            self.fileTreeWidget.addTopLevelItem(folder_item)
            folder_item.setExpanded(True)
            self.build_file_tree(folder_item, folder)

    ## 4 构建文件夹和子文件夹中的.mp4文件树
    def build_file_tree(self, parent_item, folder):
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isdir(path):
                dir_item = QTreeWidgetItem(parent_item)
                dir_item.setText(0, name)
                dir_item.setData(0, Qt.UserRole, path)
                self.build_file_tree(dir_item, path)
            elif name.endswith('.mp4'):
                file_item = QTreeWidgetItem(parent_item)
                file_item.setText(0, name)
                file_item.setData(0, Qt.UserRole, path)

    ## 5. 播放视频
    def play_video(self):
        # if 0 <= self.current_index < len(self.video_list):
        #     video_path = self.video_list[self.current_index]
        video_path = self.current_click_video_path
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.mediaPlayer.play()
        self.has_watermark = None
        # else:
        #     QMessageBox.information(self, "提示", "没有可播放的视频。")









    # todo 进度条
    ## 1.更新进度条
    def position_changed(self, position):
        self.positionSlider.setValue(position)
    ## 2.更新进度条长度
    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)

    # 3.更新时间显示
    def update_time(self):
        position = self.mediaPlayer.position()
        duration = self.mediaPlayer.duration()
        total_time = QTime(0, 0, 0).addMSecs(duration).toString("mm:ss") if duration > 0 else "00:00"
        current_time = QTime(0, 0, 0).addMSecs(position).toString("mm:ss")
        self.timeLabel.setText(f"{current_time} / {total_time}")

    # 4.设置进度条位置
    def set_position(self, position):
        self.mediaPlayer.setPosition(position)


    # todo 按钮
    ## 1.不搬运
    def not_carry_video(self):
        try:
            print("点击不搬运")
            self.is_carry = False

            self.move_video()
        except Exception as e:
            traceback.print_exc()  # 直接输出到控制台
            # 或者获取错误栈字符串
            error_msg = traceback.format_exc()
            QMessageBox.critical(self, "错误", str(e.__traceback__))
    def carry_video(self):
        try:
            print("点击搬运")
            self.is_carry = True

            self.move_video()
        except Exception as e:
            traceback.print_exc()  # 直接输出到控制台
            # 或者获取错误栈字符串
            error_msg = traceback.format_exc()
            QMessageBox.critical(self, "错误", str(e.__traceback__))

    # ## 2.搬运 不带声音
    # def carry_video_without_voice(self):
    #     self.is_carry = True
    #     self.has_voice = False
    #     self.move_video()
    # ## 3.搬运 带声音
    # def carry_video_with_voice_male(self):
    #     self.is_carry = True
    #     self.has_voice = 1
    #     self.move_video()
    # def carry_video_with_voice_female(self):
    #     self.is_carry = True
    #     self.has_voice = 2
    #     self.move_video()
    ## 4.移动视频
    def move_video(self):
        """
        移动视频
        重新构建文件树
        播放邻近视频
        :return:
        """
        try:
            #1. 移动前置处理
            self.mediaPlayer.stop()
            self.mediaPlayer.setMedia(QMediaContent())
            video_path = self.current_click_video_path
            if os.path.isdir(video_path):
                self.current_click_video_path = None
                self.current_item = None
                QMessageBox.information(self, "提示", f"{video_path}是目录而不是视频文件,请重新选择。")
                return
            if self.current_click_video_path is None:
                QMessageBox.information(self, "提示", f"未选择视频。")
                return
            current_item = self.current_item
            #todo 获取邻近节点
            adjacent=self.get_adjacent_item(current_item)
            # next_item = self.find_next_video_item(current_item)
            # prev_item = self.find_previous_video_item(current_item)


            # 2 移动位置
            if not self.is_carry:
                save_dir = "不搬运"
            elif self.is_carry:
                save_dir = "搬运"
            else:
                raise ValueError("Invalid value for self.has_watermark.")
            target_path = transform_path(video_path, save_dir)
            # target_path = os.path.join(save_dir, os.path.basename(video_path)).replace('\\', '/')
            # logger.info(f"移动视频{video_path}到 {target_path}")
            os.makedirs(os.path.dirname(target_path), exist_ok=True)


            # 3 移动并入库
            try:
                shutil.move(video_path, target_path)
                logging.info(f"视频{video_path}已移动到 {target_path} 文件夹。")
                # QMessageBox.information(self, "提示", f"视频已移动到 {save_dir} 文件夹。")

                # 更新数据库（在文件移动成功后立即进行）
                # video_name = os.path.basename(video_path)  # 使用带有扩展名的完整文件名
                try:
                    rows_affected = 0
                    # if not self.is_carry:
                    #     # 更新数据库，标记为有水印
                    #     rows_affected=ClientUtils.not_carry(video_path= video_path,target_path=target_path)
                    # elif self.is_carry and self.has_voice:
                    #     rows_affected=ClientUtils.carry_with_voice(video_path= video_path,target_path=target_path)
                    # elif self.is_carry and not self.has_voice:
                    #     rows_affected=ClientUtils.carry_without_voice(video_path= video_path,target_path=target_path)
                    #         # rows_affected = cursor.rowcount
                    body={
                        "is_carry": self.is_carry,
                        # "has_voice": self.has_voice,
                        "video_path": target_path
                    }
                    params={
                        "video_path": video_path
                    }
                    rows_affected = ClientUtils.dynamic_update_lady_material(body=body, params=params)
                    if rows_affected == 0:
                        QMessageBox.critical(self, "提示", f"未更新数据库,请查看视频{target_path}是否在数据库中")
                            #
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"数据库更新失败：{str(e)}")
                    logger.error(f"数据库更新失败：{str(e)}")

                #4 更新文件列表-删除-添加
                self.update_file_tree_after_move(video_path, target_path)

                # 5.移动到邻近视频
                if adjacent:
                    self.current_click_video_path = adjacent.data(0, Qt.UserRole).replace('\\', '/')
                    self.current_item = adjacent
                    self.play_video()
                else:
                    self.current_click_video_path = None
                    self.current_item = None
                    # QMessageBox.information(self, "提示", "没有更多视频了。")
                # if next_item is not None:
                #     self.current_click_video_path = next_item.data(0, Qt.UserRole).replace('\\', '/')
                #     self.current_item = next_item
                #     self.play_video()
                # else:
                #     if prev_item is not None:
                #         self.current_click_video_path = prev_item.data(0, Qt.UserRole).replace('\\', '/')
                #         self.current_item = prev_item
                #         self.play_video()
                #     else:
                #         QMessageBox.information(self, "提示", "没有更多视频了。")
                #         self.current_click_video_path = None
                #         self.current_item = None

            except PermissionError as e:
                QMessageBox.critical(self, "错误", f"无法移动视频文件：{str(e)}")
        except Exception as e:
            traceback.print_exc()  # 直接输出到控制台
            # 或者获取错误栈字符串
            error_msg = traceback.format_exc()
            QMessageBox.critical(self, "错误", str(e.__traceback__))





















    # 更新文件树
    def update_file_tree_after_move(self, old_path, new_path):
        """
        删除移动的节点,怎加移动后的节点 更新文件树
        :param old_path:
        :param new_path:
        :return:
        """
        try:
            def find_and_remove_item(item, path): # 递归删除节点
                for i in range(item.childCount()):
                    child = item.child(i)
                    # logger.info(f"child.data(0, Qt.UserRole) == {child.data(0, Qt.UserRole)}")
                    if child.data(0, Qt.UserRole).replace("\\","/") == path:
                        item.removeChild(child)
                        break
                    else:
                        find_and_remove_item(child, path)
            def find_and_add_to_item(item, folder_path, new_file_path): # 递归添加节点
                """

                :param item: 根节点 父节点
                :param folder_path:  被添加节点目录
                :param new_file_path: 被添加节点全路径
                 :return:
                """
                # 1. 先检查当前节点的直接子节点 找到对应目录 添加节点
                for i in range(item.childCount()):
                    child = item.child(i)
                    if child.data(0, Qt.UserRole).replace('\\','/') == folder_path:
                        file_item = QTreeWidgetItem(child)
                        file_item.setText(0, os.path.basename(new_file_path))
                        file_item.setData(0, Qt.UserRole, new_file_path)
                        return
                # 2.当前节点未找到 递归继续查找
                for i in range(item.childCount()):
                    child = item.child(i)
                    find_and_add_to_item(child, folder_path, new_file_path)
            root_item = self.fileTreeWidget.topLevelItem(0) # 获取根节点\
            find_and_remove_item(root_item, old_path) # 从根节点开始查找并删除
            find_and_add_to_item(root_item, os.path.dirname(new_path), new_path) # 在新路径对应的文件夹下添加新文件
        except Exception as e:
            traceback.print_exc() # 直接输出到控制台
            # 或者获取错误栈字符串
            error_msg = traceback.format_exc()
            QMessageBox.critical(self, "错误", str(e.__traceback__))

    def get_adjacent_item(self,item) :
        """
        获取给定节点的邻近节点：
        1. 优先尝试获取下一个兄弟节点
        2. 如果没有下一个兄弟，尝试获取上一个兄弟节点
        3. 如果都没有，返回None

        参数:
            item: 当前树节点

        返回:
            邻近节点或None
        """
        # 获取当前节点的父节点（用于访问兄弟节点）
        parent = item.parent()

        if parent:
            # 当前节点在父节点中的索引位置
            index = parent.indexOfChild(item)

            # 尝试获取下一个兄弟节点
            if index < parent.childCount() - 1:
                return parent.child(index + 1)

            # 尝试获取上一个兄弟节点
            elif index > 0:
                return parent.child(index - 1)

        else:  # 处理顶层节点
            tree_widget = item.treeWidget()
            index = tree_widget.indexOfTopLevelItem(item)

            # 尝试获取下一个顶层节点
            if index < tree_widget.topLevelItemCount() - 1:
                return tree_widget.topLevelItem(index + 1)

            # 尝试获取上一个顶层节点
            elif index > 0:
                return tree_widget.topLevelItem(index - 1)

        # 没有邻近节点
        return None














    # 打开文件夹并递归查找所有.mp4文件及子文件夹









    def find_first_video_in_item(self, item):
        # 如果是视频文件，返回
        path = item.data(0, Qt.UserRole)
        if path and path.endswith('.mp4'):
            return item
        # 否则，遍历子节点
        for i in range(item.childCount()):
            child = item.child(i)
            result = self.find_first_video_in_item(child)
            if result is not None:
                return result
        return None



    def find_last_video_in_item(self, item):
        """在节点及其子节点中查找最后一个视频项（深度优先，逆序查找）"""
        # 如果是视频文件直接返回
        path = item.data(0, Qt.UserRole)
        if path and path.endswith('.mp4'):
            return item

        # 逆序遍历子节点
        for i in reversed(range(item.childCount())):
            child = item.child(i)
            result = self.find_last_video_in_item(child)
            if result is not None:
                return result
        return None


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        player = VideoPlayer()
        player.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.exception("错误")