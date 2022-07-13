# coding:utf-8
from PyQt5.QtWidgets import  QWidget, QApplication,QPushButton,QComboBox,QLabel,QLineEdit,QTableWidget,QVBoxLayout,QHBoxLayout,QCheckBox,\
    QListWidget,QListWidgetItem,QScrollBar,QToolTip,QMessageBox,QStyleOption,QStyle,QFrame
from PyQt5.QtGui import QCursor,QPixmap,QPixmapCache,QPainter,QFont
from PyQt5.QtCore import  Qt,pyqtSignal,QRect,QThread,QPoint
import sys
import re
import traceback

class ComboCheckBox(QComboBox):
    def __init__(self, items: list,separator=';'):
        """initial function:param items: the items of the list"""
        super(ComboCheckBox, self).__init__()
        self.items = ["全选"] + items  # items list
        self.box_list = []  # selected items
        self.text = QLineEdit()  # use to selected items
        self.state = 0  # use to record state
        self.separator = separator
        self.isAll = False

        q = QListWidget()
        for i in range(len(self.items)):
            self.box_list.append(QCheckBox())
            self.box_list[i].setText(self.items[i])
            item = QListWidgetItem(q)
            q.setItemWidget(item, self.box_list[i])
            if i == 0:
                 self.box_list[i].stateChanged.connect(self.all_selected)
            else:
                self.box_list[i].stateChanged.connect(self.show_selected)

        #q.setStyleSheet("font-size: 20px; font-weight: bold; height: 40px; margin-left: 5px")
        #self.setStyleSheet("width: 300px; height: 50px; font-size: 21px; font-weight: bold")
        self.text.setReadOnly(True)
        self.setLineEdit(self.text)
        self.setModel(q.model())
        self.setView(q)

    def setItems(self,items):
        self.state = 0
        q = QListWidget()
        self.items = items = ["全选"] + items
        self.box_list = []
        for i in range(len(items)):
            self.box_list.append(QCheckBox())
            self.box_list[i].setText(items[i])
            item = QListWidgetItem(q)
            q.setItemWidget(item, self.box_list[i])
            if i == 0:
                self.box_list[i].stateChanged.connect(self.all_selected)
            else:
                self.box_list[i].stateChanged.connect(self.show_selected)

        self.text.setText('')
        self.setLineEdit(self.text)
        self.setModel(q.model())
        self.setView(q)

    def all_selected(self):
        """
        decide whether to check all
         :return:
        """
        self.isAll = True
        if self.state == 0:
            self.state = 1
            for i in range(1, len(self.items)):
                self.box_list[i].setChecked(True)

            self.text.clear()
            ret = f'{self.separator}'.join(self.get_selected())
            self.text.setText(ret)
        else:
            self.state = 0
            for i in range(1, len(self.items)):
                self.box_list[i].setChecked(False)
            self.text.clear()

        self.isAll = False

    def get_selected(self) -> list:
         """
         get selected items
         :return:
         """
         ret = []
         for i in range(1, len(self.items)):
            if self.box_list[i].isChecked():
                ret.append(self.box_list[i].text())
         return ret

    def show_selected(self):
         """
         show selected items
         :return:
         """
         if self.isAll:
             return None

         self.text.clear()
         ret = f'{self.separator}'.join(self.get_selected())
         self.text.setText(ret)

class MyTableWidget(QTableWidget):
    """自定义的QTableWidget,使用ToolTip提示用户当前单元格内的详细内容
        status:是否显示提示信息
    """
    update_table_tooltip_signal = pyqtSignal(object)

    def __init__(self, row, col,status=False):
        super(MyTableWidget, self).__init__()
        self.setRowCount(row)
        self.setColumnCount(col)
        if status:
            self.init_table()

    def init_table(self):
        self.vertical_scrollbar = QScrollBar()
        self.horizon_scrollbar = QScrollBar()
        self.setVerticalScrollBar(self.vertical_scrollbar)
        self.setHorizontalScrollBar(self.horizon_scrollbar)
        self.init_row = 0
        self.init_col = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.tool_tip = ""
        self.title_row_height = 25

        self.cellClicked.connect(self.cellClick)
        self.install_eventFilter()

    # 为TableWidget安装事件过滤器
    def install_eventFilter(self):
        self.installEventFilter(self)
        self.setMouseTracking(True)

    def cellClick(self,row,column):
        item = self.item(row, column)
        if item != None:
            self.tool_tip = item.text()
        else:
            self.tool_tip = ""
            return None
        if not self.mouse_x or not self.mouse_y:
            return None

        # 设置提示气泡显示范围矩形框,当鼠标离开该区域则ToolTip消失
        rect = QRect(self.mouse_x, self.mouse_y, 30, 10)  # QRect(x,y,width,height)
        # 设置QSS样式
        self.setStyleSheet(
            """QToolTip{border:10px;
               border-top-left-radius:5px;
               border-top-right-radius:5px;
               border-bottom-left-radius:5px;
               border-bottom-right-radius:5px;
               background:#4F4F4F;
               color:#00BFFF;
               font-size:18px;
               font-family:"微软雅黑";
            }""")
        QApplication.processEvents()
        # 在指定位置展示ToolTip
        QToolTip.showText(QCursor.pos(), self.tool_tip, self, rect)

    def mouseMoveEvent(self, event):
        s = event.windowPos()
        self.mouse_x = s.x()
        self.mouse_y = s.y()

    def addRow(self,addLineNums=1):
        """添加行"""
        rows = self.rowCount()
        for addLineNum in range(addLineNums):
            self.insertRow(rows)
            self.setFocus()
            self.setCurrentCell(rows, 0)
            rows += 1

