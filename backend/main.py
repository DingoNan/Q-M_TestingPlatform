import gevent.monkey
gevent.monkey.patch_all()
import sys
import requests
import time

from PyQt5.QtCore import QUrl, Qt, QSettings, QStringListModel, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QLabel, QGroupBox,
    QGridLayout, QMessageBox, QCompleter
)

from core.locust.locust_model import (
    start_standalone_locust_headless_programmatically,
    start_standalone_locust_web_ui_programmatically,
    start_master_locust_web_ui_programmatically,
    start_work_locust_programmatically,
    start_master_locust_headless_programmatically
)


class GuardLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class FilterComboBox(QComboBox):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMaxVisibleItems(15)
        self._items = []

        self._guard_line_edit = GuardLineEdit(self)
        self.setLineEdit(self._guard_line_edit)
        self.lineEdit().clicked.connect(self.clicked.emit)

        self._completer_model = QStringListModel(self)
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self._completer)

        self._completer.activated[str].connect(self._on_completer_activated)
        self.lineEdit().textEdited.connect(self._on_text_edited)
        self.lineEdit().editingFinished.connect(self._sync_index_from_text)

    def _on_text_edited(self, text):
        if not self.isEnabled():
            return
        self._completer.setCompletionPrefix(text)
        if text.strip():
            self._completer.complete()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Down, Qt.Key_Up):
            if self.isEnabled() and self.count() > 0:
                self.showPopup()
                return
        super().keyPressEvent(event)

    def addItem(self, text, userData=None):
        text = str(text)
        self._items.append((text, userData))
        super().addItem(text, userData)
        self._refresh_completer()

    def clear(self):
        self._items = []
        super().clear()
        self.lineEdit().clear()
        self._refresh_completer()
        self.setCurrentIndex(-1)

    def _refresh_completer(self):
        self._completer_model.setStringList([text for text, _ in self._items])

    def _on_completer_activated(self, text):
        index = self.findText(text, Qt.MatchExactly)
        if index >= 0:
            self.setCurrentIndex(index)
            self.lineEdit().setText(text)

    def _sync_index_from_text(self):
        text = self.currentText().strip()
        if not text:
            self.setCurrentIndex(-1)
            return
        index = self.findText(text, Qt.MatchExactly)
        if index >= 0:
            self.setCurrentIndex(index)

    def currentData(self, role=Qt.UserRole):
        index = self.currentIndex()
        if index < 0:
            text = self.currentText().strip()
            for item_text, item_data in self._items:
                if item_text == text:
                    return item_data
            return None
        return super().currentData(role)

    def count(self):
        return len(self._items)

    def setPlaceholder(self, text):
        self.lineEdit().setPlaceholderText(text)


