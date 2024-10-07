import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLabel, QLineEdit, QMessageBox, QDialog, QProgressBar)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QTimer
from time_manager_logic import TimeManager
import json
from datetime import datetime

class TimeManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = TimeManager()
        self.is_updating = False  # 添加这行
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_task_list)
        self.timer.start(1000)  # 每秒更新一次

    def initUI(self):
        self.setWindowTitle('时间管理程序')
        self.setGeometry(100, 100, 1600, 900)  # 增加默认窗口大小

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 任务列表
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(['任务名称', '预期时间(H)', '实际时间(H)', '进度', '状态'])
        
        # 设置列宽
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 任务名称列
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 预期时间列
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 实际时间列
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 进度列
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 状态列
        
        self.task_table.setStyleSheet("""
            QTableWidget {
                background-color: #f0f0f0;
                alternate-background-color: #e0e0e0;
                selection-background-color: #a0a0a0;
            }
            QHeaderView::section {
                background-color: #d0d0d0;
                padding: 8px;
                border: 1px solid #c0c0c0;
                font-weight: bold;
                font-size: 28px;
            }
            QTableWidget::item {
                padding: 5px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.task_table)

        # 添加任务按钮
        add_button = QPushButton("+", self)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        add_button.clicked.connect(self.add_task)
        layout.addWidget(add_button, alignment=Qt.AlignLeft)  # 将按钮移到左侧

        # 其他按钮布局
        button_layout = QHBoxLayout()
        button_actions = {
            '删除任务': self.delete_task,
            '开始任务': self.start_task,
            '停止任务': self.stop_task,
            '完成任务': self.complete_task,
            '查看统计': self.show_statistics
        }
        for button_text, action in button_actions.items():
            button = QPushButton(button_text, self)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    border: none;
                    color: white;
                    padding: 15px 30px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 20px;
                    margin: 4px 2px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
            button.clicked.connect(action)
            button_layout.addWidget(button)

        layout.addLayout(button_layout)

        self.update_task_list()

    def update_task_list(self):
        if self.is_updating:
            return
        self.is_updating = True

        current_row = self.task_table.currentRow()
        current_column = self.task_table.currentColumn()

        self.task_table.setRowCount(len(self.manager.tasks))
        for row, task in enumerate(self.manager.tasks):
            # 任务名称
            name_item = QTableWidgetItem(task.name)
            name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
            self.task_table.setItem(row, 0, name_item)

            # 预期时间
            expected_time_item = QTableWidgetItem(f"{task.expected_time:.2f}")
            expected_time_item.setFlags(expected_time_item.flags() | Qt.ItemIsEditable)
            self.task_table.setItem(row, 1, expected_time_item)

            # 实际时间
            if task.start_time:
                elapsed_time = (datetime.now() - task.start_time).total_seconds() / 3600  # 转换为小时
                current_actual_time = task.actual_time + elapsed_time
            else:
                current_actual_time = task.actual_time
            actual_time_item = QTableWidgetItem(f"{current_actual_time:.2f}")
            self.task_table.setItem(row, 2, actual_time_item)

            # 进度
            progress_bar = QProgressBar()
            if task.expected_time > 0:
                progress_percent = min(100, (current_actual_time / task.expected_time) * 100)
                progress_bar.setRange(0, 100)
                progress_bar.setValue(int(progress_percent))
                progress_bar.setFormat(f"{progress_percent:.0f}%")
            else:
                progress_bar.setRange(0, 1)
                progress_bar.setValue(1)
                progress_bar.setFormat("N/A")

            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                    font-size: 16px;
                }
                QProgressBar::chunk {
                    background-color: %s;
                    width: 10px;
                    margin: 0.5px;
                }
            """ % ("#4CAF50" if current_actual_time <= task.expected_time else "#FF5252"))
            self.task_table.setCellWidget(row, 3, progress_bar)

            # 状态
            status = "进行中" if task.start_time else "未开始"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor('green' if status == "进行中" else 'red'))
            self.task_table.setItem(row, 4, status_item)

        if current_row >= 0 and current_column >= 0:
            self.task_table.setCurrentCell(current_row, current_column)

        self.is_updating = False

    def on_item_changed(self, item):
        if self.is_updating:
            return
        self.is_updating = True

        row = item.row()
        if item.column() == 0:  # 任务名称列
            new_name = item.text()
            self.manager.edit_task(row, new_name, self.manager.tasks[row].expected_time)
        elif item.column() == 1:  # 预期时间列
            try:
                new_expected_time = max(0.5, float(item.text()))
                self.manager.edit_task(row, self.manager.tasks[row].name, new_expected_time)
            except ValueError:
                QMessageBox.warning(self, "警告", "请输入有效的数字，已自动设置为0.5小时")
                self.manager.edit_task(row, self.manager.tasks[row].name, 0.5)
        self.manager.save_tasks()
        self.is_updating = False
        self.update_task_list()

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_():
            name, expected_time = dialog.get_task_info()
            if name is not None and expected_time is not None:
                try:
                    self.manager.add_task(name, expected_time)  # 不再乘以3600
                    self.update_task_list()
                except ValueError as e:
                    QMessageBox.warning(self, "警告", str(e))

    def delete_task(self):
        selected_rows = self.task_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        row = selected_rows[0].row()
        self.manager.delete_task(row)
        self.update_task_list()

    def start_task(self):
        selected_rows = self.task_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        row = selected_rows[0].row()
        self.manager.start_task(row)
        self.update_task_list()

    def stop_task(self):
        selected_rows = self.task_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        row = selected_rows[0].row()
        self.manager.stop_task(row)
        self.update_task_list()

    def complete_task(self):
        selected_rows = self.task_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        row = selected_rows[0].row()
        task = self.manager.tasks[row]
        self.manager.stop_task(row)
        
        # 保存完成的任务到本地文件
        completed_task = {
            "任务名称": task.name,
            "预期时间": task.expected_time,
            "实际时间": round(task.actual_time, 2)  # 保留两位小数
        }
        try:
            with open("已完成任务.json", "r", encoding="utf-8") as f:
                completed_tasks = json.load(f)
        except FileNotFoundError:
            completed_tasks = []
        
        completed_tasks.append(completed_task)
        
        with open("已完成任务.json", "w", encoding="utf-8") as f:
            json.dump(completed_tasks, f, ensure_ascii=False, indent=2)
        
        self.manager.delete_task(row)
        self.update_task_list()
        QMessageBox.information(self, "任务完成", f"任务 '{task.name}' 已完成并保存")

    def show_statistics(self):
        stats = self.manager.get_statistics()
        QMessageBox.information(self, "统计信息", 
                                f"总预期时间: {stats['总预期时间']:.2f}小时\n"
                                f"总实际时间: {stats['总实际时间']:.2f}小时\n"
                                f"效率: {stats['效率']:.2f}%")

