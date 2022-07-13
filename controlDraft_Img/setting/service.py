# coding:utf-8

import tkinter as tk
from tkinter import filedialog
import pathlib

from PIL import Image, ImageDraw, ImageFont
import traceback
import base64
import barcode
from barcode.writer import ImageWriter
import qrcode
import io
import os
import re

from PyQt5.QtCore import QThread,pyqtSignal

def getOpenfileName():
    """打开选择文件夹，返回当前选择的文件路径"""
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfilename() #获得选择好的文件路径
    return fileName

def setOpenfileName():
    """打开选择保存的img路径，返回当前选择路径"""
    root = tk.Tk()
    root.withdraw()
    folderPath = filedialog.asksaveasfilename(initialdir=pathlib.Path.cwd(), defaultextension=".png", title="Save As",
                                              filetypes=(("img Files", "*.png"),)) #获得选择好的文件夹

    return folderPath

def findAllFile(path,filename):
    """查找文件"""
    file = getallfile(path).get(filename)
    if(file is not None):
        return file
    return None

def getallfile(path):
    """遍历文件名，返回文件的路径字典"""
    fileDict = {}
    try:
        path_new = pathlib.Path(path)
        allfilelist = path_new.iterdir()
        for file in allfilelist:
            filepath = pathlib.Path('/')/path/file
            #判断是不是文件夹
            if filepath.is_dir():
                getallfile(filepath)
            else:
                fileDict.update({file:filepath})
    except:
        print(traceback.format_exc())
    return fileDict

def imgToDataURL(imgPath,imgMode='png'):
    """png输出dataURL"""
    with open(imgPath,'rb') as f:
        base64_data = base64.b64encode(f.read())
        if base64_data:
            return base64_data
            #return 'data:image/png;base64,' + base64_data.decode()
    return None

def dataURLToImg(url):
    """dataUrl转img对象"""
    try:
        img_b64decode = base64.b64decode(url)
        img_io = io.BytesIO(img_b64decode)
        img = Image.open(img_io)
        pix = img.toqpixmap()
        return pix
    except:
        print(traceback.format_exc())
    return None

def strToBarCode(text_str,filename,barcode_type='code128',font_size=16,text_distance=1,write_text=True,quiet_zone=1,module_height=15.0,module_width=0.2,dpi=300):
    """条形码生成
    font_size：显示字体大小
    text_distance：显示字体距离间距
    write_text:是否显示文本
    quiet_zone:两边空白宽度
    """
    try:
        EAN = barcode.get_barcode_class(barcode_type)
        ean = EAN(text_str, writer=ImageWriter())
        ean.save(filename,options={'font_size':font_size,'text_distance':text_distance,'write_text':write_text,'quiet_zone':quiet_zone,'module_height':module_height,
                                   'module_width':module_width,'dpi':dpi})
    except:
        print(traceback.format_exc())

def strToQRCode(text_str,filename,version=None,boxsize=10,border=4):
    """二维码生成
    version：二维码的大小
    border：二维码距图像外围边框距离
    boxsize:每个点（方块）中的像素个数
    """
    try:
        # 实例化QRCode生成qr对象
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=boxsize,
            border=border
        )
        # 传入数据
        qr.add_data(text_str)
        qr.make(fit=True)
        # 生成二维码
        img = qr.make_image()
        # 保存二维码
        img.save(filename)
        # 展示二维码
        #img.show()
    except:
        print(traceback.format_exc())

