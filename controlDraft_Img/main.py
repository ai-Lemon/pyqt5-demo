# coding:utf-8

from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget, QApplication, QPushButton, \
    QComboBox, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QToolBar, \
    QAction, QTextEdit, QFrame, QSpinBox, QStackedWidget,QDoubleSpinBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from setting.controls.myControls import message,DraggableImg, DraggableLabel, MyWidget,DraggableLine
from UI import laberMode
from setting.service import *

import sys
import os

class laberModeWindows(QWidget, laberMode.Ui_Form):
    """打印模板编辑窗口"""
    def __init__(self, xSize=100, ySize=100):
        """xSzie,ySize:宽高(mm)"""
        super(laberModeWindows, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('./setting/img/网络.png'))  # 加图标

        self.dpi = 300  # 默认打印像素大小
        self.dpiScreen = getScreenPixel()  # 屏幕像素
        self.dpiScreen = round(self.dpiScreen) if self.dpiScreen else 96
        self.xSize = xSize
        self.ySize = ySize

        self.widgetID = 0  # 添加的控件ID
        self.currentWidget = None  # 当前控件
        self.addWidgetDict = {}
        self.pastData = {}  # 复制的控件信息
        self.variableWidgetList = {}  # 记录添加的可变控件
        self.tempModelData = None   #记录模板数据
        self.moveStatus = False     #记录控件是否移动
        self.changeSizeStatus = False   #记录控件是否被缩放
        self.tracingPoint = 0           #描点位置
        self.fontChangeStatus = False   #字体状态改变
        self.isChoiseCom = False        #是否选中控件
        self.imgSvaeDatas = None         #图像数据保存

        self.messages = message()
        self.messages.messageboxSignal.connect(self.showMsgBox)

        self.initUI()
        self.choiseAttrSetting(0)

        for i in self.children():
            # 根据实际情况去过滤一些不带焦点功能的子组件
            if isinstance(i, QVBoxLayout) or isinstance(i, QHBoxLayout) or isinstance(i, QGridLayout) or isinstance(i,QAction):
                pass
            else:
                i.setFocusPolicy(Qt.NoFocus)

        self.showMaximized()

    def initUI(self):
        layout = QGridLayout()

        # 工具栏
        self.toolBar = QToolBar()
        self.toolBar.addSeparator()
        self.str_AC = QAction(QIcon("./setting/img/字符串.png"), "字符串", self)
        self.str_AC.triggered.connect(lambda: self.addWidget(0))
        self.toolBar.addAction(self.str_AC)
        self.toolBar.addSeparator()
        self.img_AC = QAction(QIcon("./setting/img/图片.png"), "图片", self)
        self.img_AC.triggered.connect(lambda: self.addWidget(1))
        self.toolBar.addAction(self.img_AC)
        self.toolBar.addSeparator()
        self.Hline_AC = QAction(QIcon("./setting/img/横线.png"), "横线", self)
        self.Hline_AC.triggered.connect(lambda: self.addWidget(2))
        self.toolBar.addAction(self.Hline_AC)
        self.toolBar.addSeparator()
        self.Vline_AC = QAction(QIcon("./setting/img/竖线.png"), "竖线", self)
        self.Vline_AC.triggered.connect(lambda: self.addWidget(3))
        self.toolBar.addAction(self.Vline_AC)
        self.toolBar.addSeparator()
        self.barCode_AC = QAction(QIcon("./setting/img/条形码.png"), "条形码", self)
        self.barCode_AC.triggered.connect(lambda: self.addWidget(4))
        self.toolBar.addAction(self.barCode_AC)
        self.toolBar.addSeparator()
        self.qrCode_AC = QAction(QIcon("./setting/img/二维码.png"), "二维码", self)
        self.qrCode_AC.triggered.connect(lambda: self.addWidget(5))
        self.toolBar.addAction(self.qrCode_AC)
        self.toolBar.addSeparator()
        self.save_AV = QAction(QIcon("./setting/img/保存.png"), "保存", self)
        self.save_AV.triggered.connect(self.saveModel)
        self.toolBar.addAction(self.save_AV)
        self.toolBar.addSeparator()
        self.del_AC = QAction(QIcon("./setting/img/deleteRow.png"), "删除", self)
        self.del_AC.triggered.connect(self.deleteControls)
        self.toolBar.addAction(self.del_AC)
        self.toolBar.addSeparator()
        self.preview_AC = QAction(QIcon("./setting/img/预览.png"), "预览", self)
        self.preview_AC.triggered.connect(self.previewModel)
        self.toolBar.addAction(self.preview_AC)
        self.toolBar.addSeparator()
        label = QAction('标签尺寸(mm)：', self)
        self.toolBar.addAction(label)
        self.labelSizeXLE = QLineEdit()
        self.labelSizeXLE.setText(str(self.xSize))
        self.labelSizeXLE.setMaximumWidth(40)
        self.labelSizeXLE.setEnabled(False)
        self.toolBar.addWidget(self.labelSizeXLE)
        label = QAction('x', self)
        self.toolBar.addAction(label)
        self.labelSizeYLE = QLineEdit()
        self.labelSizeYLE.setText(str(self.ySize))
        self.labelSizeYLE.setMaximumWidth(40)
        self.labelSizeYLE.setEnabled(False)
        self.toolBar.addWidget(self.labelSizeYLE)
        self.toolBar.setStyleSheet("QToolBar{background:#e6e6e6;spacing:8px;}")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 文字图片垂直排列
        layout.addWidget(self.toolBar, 0, 0, 1, 10)

        self.toolBar = QToolBar()
        self.toolBar.addSeparator()
        label = QAction("默认dpi：", self)
        self.toolBar.addAction(label)
        self.dpiSB = QSpinBox()
        self.dpiSB.setMaximum(9999999)
        self.dpiSB.setValue(300)
        self.dpiSB.valueChanged.connect(self.changDpi)
        self.toolBar.addWidget(self.dpiSB)
        self.toolBar.addSeparator()

        label = QAction("位置X(mm)：", self)
        self.toolBar.addAction(label)
        self.xLocationCB = QDoubleSpinBox()
        self.xLocationCB.setDecimals(1)
        self.xLocationCB.setSingleStep(0.1)
        self.xLocationCB.setMaximum(self.xSize)
        self.xLocationCB.setMinimum(0)
        self.xLocationCB.setValue(1)
        self.xLocationCB.valueChanged.connect(self.changeComponentPoint)
        self.toolBar.addWidget(self.xLocationCB)
        label = QAction("位置Y(mm):", self)
        self.toolBar.addAction(label)
        self.yLocationCB = QDoubleSpinBox()
        self.yLocationCB.setDecimals(1)
        self.yLocationCB.setSingleStep(0.1)
        self.yLocationCB.setMaximum(self.ySize)
        self.yLocationCB.setMinimum(0)
        self.yLocationCB.setValue(1)
        self.yLocationCB.valueChanged.connect(self.changeComponentPoint)
        self.toolBar.addWidget(self.yLocationCB)
        label = QAction("位置描点：", self)
        self.toolBar.addAction(label)
        self.locationPointCB = QComboBox()
        self.locationPointCB.addItems(['左上', '左下', '右上', '右下'])
        self.locationPointCB.currentIndexChanged.connect(self.changeTracingPoint)
        self.toolBar.addWidget(self.locationPointCB)
        self.toolBar.setStyleSheet("QToolBar{background:#e6e6e6;spacing:8px;}")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 文字图片垂直排列
        layout.addWidget(self.toolBar, 1, 0, 1, 10)

        # 左侧属性布局
        self.attribute_stackedWidget = QStackedWidget()
        # 文本属性
        widget1 = QWidget()
        widget_layout = QVBoxLayout()
        childLlay = QHBoxLayout()
        label = QLabel('文本：')
        label.setMinimumWidth(100)
        childLlay.addWidget(label)
        self.textEdit = QTextEdit()
        self.textEdit.setMaximumHeight(100)
        self.textEdit.textChanged.connect(self.changeLabelValue)
        childLlay.addWidget(self.textEdit)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('字体大小：')
        # label.setMinimumWidth(100)
        childLlay.addWidget(label)
        self.fontSizeSB = QDoubleSpinBox()
        self.fontSizeSB.setDecimals(0)
        self.fontSizeSB.setSingleStep(1)
        self.fontSizeSB.setMaximum(72)
        self.fontSizeSB.setMinimum(1)
        self.fontSizeSB.setValue(10)
        self.fontSizeSB.valueChanged.connect(self.changeFontSize)
        childLlay.addWidget(self.fontSizeSB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('字体：')
        label.setMinimumWidth(100)
        childLlay.addWidget(label)
        self.choiseFontTypeCB = QComboBox()
        self.choiseFontTypeCB.addItems(['黑体', '宋体', '楷体', 'Arial'])
        self.choiseFontTypeCB.currentTextChanged.connect(self.changeFontType)
        childLlay.addWidget(self.choiseFontTypeCB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('加粗：')
        label.setMinimumWidth(100)
        childLlay.addWidget(label)
        self.choiseFontThicknessCB = QComboBox()
        self.choiseFontThicknessCB.addItems(['否', '是'])
        self.choiseFontThicknessCB.currentIndexChanged.connect(self.changeFontThickness)
        childLlay.addWidget(self.choiseFontThicknessCB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('压缩比(%)：')
        label.setMinimumWidth(100)
        childLlay.addWidget(label)
        self.compressionRatioSB = QDoubleSpinBox()
        self.compressionRatioSB.setDecimals(0)
        self.compressionRatioSB.setSingleStep(1)
        self.compressionRatioSB.setMaximum(200)
        self.compressionRatioSB.setMinimum(1)
        self.compressionRatioSB.setValue(100)
        self.compressionRatioSB.valueChanged.connect(self.changeFontSpacing)
        childLlay.addWidget(self.compressionRatioSB)
        widget_layout.addLayout(childLlay)
        widget1.setLayout(widget_layout)
        self.attribute_stackedWidget.addWidget(widget1)
        # 图片属性
        widget2 = QWidget()
        widget_layout = QVBoxLayout()
        childLlay = QHBoxLayout()
        label = QLabel('图片选择：')
        childLlay.addWidget(label)
        self.imgPathLE = QLineEdit()
        childLlay.addWidget(self.imgPathLE)
        self.choiseImgPathPB = QPushButton('选择')
        self.choiseImgPathPB.clicked.connect(self.choiseImgPath)
        childLlay.addWidget(self.choiseImgPathPB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('高度(mm)：')
        childLlay.addWidget(label)
        self.imgHeightSB = QDoubleSpinBox()
        self.imgHeightSB.setDecimals(1)
        self.imgHeightSB.setSingleStep(0.1)
        self.imgHeightSB.setMaximum(self.ySize)
        self.imgHeightSB.setMinimum(0)
        self.imgHeightSB.setValue(20)
        childLlay.addWidget(self.imgHeightSB)
        label = QLabel('宽度(mm)：')
        childLlay.addWidget(label)
        self.imgWidthSB = QDoubleSpinBox()
        self.imgWidthSB.setDecimals(1)
        self.imgWidthSB.setSingleStep(0.1)
        self.imgWidthSB.setMaximum(self.xSize)
        self.imgWidthSB.setMinimum(0)
        self.imgWidthSB.setValue(20)
        childLlay.addWidget(self.imgWidthSB)
        self.imgWidthSB.valueChanged.connect(self.changeComponentSBValue)
        self.imgHeightSB.valueChanged.connect(self.changeComponentSBValue)
        widget_layout.addLayout(childLlay)
        widget2.setLayout(widget_layout)
        self.attribute_stackedWidget.addWidget(widget2)
        # 线条属性
        widget3 = QWidget()
        widget_layout = QVBoxLayout()
        childLlay = QHBoxLayout()
        label = QLabel('粗细(mm)：')
        childLlay.addWidget(label)
        self.lineSizeSB = QDoubleSpinBox()
        self.lineSizeSB.setDecimals(1)
        self.lineSizeSB.setSingleStep(0.1)
        self.lineSizeSB.setMaximum(1000)
        self.lineSizeSB.setMinimum(0.1)
        self.lineSizeSB.setValue(0.5)
        self.lineSizeSB.valueChanged.connect(self.changeLineThickness)
        childLlay.addWidget(self.lineSizeSB)

        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('长度(mm)：')
        childLlay.addWidget(label)
        childLlay.addWidget(self.lineSizeSB)
        self.lineLengthSB = QDoubleSpinBox()
        self.lineLengthSB.setDecimals(1)
        self.lineLengthSB.setSingleStep(0.1)
        self.lineLengthSB.setMaximum(1000)
        self.lineLengthSB.setMinimum(0.1)
        self.lineLengthSB.setValue(20)
        self.lineLengthSB.valueChanged.connect(self.changeLineLength)
        childLlay.addWidget(self.lineLengthSB)
        widget_layout.addLayout(childLlay)
        widget3.setLayout(widget_layout)
        self.attribute_stackedWidget.addWidget(widget3)
        # 条形码属性
        widget4 = QWidget()
        widget_layout = QVBoxLayout()
        childLlay = QHBoxLayout()
        label = QLabel('参数值：')
        childLlay.addWidget(label)
        self.barCodeValueLE = QTextEdit()
        self.barCodeValueLE.setMaximumHeight(80)
        self.barCodeValueLE.textChanged.connect(self.changeBarCodeImg)
        childLlay.addWidget(self.barCodeValueLE)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('文本显示：')
        childLlay.addWidget(label)
        self.barCodeShowTextCB = QComboBox()
        self.barCodeShowTextCB.addItems(['是', '否'])
        self.barCodeShowTextCB.currentIndexChanged.connect(self.changeBarCodeImg)
        childLlay.addWidget(self.barCodeShowTextCB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('文本间距：')
        childLlay.addWidget(label)
        self.barCodeTextSpacingCB = QSpinBox()
        self.barCodeTextSpacingCB.setMaximum(20)
        self.barCodeTextSpacingCB.setMinimum(0)
        self.barCodeTextSpacingCB.setValue(1)
        self.barCodeTextSpacingCB.valueChanged.connect(self.changeBarCodeImg)
        childLlay.addWidget(self.barCodeTextSpacingCB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('编码规范：')
        childLlay.addWidget(label)
        self.barCodeStyleCB = QComboBox()
        self.barCodeStyleCB.addItems(['Code128'])
        self.barCodeStyleCB.currentIndexChanged.connect(self.changeBarCodeImg)
        childLlay.addWidget(self.barCodeStyleCB)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('高度(mm)：')
        childLlay.addWidget(label)
        self.barHeightSB = QDoubleSpinBox()
        self.barHeightSB.setDecimals(1)
        self.barHeightSB.setSingleStep(0.1)
        self.barHeightSB.setMaximum(self.ySize)
        self.barHeightSB.setMinimum(0)
        self.barHeightSB.setValue(20)
        childLlay.addWidget(self.barHeightSB)
        label = QLabel('宽度(mm)：')
        childLlay.addWidget(label)
        self.barWidthSB = QDoubleSpinBox()
        self.barWidthSB.setDecimals(1)
        self.barWidthSB.setSingleStep(0.1)
        self.barWidthSB.setMaximum(self.ySize)
        self.barWidthSB.setMinimum(0)
        self.barWidthSB.setValue(20)
        childLlay.addWidget(self.barWidthSB)
        self.barHeightSB.valueChanged.connect(self.changeComponentSBValue)
        self.barWidthSB.valueChanged.connect(self.changeComponentSBValue)
        widget_layout.addLayout(childLlay)
        widget4.setLayout(widget_layout)
        self.attribute_stackedWidget.addWidget(widget4)
        # 二维码属性
        widget5 = QWidget()
        widget_layout = QVBoxLayout()
        childLlay = QHBoxLayout()
        label = QLabel('参数值：')
        childLlay.addWidget(label)
        self.qrCodeValueLE = QTextEdit()
        self.qrCodeValueLE.setMaximumHeight(80)
        self.qrCodeValueLE.textChanged.connect(self.changeQRCodeImg)
        childLlay.addWidget(self.qrCodeValueLE)
        widget_layout.addLayout(childLlay)
        childLlay = QHBoxLayout()
        label = QLabel('高度(mm)：')
        childLlay.addWidget(label)
        self.qrHeightSB = QDoubleSpinBox()
        self.qrHeightSB.setDecimals(1)
        self.qrHeightSB.setSingleStep(0.1)
        self.qrHeightSB.setMaximum(self.ySize)
        self.qrHeightSB.setMinimum(0)
        self.qrHeightSB.setValue(20)
        childLlay.addWidget(self.qrHeightSB)
        label = QLabel('宽度(mm)：')
        childLlay.addWidget(label)
        self.qrWidthSB = QDoubleSpinBox()
        self.qrWidthSB.setDecimals(1)
        self.qrWidthSB.setSingleStep(0.1)
        self.qrWidthSB.setMaximum(self.ySize)
        self.qrWidthSB.setMinimum(0)
        self.qrWidthSB.setValue(20)
        childLlay.addWidget(self.qrWidthSB)
        self.qrHeightSB.valueChanged.connect(self.changeComponentSBValue)
        self.qrWidthSB.valueChanged.connect(self.changeComponentSBValue)
        widget_layout.addLayout(childLlay)
        widget5.setLayout(widget_layout)
        self.attribute_stackedWidget.addWidget(widget5)
        layout.addWidget(self.attribute_stackedWidget, 2, 0, 1, 2)

        # 图像编辑区
        aAspectRatio = self.ySize / self.xSize  # 模板长宽比

        self.widgets = MyWidget()
        self.widgets.setObjectName('widgets')
        self.widgets.setStyleSheet("""
                                                        QWidget #widgets{
                                                            border:0.5px solid black;
                                                            background:#b9d1ea;
                                                        }
                                                        """)
        widgetsLay = QHBoxLayout()
        frame = QFrame()
        widgetsLay.addWidget(frame)
        self.editZone = QWidget(self.widgets)
        self.editZone.setObjectName('editZone')

        self.editZone.setMaximumSize(round(self.xSize / 25.4 * self.dpiScreen),round(self.ySize / 25.4 * self.dpiScreen))
        self.editZone.setMinimumSize(round(self.xSize / 25.4 * self.dpiScreen),round(self.ySize / 25.4 * self.dpiScreen))

        self.editZone.setStyleSheet("""
                                                QWidget #editZone{
                                                    border:0.5px solid black;
                                                    background-color:white;
                                                }
                                                """)
        self.editZone.show()
        widgetsLay.addWidget(self.editZone)
        frame = QFrame()
        widgetsLay.addWidget(frame)
        self.widgets.setLayout(widgetsLay)
        layout.addWidget(self.widgets, 2, 2, 1, 8)

        self.str_AC.setEnabled(True)
        self.img_AC.setEnabled(True)
        self.del_AC.setEnabled(True)
        self.dpiSB.setEnabled(True)

        self.labelSizeXLE.textChanged.connect(self.changeEditSizeX)
        self.labelSizeYLE.textChanged.connect(self.changeEditSizeY)

        self.frame.setLayout(layout)


    def changDpi(self,value):
        """改变Dpi"""
        self.dpi = int(value)

    def keyPressEvent(self, event):  # 重写键盘监听事件
        # 监听 CTRL+C 组合键，实现复制数据到粘贴板
        if (event.key() == Qt.Key_C) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.copy()
        elif (event.key() == Qt.Key_V) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.paste()
        elif (event.key() == Qt.Key_S) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.saveModel()
        elif str(event.key()) == "16777221" or str(event.key()) == "16777220":  # 回车
            pass
        elif str(event.key()) == "16777223":  # delete
            self.deleteControls()
            pass
        else:
            # print(event.key(),QApplication.keyboardModifiers(),Qt.ControlModifier)
            super().keyPressEvent(event)

    def copy(self):
        """复制当前控件"""
        if not self.currentWidget:
            self.pastData = {}
            return None
        styleSheets = None
        widgetValue = self.currentWidget.getWidgetValue()
        value = widgetValue.get('value')
        if value == 0:
            styleSheets = self.currentWidget.getFontStyle()
        self.pastData = {'styleSheets': styleSheets, 'widgetValue': widgetValue}

    def paste(self):
        """粘贴控件"""
        if not self.pastData:
            return None
        styleSheets = self.pastData.get('styleSheets')
        widgetValue = self.pastData.get('widgetValue')
        if not widgetValue:
            return None
        if styleSheets:
            widgetValue.update(styleSheets)
        self.addWidget2(widgetValue,isCopy=True,styleSheets=styleSheets)

    def choiseAttrSetting(self, value):
        """选择属性设置界面"""
        self.attribute_stackedWidget.setCurrentIndex(value)

    def changeEditSizeX(self, text):
        """改变编辑区宽度"""
        x = self.labelSizeXLE.text()
        y = self.labelSizeYLE.text()
        if x and x.isdigit() and y and y.isdigit():
            x, y = int(x), int(y)
            self.editZone.setMaximumSize(round(x / 25.4 * self.dpiScreen), round(y / 25.4 * self.dpiScreen))
            self.editZone.setMinimumSize(round(x / 25.4 * self.dpiScreen), round(y / 25.4 * self.dpiScreen))

    def changeEditSizeY(self, text):
        """改变编辑区高度"""
        x = self.labelSizeXLE.text()
        y = self.labelSizeYLE.text()
        if x and x.isdigit() and y and y.isdigit():
            x, y = int(x), int(y)
            self.editZone.setMaximumSize(round(x / 25.4 * self.dpiScreen), round(y / 25.4 * self.dpiScreen))
            self.editZone.setMinimumSize(round(x / 25.4 * self.dpiScreen), round(y / 25.4 * self.dpiScreen))
            # self.editZone.move(20, 20)

    def changeTracingPoint(self, value):
        """改边描点位置，0：左上，1：左下，2，右上，3，右下"""
        if not self.currentWidget:
            return None
        if self.isChoiseCom:
            return None

        self.tracingPoint = value
        self.updateComPoint(self.currentWidget)

    def updateComPoint(self, currentWidget):
        """刷新组件坐标点"""
        if not currentWidget:
            return None

        self.isChoiseCom = True
        value = currentWidget.getWidgetValue()
        if value.get('width') is not None and value.get('height') is not None:
            comWidth, comHeight = round(value.get('width') / 25.4 * self.dpiScreen, 3), round(
                value.get('height') / 25.4 * self.dpiScreen, 3)
        else:
            comWidth = self.currentWidget.width()
            comHeight = self.currentWidget.height()

        xPoint = currentWidget.geometry().x()
        yPoint = currentWidget.geometry().y()
        if self.tracingPoint == 0:
            xPoint2, yPoint2 = xPoint, yPoint
        elif self.tracingPoint == 1:
            xPoint2, yPoint2 = xPoint, yPoint + comHeight
        elif self.tracingPoint == 2:
            xPoint2, yPoint2 = xPoint + comWidth, yPoint
        else:
            xPoint2, yPoint2 = xPoint + comWidth, yPoint + comHeight

        self.xLocationCB.setValue(round(xPoint2 / self.dpiScreen * 25.4, 1))
        self.yLocationCB.setValue(round(yPoint2 / self.dpiScreen * 25.4, 1))

        value.update(
            {'fixedX': round(xPoint2 * 25.4 / self.dpiScreen, 3), 'fixedY': round(yPoint2 * 25.4 / self.dpiScreen, 3),
             'tracingPoint': self.tracingPoint})
        currentWidget.updateWidgetValue(value)

        self.isChoiseCom = False

    def calculatePoint(self, currentWidget, xPoint, yPoint):
        """根据描点位置计算返回控件的坐标"""
        if not currentWidget:
            return None
        comWidth = self.currentWidget.width()
        comHeight = self.currentWidget.height()
        if self.tracingPoint == 0:
            xPoint2, yPoint2 = xPoint, yPoint
        elif self.tracingPoint == 1:
            xPoint2, yPoint2 = xPoint, yPoint - comHeight
        elif self.tracingPoint == 2:
            xPoint2, yPoint2 = xPoint - comWidth, yPoint
        else:
            xPoint2, yPoint2 = xPoint - comWidth, yPoint - comHeight
        return xPoint2, yPoint2

    def changeComponentSBValue(self, value):
        """组件size改变事件"""
        if self.isChoiseCom:
            return None
        if self.currentWidget and not self.changeSizeStatus:
            value = self.currentWidget.getWidgetValue()
            type = value.get('type')
            if type == 'img':
                imgType = value.get('imgType')
                if imgType == 'logo':
                    height = self.imgHeightSB.value()
                    width = self.imgWidthSB.value()
                elif imgType == 'barCode':
                    height = self.barHeightSB.value()
                    width = self.barWidthSB.value()
                elif imgType == 'qrCode':
                    height = self.qrHeightSB.value()
                    width = self.qrWidthSB.value()
            self.currentWidget.resize(round(width / 25.4 * self.dpiScreen), round(height / 25.4 * self.dpiScreen))
            # self.currentWidget.resize(width,height)
            value = self.currentWidget.getWidgetValue()
            value.update({'width': round(self.currentWidget.width() * 25.4 / self.dpiScreen, 3),
                          'height': round(self.currentWidget.height() * 25.4 / self.dpiScreen, 3)})
            # value.update({'width':round(width / 25.4 * self.dpiScreen,1),'height':round(height / 25.4 * self.dpiScreen,1)})
            self.currentWidget.updateWidgetValue(value)

            self.updateComPoint(self.currentWidget)

    def changeComponentPoint(self, value):
        """改变组件位置"""
        if self.isChoiseCom:
            return None
        if self.currentWidget and not self.moveStatus:
            points = self.calculatePoint(self.currentWidget, round(self.xLocationCB.value() / 25.4 * self.dpiScreen),
                                         round(self.yLocationCB.value() / 25.4 * self.dpiScreen))
            if not points:
                return None
            xPoint, yPoint = points[0], points[1]
            self.currentWidget.setGeometry(xPoint, yPoint, self.currentWidget.width(), self.currentWidget.height())
            value = self.currentWidget.getWidgetValue()
            value.update({'fixedX': round(xPoint * 25.4 / self.dpiScreen, 3),
                          'fixedY': round(yPoint * 25.4 / self.dpiScreen, 3)})

    def addWidget(self, value, styleSheets=None, widgetValue=None):
        """添加控件"""
        self.textEdit.setEnabled(True)

        if value == 0:  # 文本
            self.widgetID += 1
            textLabel = DraggableLabel('', self.editZone, self.choiseWidget, zoomFeedbackFunc=self.zoomFeedbackFuncs,
                                       positionChange=self.zoomMoveFuncs)
            textLabel.setObjectName(f'widget{self.widgetID}')
            textLabel.setGeometry(round(5 / 25.4 * self.dpiScreen), round(5 / 25.4 * self.dpiScreen), 100, 20)
            fonts = self.choiseFontTypeCB.currentText()
            fontSize = round(self.fontSizeSB.value() / 2.845 / 25.4 * self.dpiScreen)
            fontBold = True if self.choiseFontThicknessCB.currentIndex() == 1 else False
            if not styleSheets:
                styleSheets = {'font-size': fontSize, 'font-family': fonts, 'font-bold': fontBold}
            if not widgetValue:
                widgetValue = {'type': 'str', 'font-size': self.fontSizeSB.value(), 'font-family': fonts, 'value': 0,
                               'fixedX': 5.0, 'fixedY': 5.0, 'tracingPoint': self.tracingPoint}
            textLabel.updateWidgetValue(widgetValue)
            textLabel.updateFontStyle(styleSheets)

            textLabel.show()
            self.currentWidget = textLabel
            self.textEdit.setText('样本文本')
            # self.currentWidget.adjustSize()
        elif value == 1:  # 图片
            self.widgetID += 1
            imgLabel = DraggableImg(self.editZone, self.choiseWidget, positionChange=self.zoomMoveFuncs,
                                    sizeChange=self.changeComponentSize)
            imgLabel.setObjectName(f'widget{self.widgetID}')
            imgLabel.setGeometry(round(5 / 25.4 * self.dpiScreen), round(5 / 25.4 * self.dpiScreen),
                                 round(20 / 25.4 * self.dpiScreen), round(20 / 25.4 * self.dpiScreen))  # 20mm x 20mm
            if not widgetValue:
                widgetValue = {'type': 'img', 'imgType': 'logo', 'imgPath': None, 'value': 1, 'width': 20.0,
                               'height': 20.0, 'fixedX': 5.0, 'fixedY': 5.0, 'tracingPoint': self.tracingPoint}
            else:
                imgValue = widgetValue.get('imgValue')
                imgPath = widgetValue.get('imgPath')
                imgLabel.setText(imgPath)
                imgLabel.setImg(imgPath)

            imgLabel.setWidgetValue(widgetValue)
            imgLabel.show()
            # self.currentWidget = imgLabel
        elif value == 2:
            self.widgetID += 1
            lineLength = self.lineLengthSB.value()
            lineSize = self.lineSizeSB.value()
            if not widgetValue:
                widgetValue = {'type': 'Hline', 'lineSize': lineSize, 'backGroundColor': 'black', 'value': 2,
                               'lineLength': lineLength, 'fixedX': 5.0, 'fixedY': 5.0,
                               'tracingPoint': self.tracingPoint}
            else:
                lineLength = widgetValue.get('lineLength')
                lineSize = widgetValue.get('lineSize')

            line = DraggableLine(self.editZone, self.choiseWidget, zoomFeedbackFunc=self.lineFeedbackFuncs,
                                 positionChange=self.zoomMoveFuncs, sizeChange=self.changeComponentSize)
            line.setObjectName(f'Hline{self.widgetID}')
            line.setGeometry(round(5 / 25.4 * self.dpiScreen), round(5 / 25.4 * self.dpiScreen),
                             round(lineLength / 25.4 * self.dpiScreen), round(lineSize / 25.4 * self.dpiScreen))
            line.setWidgetValue(widgetValue)
            line.show()
            # self.currentWidget = line
        elif value == 3:
            self.widgetID += 1
            lineLength = self.lineLengthSB.value()
            lineSize = self.lineSizeSB.value()
            if not widgetValue:
                widgetValue = {'type': 'Vline', 'lineSize': lineSize, 'backGroundColor': 'black', 'value': 3,
                               'lineLength': lineLength, 'fixedX': 5.0, 'fixedY': 5.0,
                               'tracingPoint': self.tracingPoint}
            else:
                lineLength = widgetValue.get('lineLength')
            line = DraggableLine(self.editZone, self.choiseWidget, orientation='Vertical',
                                 zoomFeedbackFunc=self.lineFeedbackFuncs, positionChange=self.zoomMoveFuncs,
                                 sizeChange=self.changeComponentSize)
            line.setObjectName(f'Vline{self.widgetID}')
            line.setGeometry(round(5 / 25.4 * self.dpiScreen), round(5 / 25.4 * self.dpiScreen),
                             round(lineSize / 25.4 * self.dpiScreen), round(lineLength / 25.4 * self.dpiScreen))
            line.setWidgetValue(widgetValue)
            line.show()
            # self.currentWidget = line
        elif value == 4:
            self.widgetID += 1

            barCodeLabel = DraggableImg(self.editZone, self.choiseWidget, positionChange=self.zoomMoveFuncs,
                                        sizeChange=self.changeComponentSize)
            barCodeLabel.setObjectName(f'widget{self.widgetID}')
            barCodeLabel.setGeometry(round(5 / 25.4 * self.dpiScreen), round(5 / 25.4 * self.dpiScreen),
                                     round(20 / 25.4 * self.dpiScreen), round(20 / 25.4 * self.dpiScreen))
            if not widgetValue:
                widgetValue = {'type': 'img', 'imgType': 'barCode', 'imgPath': None, 'value': 4, 'width': 20.0,
                               'height': 20.0, 'fixedX': 5.0, 'fixedY': 5.0, 'tracingPoint': self.tracingPoint}
            else:
                imgPath = widgetValue.get('imgPath')
                barCodeLabel.setText(imgPath)
                barCodeLabel.setImg(imgPath)

            barCodeLabel.setWidgetValue(widgetValue)
            barCodeLabel.show()
        elif value == 5:
            self.widgetID += 1
            qrCodeLabel = DraggableImg(self.editZone, self.choiseWidget, positionChange=self.zoomMoveFuncs,
                                       sizeChange=self.changeComponentSize)
            qrCodeLabel.setObjectName(f'widget{self.widgetID}')
            qrCodeLabel.setGeometry(round(5 / 25.4 * self.dpiScreen), round(5 / 25.4 * self.dpiScreen),
                                    round(20 / 25.4 * self.dpiScreen), round(20 / 25.4 * self.dpiScreen))
            if not widgetValue:
                widgetValue = {'type': 'img', 'imgType': 'qrCode', 'imgPath': None, 'value': 5, 'width': 20.0,
                               'height': 20.0, 'fixedX': 5.0, 'fixedY': 5.0, 'tracingPoint': self.tracingPoint}
            else:
                imgPath = widgetValue.get('imgPath')
                qrCodeLabel.setText(imgPath)
                qrCodeLabel.setImg(imgPath)

            qrCodeLabel.setWidgetValue(widgetValue)
            qrCodeLabel.show()

        self.setFocus()

    def addWidget2(self, widgetValue, isCopy=False, styleSheets=None):
        """根据已有值添加控件"""
        types = widgetValue.get('type')
        fixedX = widgetValue.get('fixedX')
        fixedY = widgetValue.get('fixedY')
        tracingPoint = widgetValue.get('tracingPoint', 0)
        if types == 'img':
            imgH = widgetValue.get('height')
            imgW = widgetValue.get('width')
            path = widgetValue.get('imgPath')
            imgType = widgetValue.get('imgType')
            if imgType == 'logo':
                # 创建图片
                self.widgetID += 1
                imgLabel = DraggableImg(self.editZone, self.choiseWidget, positionChange=self.zoomMoveFuncs,
                                        sizeChange=self.changeComponentSize)
                imgLabel.setObjectName(f'widget{self.widgetID}')
                imgLabel.setGeometry(round(fixedX / 25.4 * self.dpiScreen), round(fixedY / 25.4 * self.dpiScreen),
                                     round(imgW / 25.4 * self.dpiScreen), round(imgH / 25.4 * self.dpiScreen))
                imgLabel.show()
                self.currentWidget = imgLabel
                widgetValue.update({'value': 1, 'imgPath': path})
                imgLabel.updateWidgetValue(widgetValue)
                # 设置属性
                self.choiseAttrSetting(1)
                self.locationPointCB.setCurrentIndex(tracingPoint)
                self.imgHeightSB.setValue(round(imgH, 1))
                self.imgWidthSB.setValue(round(imgW, 1))
                self.imgPathLE.setText(path)
                self.xLocationCB.setValue(round(fixedX, 1))
                self.yLocationCB.setValue(round(fixedY, 1))
                imgLabel.setImg(path)
            elif imgType == 'barCode':
                data = widgetValue.get('data')
                textDistance = widgetValue.get('textDistance')
                writeText = 0 if widgetValue.get('writeText', False) else 1
                # 创建图片
                self.widgetID += 1
                barCodeLabel = DraggableImg(self.editZone, self.choiseWidget, positionChange=self.zoomMoveFuncs,
                                            sizeChange=self.changeComponentSize)
                barCodeLabel.setObjectName(f'widget{self.widgetID}')
                barCodeLabel.setGeometry(round(fixedX / 25.4 * self.dpiScreen), round(fixedY / 25.4 * self.dpiScreen),
                                         round(imgW / 25.4 * self.dpiScreen), round(imgH / 25.4 * self.dpiScreen))
                barCodeLabel.show()
                self.currentWidget = barCodeLabel
                widgetValue.update({'value': 4, 'imgPath': path, 'width': imgW, 'height': imgH})
                barCodeLabel.updateWidgetValue(widgetValue)
                # 设置属性
                self.choiseAttrSetting(3)
                self.locationPointCB.setCurrentIndex(tracingPoint)
                self.barCodeValueLE.setText(data)
                self.barCodeShowTextCB.setCurrentIndex(writeText)
                self.barCodeTextSpacingCB.setValue(textDistance)
                self.barHeightSB.setValue(round(imgH, 1))
                self.barWidthSB.setValue(round(imgW, 1))
                self.xLocationCB.setValue(round(fixedX, 1))
                self.yLocationCB.setValue(round(fixedY, 1))
            elif imgType == 'qrCode':
                data = widgetValue.get('data')
                # 创建图片
                self.widgetID += 1
                qrCodeLabel = DraggableImg(self.editZone, self.choiseWidget, positionChange=self.zoomMoveFuncs,
                                           sizeChange=self.changeComponentSize)
                qrCodeLabel.setObjectName(f'widget{self.widgetID}')
                qrCodeLabel.setGeometry(round(fixedX / 25.4 * self.dpiScreen), round(fixedY / 25.4 * self.dpiScreen),
                                        round(imgW / 25.4 * self.dpiScreen), round(imgH / 25.4 * self.dpiScreen))
                qrCodeLabel.show()
                self.currentWidget = qrCodeLabel
                widgetValue.update({'value': 5, 'imgPath': path, 'width': imgW, 'height': imgH})
                qrCodeLabel.updateWidgetValue(widgetValue)
                # 设置属性
                self.choiseAttrSetting(4)
                self.locationPointCB.setCurrentIndex(tracingPoint)
                self.qrCodeValueLE.setText(data)
                self.qrHeightSB.setValue(round(imgH, 1))
                self.qrWidthSB.setValue(round(imgW, 1))
                self.xLocationCB.setValue(round(fixedX, 1))
                self.yLocationCB.setValue(round(fixedY, 1))
        elif types == 'str':
            data = widgetValue.get('data')
            font = widgetValue.get('font-family')
            fontBold = 1 if widgetValue.get('font-bold', False) else 0
            fontSize = widgetValue.get('font-size')
            fontSpacing = widgetValue.get('font-spacing', 100)
            textHeight = widgetValue.get('textHeight') if not isCopy else self.currentWidget.height()
            textWidth = widgetValue.get('textWidth') if not isCopy else self.currentWidget.width()

            # 创建文本
            self.widgetID += 1
            textLabel = DraggableLabel('', self.editZone, self.choiseWidget, zoomFeedbackFunc=self.zoomFeedbackFuncs,
                                       positionChange=self.zoomMoveFuncs)
            textLabel.setObjectName(f'widget{self.widgetID}')
            textLabel.setGeometry(round(fixedX / 25.4 * self.dpiScreen), round(fixedY / 25.4 * self.dpiScreen),
                                  textWidth, textHeight)
            textLabel.show()
            self.currentWidget = textLabel
            textLabel.updateWidgetValue(widgetValue)
            font_Bold = True if widgetValue.get('font-bold') else False
            if isCopy and styleSheets:
                textLabel.updateFontStyle(styleSheets)
            else:
                textLabel.updateFontStyle(
                    {'value': 0, 'font-size': round(widgetValue.get('font-size') / 2.845 / 25.4 * self.dpiScreen),
                     'font-spacing': widgetValue.get('font-spacing'),
                     'font-family': widgetValue.get('font-family'), 'font-bold': font_Bold})
            # 设置属性
            self.choiseAttrSetting(0)
            self.locationPointCB.setCurrentIndex(tracingPoint)
            self.textEdit.setText(data)
            self.fontSizeSB.setValue(fontSize)
            self.choiseFontTypeCB.setCurrentText(font)
            self.choiseFontThicknessCB.setCurrentIndex(fontBold)
            self.compressionRatioSB.setValue(fontSpacing)
            self.xLocationCB.setValue(round(fixedX, 1))
            self.yLocationCB.setValue(round(fixedY, 1))
        elif types == 'Hline':
            backGroundColor = widgetValue.get('backGroundColor')
            lineLength = widgetValue.get('lineLength')
            lineSize = widgetValue.get('lineSize')
            # 创建横线
            self.widgetID += 1
            line = DraggableLine(self.editZone, self.choiseWidget, zoomFeedbackFunc=self.lineFeedbackFuncs,
                                 positionChange=self.zoomMoveFuncs, sizeChange=self.changeComponentSize)
            line.setObjectName(f'Hline{self.widgetID}')
            line.setGeometry(round(fixedX / 25.4 * self.dpiScreen), round(fixedY / 25.4 * self.dpiScreen),
                             round(lineLength / 25.4 * self.dpiScreen), round(lineSize / 25.4 * self.dpiScreen))
            line.show()
            self.currentWidget = line
            widgetValue.update({'value': 2})
            line.updateWidgetValue(widgetValue)
            # 设置属性
            self.choiseAttrSetting(2)
            self.locationPointCB.setCurrentIndex(tracingPoint)
            self.lineLengthSB.setValue(round(lineLength, 1))
            self.lineSizeSB.setValue(round(lineSize, 1))
            self.xLocationCB.setValue(round(fixedX, 1))
            self.yLocationCB.setValue(round(fixedY, 1))
        elif types == 'Vline':
            backGroundColor = widgetValue.get('backGroundColor')
            lineLength = widgetValue.get('lineLength')
            lineSize = widgetValue.get('lineSize')
            # 创建横线
            self.widgetID += 1
            line = DraggableLine(self.editZone, self.choiseWidget, orientation='Vertical',
                                 zoomFeedbackFunc=self.lineFeedbackFuncs, positionChange=self.zoomMoveFuncs,
                                 sizeChange=self.changeComponentSize)
            line.setObjectName(f'Vline{self.widgetID}')
            line.setGeometry(round(fixedX / 25.4 * self.dpiScreen), round(fixedY / 25.4 * self.dpiScreen),
                             round(lineSize / 25.4 * self.dpiScreen), round(lineLength / 25.4 * self.dpiScreen))
            line.show()
            self.currentWidget = line
            widgetValue.update({'value': 3})
            line.updateWidgetValue(widgetValue)
            # 设置属性
            self.choiseAttrSetting(2)
            self.locationPointCB.setCurrentIndex(tracingPoint)
            self.lineLengthSB.setValue(round(lineLength, 1))
            self.lineSizeSB.setValue(round(lineSize, 1))
            self.xLocationCB.setValue(round(fixedX, 1))
            self.yLocationCB.setValue(round(fixedY, 1))

    def replayWidget(self, tempValue):
        """重新编辑控件"""
        if not tempValue:
            return None
        tmpDatas = tempValue.get('tmpDatas')
        templateID = tempValue.get('templateID')
        templateName = tempValue.get('templateName')
        self.modelName.setText(templateName)
        for widgetValue in tmpDatas:
            if not widgetValue:
                continue
            self.addWidget2(widgetValue)

    def changeFontSpacing(self, value):
        """改变文本间距"""
        if self.isChoiseCom:
            return None
        if self.currentWidget:
            self.currentWidget.updateWidgetValue({'font-spacing': int(value)})
            self.currentWidget.updateFontStyle({'font-spacing': value})
            self.updateComPoint(self.currentWidget)

    def changeLineThickness(self, value):
        """改变线条粗细"""
        if self.isChoiseCom:
            return None
        if self.currentWidget:
            self.currentWidget.updateWidgetValue({'lineSize': value})
            self.currentWidget.updateLineThickness(round(value / 25.4 * self.dpiScreen))
            self.updateComPoint(self.currentWidget)

    def changeLineLength(self, value):
        """改变线条长度"""
        if self.isChoiseCom:
            return None
        if self.currentWidget and not self.changeSizeStatus:
            comValue = self.currentWidget.getWidgetValue()
            type = comValue.get('type')
            if type == 'Hline':
                self.currentWidget.resize(round(value / 25.4 * self.dpiScreen), self.currentWidget.height())
            else:
                self.currentWidget.resize(self.currentWidget.width(), round(value / 25.4 * self.dpiScreen))
            self.currentWidget.updateWidgetValue({'lineLength': value})
            # self.currentWidget.resize()
            self.updateComPoint(self.currentWidget)

    def lineFeedbackFuncs(self, value):
        """缩放反馈"""
        # print(value)
        pass

    def zoomFeedbackFuncs(self, value):
        """控件缩放反馈"""
        if not self.currentWidget:
            return None
        self.fontSizeSB.setValue(value)
        self.updateComPoint(self.currentWidget)

    def zoomMoveFuncs(self, datas):
        """控件移动反馈"""
        if not self.currentWidget:
            return None

        self.updateComPoint(self.currentWidget)

    def changeComponentSize(self, datas):
        """改变组件大小反馈"""
        width, height = datas[0], datas[1]
        width2 = round(width / self.dpiScreen * 25.4, 1) if width else 0
        height2 = round(height / self.dpiScreen * 25.4, 1) if height else 0
        if self.currentWidget:
            value = self.currentWidget.getWidgetValue()
            self.changeSizeStatus = True
            type = self.currentWidget.getWidgetValue().get('type')
            if type == 'img':
                self.imgHeightSB.setValue(height2)
                self.imgWidthSB.setValue(width2)
            elif type == 'barCode':
                self.barHeightSB.setValue(height2)
                self.barWidthSB.setValue(width2)
            elif type == 'Hline':
                self.lineLengthSB.setValue(width2)
                value.update({'lineLength': width2})
            elif type == 'Vline':
                self.lineLengthSB.setValue(height2)
                value.update({'lineLength': height2})
            else:
                self.qrHeightSB.setValue(height2)
                self.qrWidthSB.setValue(width2)
            if width:
                value.update({'width': round(width * 25.4 / self.dpiScreen, 3)})
            if height:
                value.update({'height': round(height * 25.4 / self.dpiScreen, 3)})
            self.currentWidget.updateWidgetValue(value)
            self.changeSizeStatus = False

            self.updateComPoint(self.currentWidget)

    def choiseWidget(self, obj):
        """选择控件"""
        self.isChoiseCom = True
        self.currentWidget = obj
        self.editZone.setFocus()
        value = obj.getWidgetValue()
        if value:
            type = value.get('type')
            tracingPoint = value.get('tracingPoint')
            self.locationPointCB.setCurrentIndex(tracingPoint)
            fixedX = value.get('fixedX')
            fixedY = value.get('fixedY')
            self.xLocationCB.setValue(round(fixedX, 1))
            self.yLocationCB.setValue(round(fixedY, 1))
            varValue = value.get('varValue')
            if type == 'str':
                self.choiseAttrSetting(0)
                fontSize = value.get('font-size')
                fontFamily = value.get('font-family')
                textValue = value.get('textValue', '')
                fontBold = value.get('font-bold', False)
                fontSpacing = value.get('font-spacing', 100.0)
                if fontSize:
                    self.fontSizeSB.setValue(fontSize)
                if fontBold:
                    self.choiseFontThicknessCB.setCurrentIndex(1)
                else:
                    self.choiseFontThicknessCB.setCurrentIndex(0)
                if fontSpacing:
                    self.compressionRatioSB.setValue(int(fontSpacing))
                self.choiseFontTypeCB.setCurrentText(fontFamily)
                self.textEdit.setText(textValue)
            elif type == 'img':
                imgType = value.get('imgType')
                if imgType == 'logo':
                    self.choiseAttrSetting(1)
                    imgPath = value.get('imgPath', '')
                    width, height = value.get('width', 0), value.get('height', 0)
                    width2, height2 = round(width, 1), round(height, 1)
                    self.imgPathLE.setText(imgPath)
                    self.imgWidthSB.setValue(width2)
                    self.imgHeightSB.setValue(height2)
                elif imgType == 'barCode':
                    self.choiseAttrSetting(3)
                    imgValue = value.get('data', '')
                    width, height = value.get('width', 0), value.get('height', 0)
                    width2, height2 = round(width, 1), round(height, 1)
                    writeText = value.get('writeText', True)
                    textDistance = value.get('textDistance', 1)
                    if writeText:
                        self.barCodeShowTextCB.setCurrentIndex(0)
                    else:
                        self.barCodeShowTextCB.setCurrentIndex(1)
                    self.barCodeTextSpacingCB.setValue(textDistance)
                    self.barCodeValueLE.setText(imgValue)
                    self.barWidthSB.setValue(width2)
                    self.barHeightSB.setValue(height2)
                elif imgType == 'qrCode':
                    self.choiseAttrSetting(4)
                    imgValue = value.get('data', '')
                    width, height = value.get('width', 0), value.get('height', 0)
                    width2, height2 = round(width, 1), round(height, 1)
                    self.qrCodeValueLE.setText(imgValue)
                    self.qrWidthSB.setValue(width2)
                    self.qrHeightSB.setValue(height2)
            elif type == 'Hline' or type == 'Vline':
                self.choiseAttrSetting(2)
                lineSize = value.get('lineSize')
                lineLength = value.get('lineLength')
                if lineSize:
                    self.lineSizeSB.setValue(round(lineSize, 1))
                if lineLength:
                    self.lineLengthSB.setValue(round(lineLength, 1))
        self.isChoiseCom = False

    def choiseImgPath(self):
        """选择图片路径"""
        if not self.currentWidget:
            return None
        filePath = getOpenfileName()
        if filePath:
            self.imgPathLE.setText(filePath)
            self.currentWidget.setImg(filePath)
            self.currentWidget.updateWidgetValue({'imgType': 'logo', 'imgPath': filePath, 'data': None})

    def changeBarCodeImg(self):
        """更改条形码显示文本"""
        if self.isChoiseCom:
            return None
        if not self.currentWidget:
            return None
        text = self.barCodeValueLE.toPlainText()
        if not text:
            return None
        index = self.barCodeShowTextCB.currentIndex()
        write_text = True if index == 0 else False
        text_distance = self.barCodeTextSpacingCB.value()
        barcode_type = self.barCodeStyleCB.currentText()
        self.currentWidget.updateWidgetValue({'imgType': 'barCode'})
        path = os.path.join(os.getcwd(), f'./setting/img/editMode/barCode')
        strToBarCode(text, path, barcode_type=barcode_type, write_text=write_text, text_distance=text_distance,
                     quiet_zone=0)

        self.currentWidget.setImg(path)
        self.currentWidget.updateWidgetValue({'data': text, 'writeText': write_text, 'textDistance': text_distance})

    def changeQRCodeImg(self):
        """更改二维码显示文本"""
        if self.isChoiseCom:
            return None
        if not self.currentWidget:
            return None
        text = self.qrCodeValueLE.toPlainText()
        if not text:
            return None
        self.currentWidget.updateWidgetValue({'imgType': 'qrCode'})
        path = os.path.join(os.getcwd(), f'./setting/img/editMode/qrCode')
        strToQRCode(text, path, border=0)

        self.currentWidget.setImg(path)
        self.currentWidget.updateWidgetValue({'data': text})

    def changeFontSize(self, value):
        """改变文本大小"""
        if self.isChoiseCom:
            return None
        if self.currentWidget and not self.fontChangeStatus:
            fontSizePx = round(value / 2.845 / 25.4 * self.dpiScreen)
            self.currentWidget.updateFontStyle({'font-size': fontSizePx})
            self.currentWidget.updateWidgetValue({'font-size': value})
            # self.currentWidget.adjustSize()

            self.updateComPoint(self.currentWidget)

    def changeLabelValue(self):
        """更改文本标签显示"""
        if self.isChoiseCom:
            return None
        if not self.currentWidget or self.fontChangeStatus:
            return None
        text = self.textEdit.toPlainText().strip()
        fontSize = round(self.fontSizeSB.value() / 2.845 / 25.4 * self.dpiScreen)
        styleSheets = {'font-size': fontSize}
        fonts = self.choiseFontTypeCB.currentText()
        styleSheets.update({'font-family': fonts})
        self.currentWidget.updateFontStyle(styleSheets)
        self.currentWidget.updateWidgetValue(
            {'type': 'str', 'font-size': self.fontSizeSB.value(), 'font-family': fonts, 'textValue': text})
        self.currentWidget.setText(text)
        self.currentWidget.adjustSize()

        self.updateComPoint(self.currentWidget)

    def changeFontType(self, text):
        """改变字体"""
        if self.isChoiseCom:
            return None
        if self.currentWidget and not self.fontChangeStatus:
            self.currentWidget.updateFontStyle({'font-family': text})
            self.currentWidget.updateWidgetValue({'font-family': text})

            self.updateComPoint(self.currentWidget)

    def changeFontThickness(self, index):
        """字体加粗"""
        if self.isChoiseCom:
            return None
        if self.currentWidget and not self.fontChangeStatus:
            if index == 0:
                self.currentWidget.updateFontStyle({'font-bold': False})
                self.currentWidget.updateWidgetValue({'font-bold': False})
            elif index == 1:
                self.currentWidget.updateFontStyle({'font-bold': True})
                self.currentWidget.updateWidgetValue({'font-bold': True})

            self.updateComPoint(self.currentWidget)

    def saveModel(self,isPreview=False):
        """保存模板数据,isPreview：是否预览图像"""
        tmpDatas = []
        dpi = self.dpiSB.value()
        widths = float(self.labelSizeXLE.text())
        heights = float(self.labelSizeYLE.text())
        qrImgNum = 0
        barCodeImgNum = 0
        for con in self.editZone.children():
            conValue = con.getWidgetValue()
            comWidth = con.width()
            comHeight = con.height()
            tracingPoint = conValue.get('tracingPoint', 0)
            type = conValue.get('type')
            fixedX = conValue.get('fixedX')
            fixedY = conValue.get('fixedY')
            if type == 'str':
                text = conValue.get('textValue')
                fontBold = conValue.get('font-bold')
                fontSize = conValue.get('font-size')
                fontSpacing = conValue.get('font-spacing', 100.0)
                fonts = conValue.get('font-family')
                tmpDatas.append({'type': 'str', 'data': text, 'font-family': fonts, 'font-size': fontSize,
                                 'textWidth': comWidth, 'textHeight': comHeight,
                                 'fixedX': fixedX, 'fixedY': fixedY, 'font-bold': fontBold, 'font-spacing': fontSpacing,
                                 'tracingPoint': tracingPoint})
            elif type == 'img':
                textValue = conValue.get('data')
                imgType = conValue.get('imgType')
                imgName = None
                path = None
                if imgType == 'barCode':
                    barCodeImgNum += 1
                    path = f'./setting/img/editMode/barCode{barCodeImgNum}.png'
                elif imgType == 'qrCode':
                    qrImgNum += 1
                    path = f'./setting/img/editMode/qrCode{qrImgNum}.png'
                elif imgType == "logo":
                    path = conValue.get('imgPath')
                    if not path:
                        self.messages.messageboxSignal.emit('图片标签路径不能为空！')
                        return None

                imgW = conValue.get('width')
                imgH = conValue.get('height')
                writeText = conValue.get('writeText')
                textDistance = conValue.get('textDistance')
                tmpDatas.append(
                    {'type': 'img', 'data': textValue, 'fixedX': fixedX, 'fixedY': fixedY, "imgType": imgType,
                     'imgName': imgName, "imgPath": path, "width": imgW, "height": imgH, 'writeText': writeText,
                     'textDistance': textDistance,
                     'tracingPoint': tracingPoint})
            elif type == 'Hline':
                backGroundColor = conValue.get('backGroundColor')
                lineSize = conValue.get('lineSize')
                lineLength = conValue.get('lineLength')
                tmpDatas.append(
                    {'type': type, 'lineSize': lineSize, 'lineLength': lineLength, 'fixedX': fixedX, 'fixedY': fixedY,
                     'backGroundColor': backGroundColor, 'tracingPoint': tracingPoint})
            elif type == 'Vline':
                backGroundColor = conValue.get('backGroundColor')
                lineSize = conValue.get('lineSize')
                lineLength = conValue.get('lineLength')
                tmpDatas.append(
                    {'type': type, 'lineSize': lineSize, 'lineLength': lineLength, 'fixedX': fixedX, 'fixedY': fixedY,
                     'backGroundColor': backGroundColor, 'tracingPoint': tracingPoint})
        if not tmpDatas:
            self.messages.messageboxSignal.emit('当前模板编辑区为空！')
            return None
        self.imgSvaeDatas = {'width':round(widths/25.4*self.dpiScreen), 'height':round(heights/25.4*self.dpiScreen),'dpiScreen':self.dpiScreen,'tmpDatas':tmpDatas}
        if isPreview:
            return self.imgSvaeDatas

        #选择路径保存
        savePath = setOpenfileName()
        if savePath:
            pix = laberDraw(tmpDatas, width=round(widths/25.4*self.dpiScreen), height=round(heights/25.4*self.dpiScreen),dpiScreen=self.dpiScreen,save_img=savePath)
            if pix:
                self.messages.messageboxSignal.emit('已保存！')

    def previewModel(self):
        """预览图像"""
        imgSvaeDatas = self.saveModel(isPreview=True)
        if not imgSvaeDatas:
            return None
        laberDraw2(imgSvaeDatas)

    def showMsgBox(self, msg):
        dialog = QDialog()
        QMessageBox.warning(dialog, '提示', msg)

    def deleteControls(self):
        """删除控件"""
        if self.currentWidget:
            self.currentWidget.deleteLater()
            self.currentWidget = None
            self.textEdit.setText('')

    def forceOut(self):
        """用户登录过期，强制退出"""
        sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainTK = laberModeWindows()
    mainTK.show()
    sys.exit(app.exec_())