class MyTableWidget2(QWidget):
    """带分页的TableWidget
        status:是否显示提示信息
        changePageFunc：页码改变时传递页码的函数
    """
    control_signal = pyqtSignal(list)
    update_table_tooltip_signal = pyqtSignal(object)

    def __init__(self, row, col,status=False,changePageFunc=None):
        super(MyTableWidget2, self).__init__()
        # print(args)
        self.row = row
        self.col = col
        self.status = status
        self.changePageFunc = changePageFunc
        self.__init_ui()

    def __init_ui(self):
        style_sheet = """
            QTableWidget {
                border: none;
                background-color:rgb(240,240,240)
            }
            QPushButton{
                max-width: 18ex;
                max-height: 6ex;
                font-size: 11px;
            }
            QLineEdit{
                max-width: 30px
            }
        """
        self.table = MyTableWidget(self.row, self.col,self.status)
        #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应宽度
        self.control_signal.connect(self.inventoryInfo_page_controller)

        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.table)
        self.setLayout(self.__layout)
        #self.setStyleSheet(style_sheet)

    def setPageController(self, page):
        """自定义页码控制器"""
        control_layout = QHBoxLayout()
        homePage = QPushButton("首页")
        prePage = QPushButton("<上一页")
        self.curPage = QLabel("1")
        nextPage = QPushButton("下一页>")
        finalPage = QPushButton("尾页")
        self.totalPage = QLabel("共" + str(page) + "页")
        skipLable_0 = QLabel("跳到")
        self.skipPage = QLineEdit()
        skipLabel_1 = QLabel("页")
        confirmSkip = QPushButton("确定")
        homePage.clicked.connect(self.__home_page)
        prePage.clicked.connect(self.__pre_page)
        nextPage.clicked.connect(self.__next_page)
        finalPage.clicked.connect(self.__final_page)
        confirmSkip.clicked.connect(self.__confirm_skip)
        control_layout.addStretch(1)
        control_layout.addWidget(homePage)
        control_layout.addWidget(prePage)
        control_layout.addWidget(self.curPage)
        control_layout.addWidget(nextPage)
        control_layout.addWidget(finalPage)
        control_layout.addWidget(self.totalPage)
        control_layout.addWidget(skipLable_0)
        control_layout.addWidget(self.skipPage)
        control_layout.addWidget(skipLabel_1)
        control_layout.addWidget(confirmSkip)
        control_layout.addStretch(1)
        self.__layout.addLayout(control_layout)

    def __home_page(self):
        """点击首页信号"""
        self.control_signal.emit(["home", self.curPage.text()])

    def __pre_page(self):
        """点击上一页信号"""
        self.control_signal.emit(["pre", self.curPage.text()])

    def __next_page(self):
        """点击下一页信号"""
        self.control_signal.emit(["next", self.curPage.text()])

    def __final_page(self):
        """尾页点击信号"""
        self.control_signal.emit(["final", self.curPage.text()])

    def __confirm_skip(self):
        """跳转页码确定"""
        if self.skipPage.text() and self.skipPage.text().isdigit():
            self.control_signal.emit(["confirm", self.skipPage.text()])
        else:
            QMessageBox.information(self, "提示", "跳转页码请输入数值", QMessageBox.Yes)

    def showTotalPage(self):
        """返回当前总页数"""
        return int(self.totalPage.text()[1:-1])

    def setPageCountNum(self,num):
        """设置总页数"""
        self.totalPage.setText("共" + str(num) + "页")

    def setCurrentPageNum(self,num):
        """设置当前页数"""
        self.curPage.setText(str(num))

    def removeRowDatas(self,row='all'):
        """移除行"""
        if row == 'all':
            for i in range(self.table.rowCount()-1,-1,-1):
                self.table.removeRow(i)
        elif row.isdigit():
            self.table.removeRow(row)

    def removeColDatas(self,col='all'):
        """移除行"""
        if col == 'all':
            for i in range(self.table.columnCount() - 1, -1, -1):
                self.table.removeColumn(i)
        elif col.isdigit():
            self.table.removeColumn(col)

    def addRows(self,row=1):
        """添加行"""
        for i in range(row):
            self.table.addRow(1)

    def inventoryInfo_page_controller(self,signal):
        total_page = self.showTotalPage()
        if "home" == signal[0]:
            self.curPage.setText("1")
        elif "pre" == signal[0]:
            if 1 == int(signal[1]):
                QMessageBox.information(self, "提示", "已经是第一页了", QMessageBox.Yes)
                return
            self.curPage.setText(str(int(signal[1]) - 1))
        elif "next" == signal[0]:
            if total_page == int(signal[1]):
                QMessageBox.information(self, "提示", "已经是最后一页了", QMessageBox.Yes)
                return
            self.curPage.setText(str(int(signal[1]) + 1))
        elif "final" == signal[0]:
            self.curPage.setText(str(total_page))
        elif "confirm" == signal[0]:
            if total_page < int(signal[1]) or int(signal[1]) < 0:
                QMessageBox.information(self, "提示", "跳转页码超出范围", QMessageBox.Yes)
                return
            self.curPage.setText(signal[1])
        cur_page = self.curPage.text()  # 改变表格内容
        if self.changePageFunc:
            self.changePageFunc(page=cur_page)