def laberDraw(dataList,width=1000,height=1000,interval=50,dpi=300,dpiScreen=96,**kwargs):
    """绘制标签图片,dataList:数据列表,width标签宽度，height标签高度,interval行间隔高度,iniX开始x坐标,iniY:开始y坐标
    type:数据类型(img,str)
    data：数据源(图片数据/字符串数据)
    fixedX:固定X始坐标
    fixedY:Y始坐标
    imgW:img宽度
    imgH:img高度
    imgType:图片类型，barCode:条形码，qrCode:二维码，logo，other
    path:图片路径,
    dpi：打印机像素比
    dpiScreen：电脑屏幕像素比
    """
    base_imgPath = f'./setting/img/laberMode/basis_{width}x{height}.png'
    save_imgPath = kwargs.get('save_img', './setting/img/printPreView.png')
    if not os.path.exists(base_imgPath):
        if not os.path.exists('./setting/img/laberMode/basis_1000x1000.png'):
            return None

        try:
            img = Image.open('./setting/img/laberMode/basis_1000x1000.png')
            out = img.resize((int(width), int(height)), Image.ANTIALIAS)
            # 保存文件
            out.save(base_imgPath)
        except:
            print(traceback.format_exc())
            return None

        if not os.path.exists(base_imgPath):
            return None

    base_img = Image.open(base_imgPath)
    draw = ImageDraw.Draw(base_img)  # 生成绘制对象draw
    for datas in dataList:
        types = datas.get('type')
        data = datas.get('data')
        fixedX = round(datas.get('fixedX',0) / 25.4 * dpiScreen)
        fixedY = round(datas.get('fixedY',0) / 25.4 * dpiScreen)
        tracingPoint = datas.get('tracingPoint',0)
        if types == 'img':
            num = ''
            imgRes = None
            path = datas.get('imgPath')
            if path:
                pattern = re.compile(r'\d+')
                result = pattern.findall(path)
                num = result[0] if result else ''
            imgType = datas.get('imgType')
            if imgType == 'barCode':
                textDistance = datas.get('textDistance',1)
                writeText = datas.get('writeText',True)
                if data:
                    strToBarCode(data, f'./setting/img/editMode/barCode{num}',font_size=21,write_text=writeText,text_distance=textDistance,quiet_zone=0)
            elif imgType == 'qrCode':
                if data:
                    strToQRCode(data,f'./setting/img/editMode/qrCode{num}.png', border=0)

            imgW = round(datas.get('width',0) / 25.4 * dpiScreen)
            imgH = round(datas.get('height',0) / 25.4 * dpiScreen)
            fixedX, fixedY = calculatePoint(imgW,imgH,fixedX, fixedY,tracingPoint)
            if imgRes:
                tmp_img = Image.open(io.BytesIO(imgRes))
            else:
                tmp_img = Image.open(path)
            #tmp_img = Image.open(path)
            region = tmp_img.resize((imgW, imgH))
            if region.mode == 'RGBA':
                base_img.paste(region, (fixedX, fixedY, imgW + fixedX, imgH + fixedY), mask=region)
            else:
                base_img.paste(region, (fixedX, fixedY, imgW + fixedX, imgH + fixedY))
        elif types == 'str':
            textWidth = datas.get('textWidth', 0)
            textHeight = datas.get('textHeight', 0)
            data = datas.get('data')
            fixedX = datas.get('fixedX')
            fixedY = datas.get('fixedY')
            fixedX, fixedY = calculatePoint(textWidth, textHeight, round(fixedX / 25.4  * dpiScreen), round(fixedY / 25.4  * dpiScreen), tracingPoint)
            font = datas.get('font-family', 'simkai.ttf')
            fontBold = datas.get('font-bold')
            if font == '宋体':
                font = 'simsun.ttc'
            elif font == '楷体':
                font = 'simkai.ttf'
            elif font == '黑体':
                font = 'simheiBold.ttf' if fontBold else 'simhei.ttf'
            elif font == 'Arial':
                font = 'arialBold.ttf' if fontBold else 'arial.ttf'
            fontPath = os.path.join(os.getcwd(), 'fonts', font)
            fontPath = fontPath.replace('\\','\\\\')
            fontSize = round(datas.get('fontSize', 10) / 2.845 / 25.4  * dpiScreen)
            typeface = ImageFont.truetype(font=fontPath, size=fontSize)
            draw.text((fixedX, fixedY), data, fill=(0, 0, 0), font=typeface)
        elif types == 'Hline':
            backGroundColor = datas.get('backGroundColor')
            lineLength = round(datas.get('lineLength',0) / 25.4 * dpiScreen)
            lineSize = round(datas.get('lineSize',0) / 25.4 * dpiScreen)
            draw.line((fixedX, fixedY,fixedX+lineLength,fixedY), fill=f'{backGroundColor}',width=lineSize)
        elif types == 'Vline':
            backGroundColor = datas.get('backGroundColor')
            lineLength = round(datas.get('lineLength', 0) / 25.4 * dpiScreen)
            lineSize = round(datas.get('lineSize', 0) / 25.4 * dpiScreen)
            draw.line((fixedX, fixedY,fixedX,fixedY+lineLength), fill=f'{backGroundColor}',width=lineSize)

    #base_img.show()  # 查看合成的图片
    base_img.save(save_imgPath)  # 保存图

    imgUrl = imgToDataURL(save_imgPath)
    return dataURLToImg(imgUrl)