class TaskDialog(QDialog):
    def __init__(self, parent=None, name='', expected_time=''):
        super().__init__(parent)
        self.setWindowTitle("添加任务")
        self.setGeometry(300, 300, 500, 250)

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit(self)
        self.name_input.setText(name)
        self.name_input.setStyleSheet("font-size: 24px;")
        layout.addWidget(QLabel("任务名称:", styleSheet="font-size: 24px;"))
        layout.addWidget(self.name_input)

        self.time_input = QLineEdit(self)
        self.time_input.setText(str(expected_time))
        self.time_input.setStyleSheet("font-size: 24px;")
        layout.addWidget(QLabel("预期时间(小时):", styleSheet="font-size: 24px;"))
        layout.addWidget(self.time_input)

        button_box = QHBoxLayout()
        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.ok_button.setStyleSheet("font-size: 24px; padding: 10px 20px; background-color: #2196F3; color: white;")
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("font-size: 24px; padding: 10px 20px; background-color: #2196F3; color: white;")
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)
        layout.addLayout(button_box)

        self.name = None
        self.expected_time = None

    def validate_and_accept(self):
        name = self.name_input.text()
        try:
            expected_time = float(self.time_input.text()) if self.time_input.text() else 0
            self.name = name
            self.expected_time = max(0.01, expected_time)  # 允许最小值为0.1小时
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字，已自动设置为0.5小时")
            self.name = name
            self.expected_time = 0.5
            self.accept()

    def get_task_info(self):
        return self.name, self.expected_time

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格，它在高 DPI 屏幕上表现较好
    font = app.font()
    font.setPointSize(12)  # 设置默认字体大小为12
    app.setFont(font)
    ex = TimeManagerGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()