class MyListWidget(QListWidget):
    def __init__(self,func=None):
        QListWidget.__init__(self)
        if func:
            self.func = func
            self.itemClicked.connect(self.item_click)

            self.messages = message()
            self.messages.signal.connect(self.func)

    def item_click(self, item):
        self.messages.signal.emit(str(item.statusTip()))

class DraggableLabel(QLabel):
    """可编辑的标签"""
    def __init__(self, title,parent,clickFun,isBorder=0.5,zoomFeedbackFunc=None,positionChange=None):
        super().__init__(title,parent)
        self.isBorder = isBorder
        self.zoomFeedbackFunc = zoomFeedbackFunc        #缩放反馈
        self.positionChange = positionChange
        self.iniDragCor = [0, 0]
        #self.setAlignment(Qt.AlignCenter)
        self.setAlignment(Qt.AlignLeft)

        if self.isBorder:
            #self.setStyleSheet(f"""QLabel{{ border:{self.isBorder}px dotted black;}}""")
            self.setStyleSheet(f"""QLabel:hover{{border:{self.isBorder}px dotted black;}}""")
        self.setMouseTracking(True)
        self.isEditStatus = False       #是否编辑状态
        self.enableAdj = False  # 是否启用控件调整
        self.isZoom = False  # 是否缩放状态
        self.isZoomX = False
        self.isZoomY = False
        self.widgetValue = {}

        self.messages = message()
        self.clickFun = clickFun
        self.messages.signal.connect(self.clickFun)
        self.messages.zoomFeedbackSignal.connect(self.zoomFeedbackFunc)
        if self.positionChange:
            self.messages.signal2.connect(self.positionChange)

    def setZoomBroad(self):
        """设置缩放状态下的边框"""
        self.setStyleSheet(f"""QLabel{{ border:{self.isBorder}px dotted black;}}""")

    def editText(self):
        """编辑状态"""
        print('编辑状态')
        self.isEditStatus = True
        self.enableAdj = False
        self.setCursor(Qt.IBeamCursor)              #编辑光标
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.TextEditable)

    def noEditText(self):
        """非编辑状态"""
        print('非编辑状态')
        self.setCursor(Qt.ArrowCursor)              #指向光标
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.isEditStatus = False

    def mousePressEvent(self, e):
        if self.isEditStatus:
            return None
        #print("按下", e.pos())
        #self.setFocus()
        self.messages.signal.emit(self)
        self.enableAdj = True
        # self.heights = self.height() - self.isBorder*2
        # self.widths = self.width() - self.isBorder*2
        self.heights = self.height()
        self.widths = self.width()
        self.currentX = self.geometry().x()  # 当前x坐标
        self.currentY = self.geometry().y()  # 当前y坐标
        #print(self.currentX, self.currentY)
        #print(self.widths, self.heights)
        if self.enableAdj:
            self.iniDragCor[0] = e.x()
            self.iniDragCor[1] = e.y()

    def mouseReleaseEvent(self, e):
        if self.isEditStatus:
            return None
        #print("松开", e.pos())
        self.enableAdj = False

    def mouseMoveEvent(self, e):
        #self.isDrag = False
        if not self.enableAdj and not self.isEditStatus and ((e.x() == 0 and e.y() == 0)  or (e.x() ==self.width() - self.isBorder*2 and e.y() == self.height() - self.isBorder*2)):
            self.setCursor(Qt.SizeFDiagCursor)  # 斜左向光标
            self.isDrag = False
            self.isZoom = True
            self.isZoomX = False
            self.isZoomY = False
        elif not self.enableAdj and not self.isEditStatus and ((e.x() == 0 and e.y() == self.height() - self.isBorder*2) or (e.x() == self.width() - self.isBorder*2 and e.y() == 0)):
            self.setCursor(Qt.SizeBDiagCursor)  # 斜右向光标
            self.isDrag = False
            self.isZoom = True
            self.isZoomX = False
            self.isZoomY = False
        elif not self.enableAdj and not self.isEditStatus and (e.x() == 0 or e.x() == self.width() - self.isBorder*2 ):
            self.setCursor(Qt.SizeHorCursor)        #横向光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = True
            self.isZoomY = False
        elif not self.enableAdj and not self.isEditStatus and (e.y() == 0 or e.y() == self.height() - self.isBorder*2):
            self.setCursor(Qt.SizeVerCursor)        #纵向光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = True
        elif not self.enableAdj and not self.isEditStatus:
            self.setCursor(Qt.SizeAllCursor)  # 移动光标
            self.isDrag = True
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = False

        if self.enableAdj and self.isDrag:  # 调整位置
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            cor = QPoint(x, y)
            currentX = self.mapToParent(cor).x()
            currentY = self.mapToParent(cor).y()
            if currentX <= 0:
                self.move(0, currentY)
            elif currentY <= 0:
                self.move(currentX, 0)
            else:
                self.move(currentX, currentY)  # 需要maptoparent一下才可以的,否则只是相对位置。
            if self.positionChange:
                datas = [self.geometry().x(),self.geometry().y()]
                self.messages.signal2.emit(datas)
            # print('drag button event,', time.time(), e.pos(), e.x(), e.y())
        elif self.enableAdj and self.isZoomX:  # 横向缩放
            x = e.x() - self.iniDragCor[0]

            newFont = self.font()
            stretchs = newFont.stretch()
            if self.widths + x > self.width():
                stretchs = newFont.stretch() + 1
            elif self.widths + x < self.width():
                stretchs = newFont.stretch() - 1

            if self.widths + x <= 2:
                return None
            self.resize(self.widths + x, self.heights)
            #self.messages.zoomFeedbackSignal.emit(round(self.height() - self.isBorder * 2))

            newFont.setStretch(stretchs)
            #self.setFont(newFont)
        elif self.enableAdj and self.isZoomY:  # 纵向缩放
            y = e.y() - self.iniDragCor[1]
            if self.heights + y <= 2:
                return None
            self.resize(self.widths, self.heights + y)
            self.messages.zoomFeedbackSignal.emit(round(self.height() - self.isBorder * 2))
        elif self.enableAdj and self.isZoom:  # 缩放
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            newFont = self.font()
            stretchs = newFont.stretch()
            if self.widths + x > self.width():
                stretchs = newFont.stretch() + 1
            elif self.widths + x < self.width():
                stretchs = newFont.stretch() - 1
            if self.widths + x <= 2 or self.heights + y <= 2:
                return None
            self.resize(self.widths + x, self.heights + y)
            newFont.setStretch(stretchs)
            # self.setFont(newFont)
            self.messages.zoomFeedbackSignal.emit(round(self.height() - self.isBorder * 2))
        #self.adjustSize()

    def setFontSize(self, value):
        pass
        #self.setStyleSheet(f"QLabel{{font-size:{value}px;border:{self.isBorder}px dotted black;}}")

    def keyPressEvent(self, e) -> bool:
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Escape or e.key() == Qt.Key_Enter:
            print(self.text())
        else:
            super().keyPressEvent(e)

    def setWidgetValue(self, value):
        """设置可读值"""
        self.widgetValue = value

    def updateWidgetValue(self,value):
        """更细可读值"""
        self.widgetValue.update(value)

    def getWidgetValue(self):
        """返回可读值"""
        return self.widgetValue

    def updateStyleSheet(self,changeValue):
        """更新样式表"""
        oldStyleSheet = self.styleSheet()
        pat = re.compile(r'QLabel{(.*?)}')
        value = pat.findall(oldStyleSheet)
        if value:
            styleSheetValue = value[0]
        else:
            styleSheetValue = ''
        for key,data in changeValue.items():
            pat = re.compile(r'{0}:(.*?);'.format(key))
            value = pat.findall(oldStyleSheet)
            if value:
                value = value[0]
                styleSheetValue = styleSheetValue.replace(f'{key}:{value};',f'{key}:{data};')
            else:
                styleSheetValue += f'{key}:{data};'
        newStyleSheet = f'QLabel{{{styleSheetValue}}}'
        self.setStyleSheet(newStyleSheet)
        self.adjustSize()

    def updateFontStyle(self,changeValue):
        """更改字体"""
        newFont = self.font()
        fontSzie = changeValue.get('font-size')
        fontFamily = changeValue.get('font-family')
        fontStretch = changeValue.get('font-stretch')
        fontBold = changeValue.get('font-Bold')
        fontSpacing = changeValue.get('font-spacing')
        if fontSzie:
            newFont.setPixelSize(fontSzie)
            #newFont.setPointSize(int(fontSzie))
        if fontFamily:
            newFont.setFamily(fontFamily)
        if fontStretch:
            newFont.setStretch(int(fontStretch))
        if fontBold is not None:
            newFont.setBold(fontBold)
        if fontSpacing:
            fontSpacingNum = 100.0            #基础间距
            fontSpacingNum = fontSpacingNum * (fontSpacing / 100)
            newFont.setLetterSpacing(QFont.PercentageSpacing,fontSpacingNum)
        self.setFont(newFont)
        self.adjustSize()

    def getFontStyle(self):
        """获取字体样式信息"""
        font = self.font()
        fontSize = font.pixelSize()
        fontFamily = font.family()
        fontStretch = font.stretch()
        fontSpacing = font.letterSpacing()
        fontBold = font.bold()
        return {'font-size':fontSize,'font-family':fontFamily,'font-stretch':fontStretch,'font-spacing':fontSpacing,'font-Bold':fontBold}

    def delStyleSheet(self,values):
        """删除样式"""
        oldStyleSheet = self.styleSheet()
        pat = re.compile(r'QLabel{(.*?)}')
        value = pat.findall(oldStyleSheet)
        if value:
            styleSheetValue = value[0]
        else:
            styleSheetValue = ''
        for data in values:
            pat = re.compile(r'{0}:(.*?);'.format(data))
            value = pat.findall(oldStyleSheet)
            if value:
                value = value[0]
                styleSheetValue = styleSheetValue.replace(f'{data}:{value};', '')

        newStyleSheet = f'QLabel{{{styleSheetValue}}}'
        self.setStyleSheet(newStyleSheet)
        self.adjustSize()