def laberDraw2(datas):
    if not datas:
        return None
    width = datas.get('width')
    height = datas.get('height')
    dpiScreen = datas.get('dpiScreen')
    dataList = datas.get('tmpDatas')
    base_imgPath = f'./setting/img/laberMode/basis_{width}x{height}.png'
    if not os.path.exists(base_imgPath):
        if not os.path.exists('./setting/img/laberMode/basis_1000x1000.png'):
            return None

        try:
            img = Image.open('./setting/img/laberMode/basis_1000x1000.png')
            out = img.resize((int(width), int(height)), Image.ANTIALIAS)
            # 保存文件
            out.save(base_imgPath)
        except:
            print(traceback.format_exc())
            return None

        if not os.path.exists(base_imgPath):
            return None

    base_img = Image.open(base_imgPath)
    draw = ImageDraw.Draw(base_img)  # 生成绘制对象draw
    for datas in dataList:
        types = datas.get('type')
        data = datas.get('data')
        fixedX = round(datas.get('fixedX',0) / 25.4 * dpiScreen)
        fixedY = round(datas.get('fixedY',0) / 25.4 * dpiScreen)
        tracingPoint = datas.get('tracingPoint',0)
        if types == 'img':
            num = ''
            imgRes = None
            path = datas.get('imgPath')
            if path:
                pattern = re.compile(r'\d+')
                result = pattern.findall(path)
                num = result[0] if result else ''
            imgType = datas.get('imgType')
            if imgType == 'barCode':
                textDistance = datas.get('textDistance',1)
                writeText = datas.get('writeText',True)
                if data:
                    strToBarCode(data, f'./setting/img/editMode/barCode{num}',font_size=21,write_text=writeText,text_distance=textDistance,quiet_zone=0)
            elif imgType == 'qrCode':
                if data:
                    strToQRCode(data,f'./setting/img/editMode/qrCode{num}.png', border=0)

            imgW = round(datas.get('width',0) / 25.4 * dpiScreen)
            imgH = round(datas.get('height',0) / 25.4 * dpiScreen)
            fixedX, fixedY = calculatePoint(imgW,imgH,fixedX, fixedY,tracingPoint)
            if imgRes:
                tmp_img = Image.open(io.BytesIO(imgRes))
            else:
                tmp_img = Image.open(path)
            #tmp_img = Image.open(path)
            region = tmp_img.resize((imgW, imgH))
            if region.mode == 'RGBA':
                base_img.paste(region, (fixedX, fixedY, imgW + fixedX, imgH + fixedY), mask=region)
            else:
                base_img.paste(region, (fixedX, fixedY, imgW + fixedX, imgH + fixedY))
        elif types == 'str':
            textWidth = datas.get('textWidth', 0)
            textHeight = datas.get('textHeight', 0)
            data = datas.get('data')
            fixedX = datas.get('fixedX')
            fixedY = datas.get('fixedY')
            fixedX, fixedY = calculatePoint(textWidth, textHeight, round(fixedX / 25.4  * dpiScreen), round(fixedY / 25.4  * dpiScreen), tracingPoint)
            font = datas.get('font-family', 'simkai.ttf')
            fontBold = datas.get('font-bold')
            if font == '宋体':
                font = 'simsun.ttc'
            elif font == '楷体':
                font = 'simkai.ttf'
            elif font == '黑体':
                font = 'simheiBold.ttf' if fontBold else 'simhei.ttf'
            elif font == 'Arial':
                font = 'arialBold.ttf' if fontBold else 'arial.ttf'
            fontPath = os.path.join(os.getcwd(), 'fonts', font)
            fontPath = fontPath.replace('\\','\\\\')
            fontSize = round(datas.get('fontSize', 10) / 2.845 / 25.4  * dpiScreen)
            typeface = ImageFont.truetype(font=fontPath, size=fontSize)
            draw.text((fixedX, fixedY), data, fill=(0, 0, 0), font=typeface)
        elif types == 'Hline':
            backGroundColor = datas.get('backGroundColor')
            lineLength = round(datas.get('lineLength',0) / 25.4 * dpiScreen)
            lineSize = round(datas.get('lineSize',0) / 25.4 * dpiScreen)
            draw.line((fixedX, fixedY,fixedX+lineLength,fixedY), fill=f'{backGroundColor}',width=lineSize)
        elif types == 'Vline':
            backGroundColor = datas.get('backGroundColor')
            lineLength = round(datas.get('lineLength', 0) / 25.4 * dpiScreen)
            lineSize = round(datas.get('lineSize', 0) / 25.4 * dpiScreen)
            draw.line((fixedX, fixedY,fixedX,fixedY+lineLength), fill=f'{backGroundColor}',width=lineSize)

    base_img.show()  # 查看合成的图片

