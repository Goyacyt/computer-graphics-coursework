#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QColorDialog,
    QInputDialog,
    QFileDialog)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor,QPixmap
from PyQt5.QtCore import QRectF,Qt,QDir


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None

        self.pen_color=QColor(255,0,0)

        #平移的两个坐标
        self.x0=0
        self.y0=0
        self.x1=0
        self.y1=0
        self.x2=0
        self.y2=0
        self.degree=0#旋转角
    
    def set_pen_color(self,color):
        self.pen_color=color

    def reset_canvas(self):
        self.clear_selection()
        self.item_dict = {}
        self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.pen_color=QColor(255,0,0)
        self.updateScene([self.sceneRect()])

    def start_draw_mouse(self,item_id):
        self.status="mouse"
        self.temp_id = item_id
        self.temp_item=None

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item=None
    
    def start_draw_polygon(self,algorithm,item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item=None
    
    def start_draw_ellipse(self,item_id):
        self.status = 'ellipse'
        self.temp_id = item_id
        self.temp_item=None
    
    def start_draw_curve(self,algorithm,item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item=None

    def start_translate(self):
        self.status='translate'
        self.temp_id = self.selected_id

    def start_scale(self):
        self.status='scale'
        self.temp_id = self.selected_id

    def start_rotate(self):
        self.status='rotate'
        self.temp_id = self.selected_id

    def start_clip(self,algorithm):
        self.status='clip'
        self.temp_id = self.selected_id
        self.temp_algorithm=algorithm

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status=="ellipse":
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status=="mouse":
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm,self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status=="polygon" or self.status=="curve":
            if self.temp_item==None:
                self.temp_item=MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm,self.pen_color)
                self.scene().addItem(self.temp_item)
                self.temp_item.p_list.append([x,y])
            else:
                if event.button()==Qt.RightButton:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.temp_item=None
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append([x, y])
        elif self.status=="translate":
            self.temp_id=self.selected_id
            self.temp_item=self.item_dict[self.temp_id]
            if self.temp_item==None:
                print("error!the selected item not exist")
            else:
                self.x0,self.y0=x,y
        elif self.status=="rotate":
            self.temp_id=self.selected_id
            self.temp_item=self.item_dict[self.temp_id]
            if self.temp_item==None:
                print("error!the selected item not exist")
            else:
                if event.button()==Qt.LeftButton:
                    self.x0,self.y0=x,y
                    """if success:
                        self.temp_item.p_list=alg.rotate(self.item_dict[self.temp_id].p_list,self.x0,self.y0,self.degree)"""
                else:
                    self.x1,self.y1=x,y
        elif self.status=="scale":
            self.temp_id=self.selected_id
            self.temp_item=self.item_dict[self.temp_id]
            if self.temp_item==None:
                print("error!the selected item not exist")
            else:
                if event.button()==Qt.LeftButton:
                    self.x0,self.y0=x,y
                else:
                    self.x1,self.y1=x,y
                
        elif self.status=="clip":
            self.temp_id=self.selected_id
            self.temp_item=self.item_dict[self.temp_id]
            if self.temp_item==None:
                print("error!the selected item not exist")
            else:
                self.x0,self.y0=x,y
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status=="mouse":
            self.temp_item.p_list.append([x,y])
        elif self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status=="translate":
            self.x1,self.y1=x,y
            dx=self.x1-self.x0
            dy=self.y1-self.y0
            self.temp_item.p_list=alg.translate(self.item_dict[self.temp_id].p_list,dx,dy)
            self.x0,self.y0=x,y
        elif self.status=="clip":
            self.x1,self.y1=x,y
        elif self.status=="rotate":
            if event.button()==Qt.LeftButton:
                pass
            else:
                self.x2,self.y2=x,y
        elif self.status=="scale":
            if event.button()==Qt.LeftButton:
                pass
            else:
                self.x2,self.y2=x,y
                if (self.x1-self.x0)==0:
                    self.s=0
                else:
                    self.s=(self.x2-self.x0)/(self.x1-self.x0)
                self.temp_item.p_list=alg.scale(self.item_dict[self.temp_id].p_list,self.x0,self.y0,self.s)
                self.x1,self.y1=x,y
        
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.temp_item=None
            self.finish_draw()
        elif self.status=="mouse":
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.temp_item=None
            self.finish_draw()
        elif self.status=="ellipse":
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.temp_item=None
            self.finish_draw()
        elif self.status=="translate":
            self.item_dict[self.temp_id]=self.temp_item
            self.updateScene([self.sceneRect()])
            self.temp_item=None
        elif self.status=="scale":
            self.item_dict[self.temp_id]=self.temp_item
            self.updateScene([self.sceneRect()])
            self.temp_item=None
        elif self.status=="rotate":
            if event.button()==Qt.LeftButton:
                pass
            else:
                dx1 = self.x1-self.x0
                dy1 = self.y1-self.y0
                dx2 = self.x2-self.x0
                dy2 = self.y2-self.y0
                angle1 = math.atan2(dy1, dx1)
                angle1 = int(angle1 * 180/math.pi)
                angle2 = math.atan2(dy2, dx2)
                angle2 = int(angle2 * 180/math.pi)
                self.degree = angle2-angle1
                self.temp_item.p_list=alg.rotate(self.item_dict[self.temp_id].p_list,self.x0,self.y0,self.degree)

                self.item_dict[self.temp_id]=self.temp_item
                self.updateScene([self.sceneRect()])
            #self.temp_item=None
        elif self.status=="clip":
            self.temp_item.p_list=alg.clip(self.item_dict[self.temp_id].p_list,self.x0,self.y0,self.x1,self.y1,self.temp_algorithm)
            self.item_dict[self.temp_id]=self.temp_item
            self.updateScene([self.sceneRect()])
            self.temp_item=None
        
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '',pen_color=QColor(255,0,0), parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.pen_color=pen_color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen_color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type=="mouse":
            item_pixels=self.p_list
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
        
        if self.selected:
            painter.setPen(self.pen_color)
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve' or self.item_type=="mouse":
            if len(self.p_list)==0:
                return QRectF(0,0,0,0)
            elif len(self.p_list)==1:
                x,y=self.p_list[0]
                return QRectF(x,y,2,2)
            else:
                x,y=self.p_list[0]
                w,h=x,y
                for i in range(1,len(self.p_list)):
                    nx,ny=self.p_list[i]
                    if nx<x:
                        x=nx
                    if ny<y:
                        y=ny
                    if nx>w:
                        w=nx
                    if ny>h:
                        h=ny
                w=w-x
                h=h-y
                return QRectF(round(x-1),round(y-1),round(w+2),round(h+2))



class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act=file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        mouse_act=draw_menu.addAction('鼠标移动轨迹')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        mouse_act.triggered.connect(self.mouse_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id
    
    def set_pen_action(self):
        self.canvas_widget.set_pen_color(QColorDialog.getColor())

    def reset_canvas_action(self):
        height,success = QInputDialog.getInt(self, '画布大小', '画布长度', 600, 100, 2147483647)
        if success==True:
            self.height=height
        width,success = QInputDialog.getInt(self, '画布大小', '画布宽度', 600, 100, 2147483647)
        if success==True:
            self.width=width
        self.item_cnt = 0
        self.canvas_widget.reset_canvas()
        self.list_widget.currentTextChanged.disconnect(self.canvas_widget.selection_changed)
        self.list_widget.clear()
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        self.scene.clear()
        self.scene.setSceneRect(1, 1, self.width+1, self.height+1)
        self.canvas_widget.setFixedSize(self.width+3, self.height+3)
        
    def save_canvas_action(self):
        filename, type = QFileDialog.getSaveFileName(self,"保存画布",QDir.currentPath(),"BMP Files (*.bmp);;JPG Files (*.jpg);;PNG Files (*.png)")
        if filename:
            if type=="BMP Files (*.bmp)":
                if len(filename)<4 or filename[-4:]!=".bmp":
                    filename=filename+".bmp"
            elif type=="JPG Files (*.jpg)":
                if len(filename)<4 or filename[-4:]!=".jpg":
                    filename=filename+".jpg"
            else:
                if len(filename)<4 or filename[-4:]!=".png":
                    filename=filename+".png"
            picture = QPixmap()
            picture = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            picture.save(filename)

    def mouse_action(self):
        self.canvas_widget.start_draw_mouse(self.get_id())
        self.statusBar().showMessage('绘制鼠标移动路径')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移图元')
    
    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转图元')
    
    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放图元')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip("Cohen-Sutherland")
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪图元')
    
    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip("Liang-Barsky")
        self.statusBar().showMessage('Liang-Barsky算法裁剪图元')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