class DraggableTextEdit(QLineEdit):
    """可编辑的标签"""
    def __init__(self,parent,clickFun,isBorder=0.5,positionChange=None):
        super().__init__(parent)
        self.iniDragCor = [0, 0]
        self.setReadOnly(True)
        self.setAlignment(Qt.AlignVCenter)
        # self.setMouseTracking(True)
        self.resize(100,50)
        self.isBorder = isBorder
        if self.isBorder:
            self.setStyleSheet(f"""QLabel{{ border:{self.isBorder}px solid black;}}""")
        self.widgetValue = {}
        self.isEditStatus = False  # 是否可编辑
        self.enableAdj = False  # 是否启用控件调整
        self.isZoom = False  # 是否缩放状态
        self.isZoomX = False
        self.isZoomY = False
        self.positionChange = positionChange

        self.messages = message()
        self.clickFun = clickFun
        self.messages.signal.connect(self.clickFun)
        if self.positionChange:
            self.messages.signal2.connect(self.positionChange)

    def mousePressEvent(self, e):
        print("按下", e.pos())
        self.messages.signal.emit(self)
        self.enableAdj = True
        self.heights = self.height()
        self.widths = self.width()
        self.currentX = self.geometry().x()  # 当前x坐标
        self.currentY = self.geometry().y()  # 当前y坐标
        if self.enableAdj:
            self.iniDragCor[0] = e.x()
            self.iniDragCor[1] = e.y()

    def mouseReleaseEvent(self, e):
        print("松开", e.pos())
        self.enableAdj = False

    # def mouseDoubleClickEvent(self, e):
    #     self.setReadOnly(False)

    def mouseMoveEvent(self, e):
        if not self.enableAdj and ((e.x() == 0 and e.y() == 0) or (e.x() == self.width()- self.isBorder*2 and e.y() == self.height()- self.isBorder*2)):
            self.setCursor(Qt.SizeFDiagCursor)  # 斜左向光标
            self.isDrag = False
            self.isZoom = True
            self.isZoomX = False
            self.isZoomY = False
        elif not self.enableAdj and((e.x() == 0 and e.y() == self.height()- self.isBorder*2) or (e.x() == self.width()- self.isBorder*2 and e.y() == 0)):
            self.setCursor(Qt.SizeBDiagCursor)  # 斜右向光标
            self.isDrag = False
            self.isZoom = True
            self.isZoomX = False
            self.isZoomY = False
        elif not self.enableAdj and (e.x() == 0 or e.x() == self.width()- self.isBorder*2):
            self.setCursor(Qt.SizeHorCursor)  # 横向光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = True
            self.isZoomY = False
        elif not self.enableAdj and (e.y() == 0 or e.y() == self.height()- self.isBorder*2):
            self.setCursor(Qt.SizeVerCursor)  # 纵向光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = True
        elif not self.enableAdj:
            self.setCursor(Qt.SizeAllCursor)  # 移动光标
            self.isDrag = True
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = False

        if self.enableAdj and self.isDrag:  # 调整位置
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            cor = QPoint(x, y)
            currentX = self.mapToParent(cor).x()
            currentY = self.mapToParent(cor).y()
            if currentX <= 0:
                self.move(0, currentY)
            elif currentY <= 0:
                self.move(currentX, 0)
            else:
                self.move(currentX, currentY)  # 需要maptoparent一下才可以的,否则只是相对位置。

            if self.positionChange:
                datas = [self.geometry().x(), self.geometry().y()]
                self.messages.signal2.emit(datas)
            # print('drag button event,', time.time(), e.pos(), e.x(), e.y())
        elif self.enableAdj and self.isZoomX:  # 横向缩放
            x = e.x() - self.iniDragCor[0]
            if self.widths + x <= 2:
                return None
            self.resize(self.widths + x, self.heights)
        elif self.enableAdj and self.isZoomY:  # 纵向缩放
            y = e.y() - self.iniDragCor[1]
            if self.heights + y <= 2:
                return None
            self.resize(self.widths, self.heights + y)
        elif self.enableAdj and self.isZoom:  # 缩放
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            if self.widths + x <= 2 or self.heights + y <= 2:
                return None
            self.resize(self.widths + x, self.heights + y)

    def setFontSize(self,value):
        self.setStyleSheet(f"QLineEdit{{font-size:{value}px;border:{self.isBorder}px dotted black;}}")

    def setNotBorder(self):
        """设置无边框"""
        self.setStyleSheet(f"QLineEdit{{border-width:0;border-style:outset}}")

    def setWidgetValue(self, value):
        """设置可读值"""
        self.widgetValue = value

    def updateWidgetValue(self,value):
        """更细可读值"""
        self.widgetValue.update(value)

    def getWidgetValue(self):
        """返回可读值"""
        return self.widgetValue