def calculatePoint(comWidth,comHeight, xPoint, yPoint,tracingPoint):
    """根据描点位置计算返回控件的坐标
    tracingPoint：描点位置，0：左上，1：左下，2，右上，3，右下"""
    if tracingPoint == 0:
        xPoint2, yPoint2 = xPoint, yPoint
    elif tracingPoint == 1:
        xPoint2, yPoint2 = xPoint, yPoint - comHeight
    elif tracingPoint == 2:
        xPoint2, yPoint2 = xPoint - comWidth, yPoint
    else:
        xPoint2, yPoint2 = xPoint - comWidth, yPoint - comHeight
    return round(xPoint2), round(yPoint2)

def getScreenPixel():
    """获取屏幕像素比"""
    import winreg
    import wmi

    PATH = "SYSTEM\\ControlSet001\\Enum\\"

    m = wmi.WMI()
    # 获取屏幕信息
    monitors = m.Win32_DesktopMonitor()

    PPI = None
    for m in monitors:
        subPath = m.PNPDeviceID  #
        # 可能有多个注册表
        if subPath == None:
            continue
        maxPPI = None
        # 这个路径是显示器在注册表中的路径：
        infoPath = PATH + subPath + "\\Device Parameters"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, infoPath)
        # 屏幕信息按照一定的规则保存（EDID）
        value = winreg.QueryValueEx(key, "EDID")[0]
        winreg.CloseKey(key)

        # 屏幕实际尺寸
        width, height = value[21], value[22]
        # 推荐屏幕分辨率
        widthResolution = value[56] + (value[58] >> 4) * 256
        heightResolution = value[59] + (value[61] >> 4) * 256
        # 屏幕像素密度（Pixels Per Inch）
        widthDensity = widthResolution / (width / 2.54)
        heightDensity = heightResolution / (height / 2.54)

        PPI = widthDensity if widthDensity > heightDensity else heightDensity

    return PPI

class MyThread(QThread):
    finishSignal = pyqtSignal(object)

    def __init__(self, funcs):
        super(MyThread, self).__init__()
        self.funcs = funcs

    def run(self):
        try:
            self.result = self.funcs()
            self.finishSignal.emit(self.result)
        except:
            print(traceback.format_exc())
        return


import time
def coast_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} coast time:{time.perf_counter() - t:.8f} s')
        return result

    return fun


if __name__ == '__main__':
    pass