class TestConfigApp(QWidget):
    def __init__(self):
        super().__init__()
        self.web_ui = False
        self.max_num = 1000000000
        self.project_data = {}
        self.settings = QSettings("BlackBagTest", "LocustConfig")
        self.initUI()
        self.apply_stylesheet()
        self.load_settings()
        self.init_empty_data()
        self.load_project_data(show_error=False, auto_select_first=True)

    def initUI(self):
        self.setWindowTitle('BlackBagTest')
        self.setMinimumSize(820, 620)

        svg_data = '''
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
          <defs>
            <linearGradient id='grad' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='#3b82f6'/>
              <stop offset='100%' stop-color='#10b981'/>
            </linearGradient>
          </defs>
          <circle cx='32' cy='32' r='30' fill='url(#grad)' stroke='#ffffff' stroke-width='2'/>
          <path d='M22 18v12h8v8h8v-8h2c1.1 0 2-.9 2-2s-.9-2-2-2h-2V18h-8v-6h-4v6h-8zm0 24v-6h-2c-2.2 0-4-1.8-4-4v-6H14v12h8v6h4v-6h8v-8h-8v-6h-4v6zm26 8v-4h-4v4h4zm-4-6v-6h4v6h-4z' fill='#ffffff'/>
        </svg>
        '''
        svg_bytes = svg_data.encode('utf-8')
        pixmap = QPixmap()
        if pixmap.loadFromData(svg_bytes, format='svg'):
            self.setWindowIcon(QIcon(pixmap))

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        mode_group = QGroupBox("运行模式")
        mode_layout = QGridLayout()
        mode_layout.setVerticalSpacing(10)
        mode_layout.setHorizontalSpacing(15)

        mode_layout.addWidget(QLabel("分布式模式:"), 0, 0)
        self.work_mode_combobox = QComboBox()
        self.work_mode_combobox.addItems(['Standalone', 'Master', 'Work'])
        self.work_mode_combobox.currentIndexChanged.connect(self.toggleFields)
        mode_layout.addWidget(self.work_mode_combobox, 0, 1)

        mode_layout.addWidget(QLabel("运行模式:"), 0, 2)
        self.run_mode_combobox = QComboBox()
        self.run_mode_combobox.addItems(['Headless'])
        self.run_mode_combobox.currentIndexChanged.connect(self.toggleFields)
        mode_layout.addWidget(self.run_mode_combobox, 0, 3)

        mode_layout.addWidget(QLabel("测试平台后端:"), 1, 0)
        self.backend_domain_input = QLineEdit('http://127.0.0.1:8000')
        self.backend_domain_input.editingFinished.connect(self.on_backend_changed)

        backend_row_layout = QHBoxLayout()
        backend_row_layout.setContentsMargins(0, 0, 0, 0)
        backend_row_layout.setSpacing(8)
        backend_row_layout.addWidget(self.backend_domain_input)

        self.refresh_project_button = QPushButton("刷新项目")
        self.refresh_project_button.setFixedHeight(32)
        self.refresh_project_button.clicked.connect(self.on_refresh_project_clicked)
        backend_row_layout.addWidget(self.refresh_project_button)

        mode_layout.addLayout(backend_row_layout, 1, 1, 1, 3)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        param_group = QGroupBox("压测参数")
        param_layout = QGridLayout()
        param_layout.setVerticalSpacing(10)
        param_layout.setHorizontalSpacing(15)

        param_layout.addWidget(QLabel("压测域名:"), 0, 0)
        self.test_domain_input = QLineEdit('http://127.0.0.1:8000')
        param_layout.addWidget(self.test_domain_input, 0, 1)

        param_layout.addWidget(QLabel("并发用户数:"), 0, 2)
        self.concurrent_users_input = QSpinBox()
        self.concurrent_users_input.setRange(1, self.max_num)
        self.concurrent_users_input.setValue(1)
        param_layout.addWidget(self.concurrent_users_input, 0, 3)

        param_layout.addWidget(QLabel("每秒启动用户数:"), 1, 0)
        self.users_per_second_input = QSpinBox()
        self.users_per_second_input.setRange(1, self.max_num)
        self.users_per_second_input.setValue(1)
        param_layout.addWidget(self.users_per_second_input, 1, 1)

        param_layout.addWidget(QLabel("运行时间 (秒):"), 1, 2)
        self.run_time_input = QSpinBox()
        self.run_time_input.setRange(1, self.max_num)
        self.run_time_input.setValue(1)
        param_layout.addWidget(self.run_time_input, 1, 3)

        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)

        script_group = QGroupBox("脚本配置")
        script_layout = QGridLayout()
        script_layout.setVerticalSpacing(10)
        script_layout.setHorizontalSpacing(15)
        script_layout.setColumnStretch(1, 1)
        script_layout.setColumnStretch(3, 1)

        script_layout.addWidget(QLabel("选择项目:"), 0, 0)
        self.project_combo = FilterComboBox()
        self.project_combo.setPlaceholder("请输入项目名称搜索")
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        script_layout.addWidget(self.project_combo, 0, 1)

        script_layout.addWidget(QLabel("用户:"), 0, 2)
        self.user_combo = FilterComboBox()
        self.user_combo.setPlaceholder("请输入用户名称搜索")
        self.user_combo.setEnabled(False)
        self.user_combo.clicked.connect(self.on_sub_combo_clicked)
        script_layout.addWidget(self.user_combo, 0, 3)

        script_layout.addWidget(QLabel("环境:"), 1, 0)
        self.env_combo = FilterComboBox()
        self.env_combo.setPlaceholder("请输入环境名称搜索")
        self.env_combo.setEnabled(False)
        self.env_combo.clicked.connect(self.on_sub_combo_clicked)
        script_layout.addWidget(self.env_combo, 1, 1)

        script_layout.addWidget(QLabel("脚本:"), 1, 2)
        self.script_combo = FilterComboBox()
        self.script_combo.setPlaceholder("请输入脚本名称搜索")
        self.script_combo.setEnabled(False)
        self.script_combo.clicked.connect(self.on_sub_combo_clicked)
        script_layout.addWidget(self.script_combo, 1, 3)

        script_group.setLayout(script_layout)
        main_layout.addWidget(script_group)

        distributed_group = QGroupBox("分布式设置")
        distributed_layout = QGridLayout()
        distributed_layout.setVerticalSpacing(10)
        distributed_layout.setHorizontalSpacing(15)

        distributed_layout.addWidget(QLabel("Master节点IP:"), 0, 0)
        self.master_ip_input = QLineEdit('127.0.0.1')
        distributed_layout.addWidget(self.master_ip_input, 0, 1)

        distributed_layout.addWidget(QLabel("期望Work节点数:"), 0, 2)
        self.work_count_input = QSpinBox()
        self.work_count_input.setRange(1, self.max_num)
        self.work_count_input.setValue(1)
        distributed_layout.addWidget(self.work_count_input, 0, 3)

        distributed_group.setLayout(distributed_layout)
        main_layout.addWidget(distributed_group)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.help_button = QPushButton()
        self.help_button.setIcon(self.style().standardIcon(self.style().SP_MessageBoxQuestion))
        self.help_button.setToolTip("关于本工具")
        self.help_button.setFixedSize(32, 32)
        self.help_button.clicked.connect(self.show_about)
        button_layout.addWidget(self.help_button)

        button_layout.addSpacing(10)

        self.submit_button = QPushButton('开始执行压测')
        self.submit_button.setMinimumHeight(40)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.submit_button.clicked.connect(self.submitForm)
        button_layout.addWidget(self.submit_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.toggleFields()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #1f2d3d;
            }
            QLabel {
                color: #2c3e50;
                min-width: 60px;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #d0d7de;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #0969da;
                outline: none;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1f2d3d;
            }
            QPushButton:pressed {
                background-color: #0f1a24;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #2c3e50;
                width: 0px;
                height: 0px;
                margin-right: 8px;
            }
        """)

        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #e1e4e8;
                border-radius: 16px;
            }
        """)

        self.refresh_project_button.setStyleSheet("""
            QPushButton {
                background-color: #0969da;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10pt;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #0860ca;
            }
        """)

    def show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("关于 BlackBagTest")
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        msg.setText(
            "<b>BlackBagTest 压测配置工具</b><br><br>"
            "版本 1.2<br>"
            "基于 PyQt5 和 Locust 的分布式压测客户端<br><br>"
            "特性：<br>"
            "• 下拉框支持模糊搜索<br>"
            "• 后端域名自动保存"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox { min-width: 460px; }
            QLabel { min-width: 420px; }
        """)
        msg.exec_()

    def show_warning_message(self, title, text):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox { min-width: 420px; }
            QLabel { min-width: 380px; }
        """)
        msg.exec_()

    def init_empty_data(self):
        self.project_data = {}
        self.clear_project_related_combos()

    def clear_project_related_combos(self):
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.setCurrentIndex(-1)
        self.project_combo.blockSignals(False)

        self.user_combo.clear()
        self.user_combo.setEnabled(False)
        self.user_combo.setCurrentIndex(-1)

        self.env_combo.clear()
        self.env_combo.setEnabled(False)
        self.env_combo.setCurrentIndex(-1)

        self.script_combo.clear()
        self.script_combo.setEnabled(False)
        self.script_combo.setCurrentIndex(-1)

    def has_selected_project(self):
        project_name = self.project_combo.currentText().strip()
        return bool(project_name and project_name in self.project_data)

    def on_sub_combo_clicked(self):
        if not self.has_selected_project():
            self.show_warning_message("参数错误", "请先选择项目")

    def load_settings(self):
        saved_domain = self.settings.value("backend_domain", "http://127.0.0.1:8000")
        self.backend_domain_input.setText(saved_domain)

    def save_settings(self):
        self.settings.setValue("backend_domain", self.backend_domain_input.text())

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def on_backend_changed(self):
        self.load_project_data(show_error=True, auto_select_first=True)

    def on_refresh_project_clicked(self):
        self.load_project_data(show_error=True, auto_select_first=True)

    def load_project_data(self, show_error=False, auto_select_first=False):
        backend_domain = self.backend_domain_input.text().strip().rstrip('/')
        self.init_empty_data()

        if not backend_domain:
            if show_error:
                self.show_warning_message("获取项目失败", "获取项目失败，请检查测试平台域名配置")
            return

        url = f"{backend_domain}/test/get_locust_run_data"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                if show_error:
                    self.show_warning_message("获取项目失败", "获取项目失败，请检查测试平台域名配置")
                return

            data = response.json()
            if data.get('code') != 200:
                if show_error:
                    self.show_warning_message("获取项目失败", "获取项目失败，请检查测试平台域名配置")
                return

            result = data.get('result') or {}
            if not isinstance(result, dict) or not result:
                if show_error:
                    self.show_warning_message("获取项目失败", "获取项目失败，请检查测试平台域名配置")
                return

            self.project_data = result

            self.project_combo.blockSignals(True)
            self.project_combo.clear()
            for project_name in self.project_data.keys():
                self.project_combo.addItem(project_name, project_name)

            if self.project_combo.count() > 0 and auto_select_first:
                self.project_combo.setCurrentIndex(0)
            else:
                self.project_combo.setCurrentIndex(-1)
            self.project_combo.blockSignals(False)

            if self.project_combo.count() > 0 and auto_select_first:
                self.on_project_changed(self.project_combo.currentIndex())

        except Exception:
            self.init_empty_data()
            if show_error:
                self.show_warning_message("获取项目失败", "获取项目失败，请检查测试平台域名配置")

    def on_project_changed(self, index):
        self.user_combo.clear()
        self.user_combo.setEnabled(False)
        self.user_combo.setCurrentIndex(-1)

        self.env_combo.clear()
        self.env_combo.setEnabled(False)
        self.env_combo.setCurrentIndex(-1)

        self.script_combo.clear()
        self.script_combo.setEnabled(False)
        self.script_combo.setCurrentIndex(-1)

        if index < 0 or not self.project_data:
            return

        project_name = self.project_combo.currentText().strip()
        if not project_name:
            return

        project_info = self.project_data.get(project_name)
        if not project_info:
            return

        users = project_info.get('users', []) or []
        for user in users:
            username = user.get('username', '')
            user_id = user.get('id')
            if username:
                self.user_combo.addItem(username, user_id)
        self.user_combo.setEnabled(len(users) > 0)
        if self.user_combo.count() > 0:
            self.user_combo.setCurrentIndex(0)

        envs = project_info.get('envs', []) or []
        for env in envs:
            env_name = env.get('name', '')
            env_id = env.get('id')
            if env_name:
                self.env_combo.addItem(env_name, env_id)
        self.env_combo.setEnabled(len(envs) > 0)
        if self.env_combo.count() > 0:
            self.env_combo.setCurrentIndex(0)

        scripts = project_info.get('scripts', []) or []
        for script in scripts:
            script_name = script.get('name', '')
            script_id = script.get('id')
            if script_name:
                self.script_combo.addItem(script_name, script_id)
        self.script_combo.setEnabled(len(scripts) > 0)
        if self.script_combo.count() > 0:
            self.script_combo.setCurrentIndex(0)

    @staticmethod
    def get_report_id(server_host, case_id, user_id, env_id, max_user, rate, duration, cpu=0, memory=0):
        start_time = time.strftime('%Y-%m-%dT%H:%M:%S')
        report_data = {
            'case': case_id,
            'user': user_id,
            'env': env_id,
            'max_user': max_user,
            'rate': rate,
            'cpu': cpu,
            'memory': memory,
            'duration': duration,
            'start_time': start_time,
            'end_time': start_time
        }
        response = requests.post(url=server_host + '/report/locust/', json=report_data).json()
        return response['result']['id']

    def toggleFields(self):
        run_mode = self.run_mode_combobox.currentText()
        work_mode = self.work_mode_combobox.currentText()

        if work_mode == 'Standalone':
            self.master_ip_input.setEnabled(False)
            self.work_count_input.setEnabled(False)
            if run_mode == 'WebUI':
                self.test_domain_input.setEnabled(False)
                self.concurrent_users_input.setEnabled(False)
                self.users_per_second_input.setEnabled(False)
                self.run_time_input.setEnabled(False)
                self.submit_button.setText("启动Web服务")
            else:
                self.backend_domain_input.setEnabled(True)
                self.refresh_project_button.setEnabled(True)
                self.test_domain_input.setEnabled(True)
                self.concurrent_users_input.setEnabled(True)
                self.users_per_second_input.setEnabled(True)
                self.run_time_input.setEnabled(True)
                self.submit_button.setText("开始执行压测")
        elif work_mode == 'Master':
            self.master_ip_input.setEnabled(False)
            if run_mode == 'WebUI':
                self.test_domain_input.setEnabled(False)
                self.work_count_input.setEnabled(False)
                self.concurrent_users_input.setEnabled(False)
                self.users_per_second_input.setEnabled(False)
                self.run_time_input.setEnabled(False)
                self.submit_button.setText("启动Web服务")
            else:
                self.work_count_input.setEnabled(True)
                self.backend_domain_input.setEnabled(True)
                self.refresh_project_button.setEnabled(True)
                self.test_domain_input.setEnabled(True)
                self.concurrent_users_input.setEnabled(True)
                self.users_per_second_input.setEnabled(True)
                self.run_time_input.setEnabled(True)
                self.submit_button.setText("开始执行压测")
        else:
            self.master_ip_input.setEnabled(True)
            self.work_count_input.setEnabled(False)
            self.backend_domain_input.setEnabled(True)
            self.refresh_project_button.setEnabled(True)
            self.test_domain_input.setEnabled(False)
            self.concurrent_users_input.setEnabled(False)
            self.users_per_second_input.setEnabled(False)
            self.run_time_input.setEnabled(False)
            self.submit_button.setText("加入Master节点")

    def submitForm(self):
        if not self.has_selected_project():
            self.show_warning_message("参数错误", "请先选择项目")
            return
        if self.user_combo.currentData() is None:
            self.show_warning_message("参数错误", "请先选择用户")
            return
        if self.env_combo.currentData() is None:
            self.show_warning_message("参数错误", "请先选择环境")
            return
        if self.script_combo.currentData() is None:
            self.show_warning_message("参数错误", "请先选择脚本")
            return

        backend_domain = self.backend_domain_input.text().strip()
        web_port = 8089
        test_domain = self.test_domain_input.text().strip()
        run_mode = self.run_mode_combobox.currentText()
        work_mode = self.work_mode_combobox.currentText()
        concurrent_users = self.concurrent_users_input.value()
        users_per_second = self.users_per_second_input.value()
        run_time = self.run_time_input.value()
        case_id = self.script_combo.currentData()
        env_id = self.env_combo.currentData()
        user_id = self.user_combo.currentData()
        master_ip = self.master_ip_input.text().strip()
        work_count = self.work_count_input.value()

        if work_mode == 'Standalone':
            report_id = self.get_report_id(
                backend_domain, case_id, user_id, env_id,
                concurrent_users, users_per_second, run_time
            )
            if run_mode == 'WebUI':
                url = QUrl(f"http://127.0.0.1:{web_port}")
                QDesktopServices.openUrl(url)
                start_standalone_locust_web_ui_programmatically(
                    work_mode, case_id, env_id, user_id, backend_domain,
                    web_port, report_id
                )
            else:
                start_standalone_locust_headless_programmatically(
                    work_mode, case_id, env_id, user_id, backend_domain,
                    run_time, users_per_second, concurrent_users,
                    test_domain, report_id
                )
        elif work_mode == 'Master':
            report_id = self.get_report_id(
                backend_domain, case_id, user_id, env_id,
                concurrent_users, users_per_second, run_time
            )
            if run_mode == 'WebUI':
                url = QUrl(f"http://127.0.0.1:{web_port}")
                QDesktopServices.openUrl(url)
                start_master_locust_web_ui_programmatically(
                    work_mode, case_id, env_id, user_id, backend_domain,
                    web_port
                )
            else:
                start_master_locust_headless_programmatically(
                    work_mode, case_id, env_id, user_id, backend_domain,
                    run_time, users_per_second, concurrent_users,
                    test_domain, work_count, report_id
                )
        else:
            start_work_locust_programmatically(
                work_mode, case_id, env_id, user_id, backend_domain, master_ip
            )


if __name__ == '__main__':
    # 先注释掉 core/system_function/faker.py 中的inspect.getsource
    # 打包命令：pyinstaller -F --icon=./core/locust/locust.ico --name BlackBagTest  main.py
    app = QApplication(sys.argv)
    window = TestConfigApp()
    window.show()
    sys.exit(app.exec_())