class DraggableImg(QLabel):
    """显示图片并可编辑的标签"""
    def __init__(self, parent,clickFun,imgPath=None, isBorder=0.5,positionChange=None,sizeChange=None):
        super().__init__(parent)
        self.imgPath = imgPath
        self.isBorder = isBorder
        if self.isBorder:
            self.setStyleSheet(f"""QLabel{{ border:{self.isBorder}px dotted black;}}""")
        if self.imgPath:
            pixMap = QPixmap(self.imgPath)
            self.setPixmap(pixMap)
            self.setScaledContents(True)
        self.iniDragCor = [0, 0]
        self.widgetValue = {}
        self.pixMap = QPixmap()
        self.pixmapCache = QPixmapCache()

        self.setMouseTracking(True)
        self.enableAdj = False  # 是否启用控件调整
        self.isZoom = False  # 是否缩放状态
        self.isZoomX = False
        self.isZoomY = False
        self.positionChange = positionChange
        self.sizeChange = sizeChange

        self.messages = message()
        self.clickFun = clickFun
        self.messages.signal.connect(self.clickFun)
        if self.positionChange:
            self.messages.signal2.connect(self.positionChange)
        if self.sizeChange:
            self.messages.signal3.connect(self.sizeChange)

    def mousePressEvent(self, e):
        #print("按下", e.pos())
        self.messages.signal.emit(self)
        self.enableAdj = True
        # self.heights = self.height() - self.isBorder * 2
        # self.widths = self.width() - self.isBorder * 2
        self.heights = self.height()
        self.widths = self.width()
        self.currentX = self.geometry().x()  # 当前x坐标
        self.currentY = self.geometry().y()  # 当前y坐标
        # print(self.currentX, self.currentY)
        #print(self.currentX, self.currentY)
        if self.enableAdj:
            self.iniDragCor[0] = e.x()
            self.iniDragCor[1] = e.y()

    def mouseReleaseEvent(self, e):
        #print("松开", e.pos())
        self.enableAdj = False

    def mouseMoveEvent(self, e):
        if not self.enableAdj and ((e.x() == 0 and e.y() == 0) or (e.x() == self.width() - self.isBorder * 2 and e.y() == self.height() - self.isBorder * 2)):
            self.setCursor(Qt.SizeFDiagCursor)  # 斜左向光标
            self.isDrag = False
            self.isZoom = True
            self.isZoomX = False
            self.isZoomY = False
        elif not self.enableAdj and ((e.x() == 0 and e.y() == self.height() - self.isBorder * 2) or (
                e.x() == self.width() - self.isBorder * 2 and e.y() == 0)):
            self.setCursor(Qt.SizeBDiagCursor)  # 斜右向光标
            self.isDrag = False
            self.isZoom = True
            self.isZoomX = False
            self.isZoomY = False
        elif not self.enableAdj and (e.x() == 0 or e.x() == self.width() - self.isBorder * 2):
            self.setCursor(Qt.SizeHorCursor)  # 横向光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = True
            self.isZoomY = False
        elif not self.enableAdj and (e.y() == 0 or e.y() == self.height() - self.isBorder * 2):
            self.setCursor(Qt.SizeVerCursor)  # 纵向光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = True
        elif not self.enableAdj:
            self.setCursor(Qt.SizeAllCursor)  # 移动光标
            self.isDrag = True
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = False

        #print(e.x(),e.y(),self.width(),self.height())

        startPointX = self.geometry().x()
        startPointY = self.geometry().y()
        if self.enableAdj and self.isDrag:  # 调整位置
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            cor = QPoint(x, y)
            currentX = self.mapToParent(cor).x()
            currentY = self.mapToParent(cor).y()
            if currentX <= 0:
                self.move(0, currentY)
            elif currentY <= 0:
                self.move(currentX, 0)
            else:
                self.move(currentX, currentY)  # 需要maptoparent一下才可以的,否则只是相对位置。

            if self.positionChange:
                datas = [self.geometry().x(), self.geometry().y()]
                self.messages.signal2.emit(datas)
        elif self.enableAdj and self.isZoomX:  # 横向缩放
            if e.x() == 0:
                x = e.x() - self.iniDragCor[0]
            else:
                x = e.x() - self.iniDragCor[0]
            startPointX += x
            startPointX = 0 if startPointX < 0 else startPointX

            if self.widths + x <= 2:
                return None
            self.resize(self.widths + x, self.heights)
            if self.sizeChange:
                data = [self.widths + x, self.heights]
                self.messages.signal3.emit(data)
            # self.setGeometry(startPointX,startPointY,self.widths + x, self.heights)
        elif self.enableAdj and self.isZoomY:  # 纵向缩放
            y = e.y() - self.iniDragCor[1]
            if self.heights + y <= 2:
                return None
            self.resize(self.widths, self.heights + y)
            if self.sizeChange:
                data = [self.widths, self.heights + y]
                self.messages.signal3.emit(data)
        elif self.enableAdj and self.isZoom:  # 缩放
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            self.resize(self.widths + x, self.heights + y)
            if self.sizeChange:
                data = [self.widths + x, self.heights + y]
                self.messages.signal3.emit(data)

    def setImg(self,imgPath):
        """设置图片"""
        self.pixmapCache.setCacheLimit(1)
        self.pixMap.load(imgPath)
        self.setPixmap(self.pixMap)
        self.setScaledContents(True)

    def setWidgetValue(self,value):
        """设置可读值"""
        self.widgetValue = value

    def updateWidgetValue(self,value):
        """更细可读值"""
        self.widgetValue.update(value)

    def getWidgetValue(self):
        """返回可读值"""
        return self.widgetValue

