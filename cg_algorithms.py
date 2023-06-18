#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math

def reverseAxis(pointList):
    newList=[]
    for point in pointList:
        x,y=point
        newList.append([y,x])
    return newList

def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        reverse=math.fabs(y1-y0)-math.fabs(x1-x0)>0
        if reverse:
            p_list=reverseAxis(p_list)
        #保证x为步进方向
        if p_list[0][0]<p_list[1][0]:
            start=p_list[0]
            end=p_list[1]
        else:
            start=p_list[1]
            end=p_list[0]
        x0, y0 = start
        x1, y1 = end
        if x1==x0:
            x=x0
            y=y0
            while y<=y1:
                result.append((x,y))
                y+=1
        else:
            k=(y1-y0)/(x1-x0)
            x=x0
            y=y0
            while x<=x1:
                result.append((int(x),int(y)))
                x+=1
                y+=k
        if reverse:
            result=reverseAxis(result)
    elif algorithm == 'Bresenham':
        reverse=math.fabs(y1-y0)-math.fabs(x1-x0)>0
        if reverse:
            p_list=reverseAxis(p_list)
        #保证x为步进方向
        if p_list[0][0]<p_list[1][0]:
            start=p_list[0]
            end=p_list[1]
        else:
            start=p_list[1]
            end=p_list[0]
        x0, y0 = start
        x1, y1 = end
        if x1==x0:
            x=x0
            y=y0
            while y<=y1:
                result.append((x,y))
                y+=1
        else:
            dx=math.fabs(x1-x0)
            dy=math.fabs(y1-y0)
            c=0
            if y1-y0>0:
                c=1
            else:
                c=-1
            x=x0
            y=y0
            delta=2*dy-dx
            while x<=x1:
                result.append((x,y))
                if delta>=0:
                    x+=1
                    y+=c
                    delta=delta+2*dy-2*dx
                else:
                    x+=1
                    delta=delta+2*dy
        if reverse:
            result=reverseAxis(result)

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result

def copy_ellipse(p_list):
    new_list=[]
    new_list=new_list+p_list
    for point in p_list:
        x,y=point
        new_list.append([-x,y])
    res_list=[]
    res_list=res_list+new_list
    for point in new_list:
        x,y=point
        res_list.append([x,-y])
    return res_list

def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0,y0=p_list[0]
    x1,y1=p_list[1]
    result=[]
    center=[int((x0+x1)/2),int((y0+y1)/2)]
    rx=math.fabs((x1-x0)/2)
    rx=int(rx)
    ry=math.fabs((y0-y1)/2)
    ry=int(ry)
    #part A
    x,y=0,ry
    d=ry**2-rx**2*ry+rx**2/4
    while ry**2*x<rx**2*y:
        result.append([x,y])
        x+=1
        if d>=0:
            y-=1
            d+=2*ry**2*x+ry**2-2*rx**2*y
        else:
            d+=2*ry**2*x+ry**2

    #part B
    d=ry**2*(x+0.5)**2+rx**2*(y-1)**2-rx**2*ry**2
    while y>=0:
        result.append([x,y])
        y-=1
        if d<=0:
            x+=1
            d+=rx**2-2*rx**2*y+2*ry**2*x
        else:
            d+=rx**2-2*rx**2*y

    
    result=copy_ellipse(result)
    result=translate(result,center[0],center[1])
    return result

def de_Casteljau(num,p_list,t):
    p=[]
    for r in range(num):
        if r==0:
            for i in range(num):
                p.append(p_list[i])
        else:
            for i in range(num-r):
                x=(1-t)*p[i][0]+t*p[i+1][0]
                y=(1-t)*p[i][1]+t*p[i+1][1]
                p[i]=[x,y]
    return p[0]

def deBoor_Cox(u, k, i):
    if k==1:
        if u>=i and u<i+1:
            return 1
        else:
            return 0
    else:
        b1=deBoor_Cox(u,k-1,i)
        b2=deBoor_Cox(u,k-1,i+1)
        x=b1*(u-i)/(k-1)+b2*(i+k-u)/(k-1)
        return x

def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result=[]
    num=len(p_list)
    tnum=num*1000
    if algorithm=="Bezier":
        for i in range(tnum):
            t=i/tnum
            x,y=de_Casteljau(num,p_list,t)
            result.append([int(x),int(y)])
    elif algorithm=="B-spline":
        #TODO: not implement
        #阶数是生成权重中t值的最高次幂
        #节点表数量=控制点数量+阶数+1
        k=4#k阶B样条
        u=k-1
        while u<num:
            x,y=0,0
            for i in range(num):
                #为每个点计算 B[i,k]
                b=deBoor_Cox(u,k,i)
                x+=(b*p_list[i][0])
                y+=(b*p_list[i][1])
            result.append([round(x),round(y)])
            u+=(1/1000)
    return result

def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    new_list=[]
    for point in p_list:
        nx,ny=point
        nx+=dx
        ny+=dy
        new_list.append([nx,ny])
    return new_list

def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    new_list=translate(p_list,-x,-y)
    r=(r/180)*math.pi
    res_list=[]
    for point in new_list:
        nx,ny=point
        rx=round(nx*math.cos(r)-ny*math.sin(r))
        ry=round(ny*math.cos(r)+nx*math.sin(r))
        res_list.append([rx,ry])
    res_list=translate(res_list,x,y)
    return res_list

def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    new_list=[]
    for point in p_list:
        nx,ny=point
        nx=round(x+(nx-x)*s)
        ny=round(y+(ny-y)*s)
        new_list.append([nx,ny])
    return new_list


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    if x_min>x_max:
        x_max,x_min=x_min,x_max
    if y_min>y_max:
        y_max,y_min=y_min,y_max
    result=[]
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if algorithm=="Cohen-Sutherland":
        code0=0
        code1=0
        while 1:
            code0,code1=0,0
            if x0<x_min:
                code0+=1
            if x0>x_max:
                code0+=2
            if y0<y_min:
                code0+=4
            if y0>y_max:
                code0+=8
            
            if x1<x_min:
                code1+=1
            if x1>x_max:
                code1+=2
            if y1<y_min:
                code1+=4
            if y1>y_max:
                code1+=8
            
            if (code0|code1)==0:
                return [[x0,y0],[x1,y1]]
            if (code0&code1)!=0:
                return [[0,0],[0,0]]
            
            #对code0操作
            if code0==0:
                code0,code1=code1,code0
                x0,y0,x1,y1=x1,y1,x0,y0
            if code0&1:
                y0=round(y0+(x_min-x0)*(y1-y0)/(x1-x0))
                x0=x_min
            if code0&2:
                y0=round(y0+(x_max-x0)*(y1-y0)/(x1-x0))
                x0=x_max
            if code0&4:
                x0=round(x0+(y_min-y0)*(x1-x0)/(y1-y0))
                y0=y_min
            if code0&8:
                x0=round(x0+(y_max-y0)*(x1-x0)/(y1-y0))
                y0=y_max
    elif algorithm=="Liang-Barsky":
        p=[x0-x1,x1-x0,y0-y1,y1-y0]
        q=[x0-x_min,x_max-x0,y0-y_min,y_max-y0]
        u0,u1=0,1
        for i in range(4):
            if p[i]<0:
                #入边
                u0=max(u0,q[i]/p[i])
            elif p[i]>0:
                #out
                u1=min(u1,q[i]/p[i])
            elif p[i]==0:
                if q[i]<0:
                    return [[0,0],[0,0]]
            if u0>u1:
                return [[0,0],[0,0]]
        
        r_x0=round(x0+u0*(x1-x0))
        r_y0=round(y0+u0*(y1-y0))
        r_x1=round(x0+u1*(x1-x0))
        r_y1=round(y0+u1*(y1-y0))
        result=[[r_x0,r_y0],[r_x1,r_y1]]
        return result