class DraggableLine(QFrame):
    """可编辑的直线"""
    def __init__(self, parent,clickFun,orientation='Horizontal',isBorder=0,zoomFeedbackFunc=None,positionChange=None,sizeChange=None):
        super().__init__(parent)
        self.isBorder = isBorder
        self.zoomFeedbackFunc = zoomFeedbackFunc        #缩放反馈
        self.positionChange = positionChange
        self.sizeChange = sizeChange
        self.iniDragCor = [0, 0]
        #self.setStyleSheet("""QFrame{background-color: black;}""")
        if self.isBorder:
            self.setStyleSheet(f"""QFrame{{background-color: black;}} QFrame:hover{{border:{self.isBorder}px dotted green;}}""")
        else:
            self.setStyleSheet("""QFrame{background-color: black;}""")
        # font = QFont()
        # font.setPointSize(9)
        # self.setFont(font)
        self.orientation = orientation
        if orientation == 'Horizontal':
            self.setFrameShape(QFrame.HLine)
            #self.setLineWidth(1)
        else:
            self.setFrameShape(QFrame.VLine)
            #self.setLineWidth(1)
        self.setFrameShadow(QFrame.Sunken)

        self.setMouseTracking(True)
        self.isEditStatus = False       #是否编辑状态
        self.enableAdj = False  # 是否启用控件调整
        self.isZoom = False  # 是否缩放状态
        self.isZoomX = False
        self.isZoomY = False
        self.widgetValue = {'lineSize':1}
        self.heights = self.height()
        self.widths = self.width()

        self.messages = message()
        self.clickFun = clickFun
        self.messages.signal.connect(self.clickFun)
        self.messages.zoomFeedbackSignal.connect(self.zoomFeedbackFunc)
        if self.positionChange:
            self.messages.signal2.connect(self.positionChange)
        if self.sizeChange:
            self.messages.signal3.connect(self.sizeChange)

    def mousePressEvent(self, e):
        if self.isEditStatus:
            return None
        #print("按下", e.pos())
        #self.setFocus()
        self.messages.signal.emit(self)
        self.enableAdj = True
        # self.heights = self.height() - self.isBorder*2
        # self.widths = self.width() - self.isBorder*2
        self.heights = self.height()
        self.widths = self.width()
        self.currentX = self.geometry().x()  # 当前x坐标
        self.currentY = self.geometry().y()  # 当前y坐标
        # print(self.currentX, self.currentY)
        #print(self.widths, self.heights)
        if self.enableAdj:
            self.iniDragCor[0] = e.x()
            self.iniDragCor[1] = e.y()

    def mouseReleaseEvent(self, e):
        if self.isEditStatus:
            return None
        #print("松开", e.pos())
        self.enableAdj = False

    def mouseMoveEvent(self, e):
        if not self.enableAdj and not self.isEditStatus and ((self.width() - e.x() <= 3 or e.x() <= 3) and e.y() <= 3 ) :
            self.setCursor(Qt.CrossCursor)  # 缩放光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = True
            self.isZoomY = False
        elif not self.enableAdj and not self.isEditStatus and ((self.height() - e.y() <= 3 or e.y() <= 3) and e.x() <= 3 ) :
            self.setCursor(Qt.CrossCursor)  # 缩放光标
            self.isDrag = False
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = True
        elif not self.enableAdj and not self.isEditStatus:
            self.setCursor(Qt.SizeAllCursor)  # 移动光标
            self.isDrag = True
            self.isZoom = False
            self.isZoomX = False
            self.isZoomY = False

        if self.enableAdj and self.isDrag:  # 调整位置
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            cor = QPoint(x, y)
            currentX = self.mapToParent(cor).x()
            currentY = self.mapToParent(cor).y()
            if currentX <= 0:
                self.move(0, currentY)
            elif currentY <= 0:
                self.move(currentX, 0)
            else:
                self.move(currentX, currentY)  # 需要maptoparent一下才可以的,否则只是相对位置。
            if self.positionChange:
                datas = [self.geometry().x(), self.geometry().y()]
                self.messages.signal2.emit(datas)
            # print('drag button event,', time.time(), e.pos(), e.x(), e.y())
        elif self.enableAdj and self.isZoomX:  # 横向缩放
            x = e.x() - self.iniDragCor[0]

            newFont = self.font()
            stretchs = newFont.stretch()
            if self.widths + x > self.width():
                stretchs = newFont.stretch() + 1
            elif self.widths + x < self.width():
                stretchs = newFont.stretch() - 1

            if self.widths + x <= 2:
                return None
            self.resize(self.widths + x, self.heights)
            self.widgetValue.update({'lineLength': self.widths + x})
            if self.sizeChange:
                data = [self.widths + x, None]
                self.messages.signal3.emit(data)
        elif self.enableAdj and self.isZoomY:  # 纵向缩放
            y = e.y() - self.iniDragCor[1]
            if self.heights + y <= 2:
                return None
            self.resize(self.widths, self.heights + y)
            self.messages.zoomFeedbackSignal.emit(round(self.height() - self.isBorder * 2))
            self.widgetValue.update({'lineLength': self.heights + y})
            if self.sizeChange:
                data = [None, self.heights + y]
                self.messages.signal3.emit(data)
        elif self.enableAdj and self.isZoom:  # 缩放
            x = e.x() - self.iniDragCor[0]
            y = e.y() - self.iniDragCor[1]
            newFont = self.font()
            stretchs = newFont.stretch()
            if self.widths + x > self.width():
                stretchs = newFont.stretch() + 1
            elif self.widths + x < self.width():
                stretchs = newFont.stretch() - 1
            if self.widths + x <= 2 or self.heights + y <= 2:
                return None
            self.resize(self.widths + x, self.heights + y)
            newFont.setStretch(stretchs)
            # self.setFont(newFont)
            self.messages.zoomFeedbackSignal.emit(round(self.height() - self.isBorder * 2))
        #self.adjustSize()

    def setWidgetValue(self,value):
        """设置可读值"""
        self.widgetValue.update(value)

    def getWidgetValue(self):
        """返回可读值"""
        return self.widgetValue

    def updateLineThickness(self,changeValue):
        """更改线条粗细"""
        try:
            if self.orientation == 'Horizontal':
                self.resize(self.widths, changeValue)
            else:
                self.resize(changeValue, self.heights)
            self.widgetValue.update({'width': changeValue})
        except:
            print(traceback.format_exc())

    def updateWidgetValue(self,value):
        """更细可读值"""
        self.widgetValue.update(value)


class message(QThread):
    """信号"""
    signal = pyqtSignal(object)
    signal2 = pyqtSignal(object)
    signal3 = pyqtSignal(object)
    messageboxSignal = pyqtSignal(str)
    changePwdSignal = pyqtSignal(dict)
    addDataSignal = pyqtSignal(dict)
    confirmSignal = pyqtSignal(str)
    setControlsData = pyqtSignal(object)
    showProgressBar = pyqtSignal()
    closeProgressBar = pyqtSignal()
    childWinClose = pyqtSignal(object)
    zoomFeedbackSignal = pyqtSignal(object)

    def __init__(self):
        super(message, self).__init__()

class UiMainWindow(QWidget):
    def __init__(self):
        super(UiMainWindow, self).__init__()
        self.setWindowTitle('Test')
        self.resize(600, 400)
        combo = ComboCheckBox(["Python", "Java", "Go", "C++", "JavaScript", "PHP"],separator='/')
        layout = QVBoxLayout()
        layout.addWidget(combo)
        self.setLayout(layout)

class MyWidget(QWidget):
    def __init__(self,parent=None):
        super(MyWidget, self).__init__(parent)

    def mousePressEvent(self, e):
        self.setFocus()

    def paintEvent(self, event):
        # 以下几行代码的功能是避免在多重传值后的功能失效
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)



if __name__ == "__main__":
     app = QApplication(sys.argv)
     ui = UiMainWindow()
     ui.show()
     sys.exit(app.exec_())