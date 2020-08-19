import cv2
import numpy as np
from PIL import Image
from PIL import ImageStat

def get_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # 灰階處理
    blur = cv2.GaussianBlur(gray, (13, 13), 0)        # 高斯模糊
    canny = cv2.Canny(blur,160,180)                # 邊緣偵測
    return canny
def get_canny(blur,low,high):
    canny=cv2.Canny(blur,low,high)
    return canny

def get_roi(img):
    mask = np.zeros_like(img)          # 全黑遮罩
    points = np.array([[[310, 931], [823, 622], [1310, 583], [1530, 737]]]) #vios0816
    # points = np.array([[[344, 753],[747, 497],[1621, 710],[1150, 482]]]) #vios0813a
    # points = np.array([[[223, 1020], [642, 772], [1021, 764], [1507, 1034]]]) #vios
    # points = np.array([[[223, 1020], [792, 697], [927, 714], [1507, 1034]]])  # yaris
    cv2.fillPoly(mask, points, 255)    # 多邊三角形
    roi = cv2.bitwise_and(img, mask)
    return roi

def draw_lines(img, lines):                 # 建立自訂函式
    for line in lines:
        points = line.reshape(4,)       # 降成一維 shape = (4,)
        x1, y1, x2, y2 = points         # 取出直線座標
        cv2.line(img,                   # 繪製直線
                 (x1, y1), (x2, y2),
                 (0, 0, 255), 3)
    return img

def get_avglines(lines):
    if lines is None:                   # 如果有找到線段
        print('偵測不到直線線段')
        return None
    #-----↓先依斜率分到左組或右組↓
    lefts = []
    rights = []
    for line in lines:
        points = line.reshape(4,)
        x1, y1, x2, y2 = points
        slope, b = np.polyfit((x1, x2), (y1, y2), 1)  # y = slope*x + b
        # print(f'y = {slope} x + {b}')  #若有需要可將斜率與截距印出
        if slope > 0:   # 斜率 > 0, 右邊的直線函數
            rights.append([slope, b])  # 以 list 存入
        else:       # 斜率 < 0, 左邊的直線函數
            lefts.append([slope, b])  # 以 list 存入

    #-----↓再計算左組與右組的平圴線↓
    if rights and lefts:     # 必須同時有左右兩邊的直線函數
        right_avg = np.average(rights, axis=0)    # 取得右邊的平均直線
        left_avg = np.average(lefts, axis=0)      # 取得左邊的平均直線
        return np.array([right_avg, left_avg])
    else:
        print('無法同時偵測到左右邊緣')
        return None
def get_sublines(img,avglines,a,c,d):
    sublines=[]
    x_1=0.5*(a+c)
    y=d
    for line in avglines:
        slope,b = line
        y1=img.shape[0]
        y2=int(y1*(0.68))
        x1=int(((y1 - b) / slope))
        x2=int((y2 - b) / slope)
        sublines.append([x1, y1, x2, y2])
        ans=1
        #偵測檢測點是否有跟車道線交叉
        # ========================試試看去絕對值====================
        if abs(slope*x_1+b-d)>0.2*abs(c-a):
            ans=0 #維持現狀
        if abs(slope*x_1+b-d)<=0.2*abs(c-a):
            ans=1 #開啟標示
        if ((slope*a+b-d)>=-2 and (slope*a+b-d)<=0)or ((slope*c+b-d)>=-2 and (slope*c+b-d)<=0):
            ans=2 #關閉標示
    return np.array(sublines),ans
def get_brightness_left(img,a,b,c,d):
    # ==============輸入座標為YOLO_方向燈模型==============
    x_target = int(0.5 * (a + c) - 8)
    y_target = int(0.5 * (b + d))
    h_target = int(abs(0.7 * (b - d)))
    w_target = int(abs(0.8 * (c - a)))
    crop_img = img[y_target:y_target + h_target, x_target:x_target + w_target]
    # cv2.imshow("cropped", crop_img)
    im = Image.fromarray(cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
    img = im.convert('L')
    stat = ImageStat.Stat(img)
    if stat.mean[0] > 135:
        return 1
    else:
        return 0
    # mask = np.zeros_like(img)# 全黑遮罩
    # point_left = np.array([[[int(a+3),int(b-0.3*(b-d))], [int(a+0.25*(c-a)),int(b-0.3*(b-d))], [int(a+0.25*(c-a)), int(b-0.55*(b-d))],[int(a+3),int(b-0.55*(b-d))]]])
    # cv2.fillPoly(mask, point_left,  255)    # 多邊三角形 只吃int值
    # roi = cv2.bitwise_and(img, mask)
    # im = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    # img = im.convert('L')
    # print(img)
   # ====================================圖像分割=================================
   #  x=int(a+0.4*(c-a))
   #  y=int(b-0.3*(b-d))
   #  h = int(abs(0.3 * (b - d)))
   #  w = int(abs(0.3 * (c - a)))
   #=======================柏油路========================
    # x = int(a + 0.4 * (c - a))
    # y = int(d+200)
    # h = int(abs(0.2 * (b - d)))
    # w = int(abs(0.2 * (c - a)))
    # crop_img = img[y:y + h, x:x + w]
   # =======================左方向燈========================
   #  x_target = int(a + 15)
   #  y_target = int(b - 0.3 * (b - d))
   #  h_target = int(abs(0.2 * (b - d)))
   #  w_target = int(abs(0.18 * (c - a)))

    # =======================右方向燈========================
    # x_target = int(c-abs(0.45 * (c - a)+10))
    # y_target = int(b - 0.3 * (b - d))
    # h_target = int(abs(0.2 * (b - d)))
    # w_target = int(abs(0.45 * (c - a)))
    # crop_img = img[y_target:y_target + h_target, x_target:x_target + w_target]
    # # cv2.imshow("cropped", crop_img)
    # im = Image.fromarray(cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
    # img = im.convert('L')
    # stat = ImageStat.Stat(img)
    # return stat.mean[0]
    # class brightness:
    #     mask = np.zeros_like(img)  # 全黑遮罩
    #     def point_get(self,x1,x2,y1,y2):
    #         self.point=np.array([[[self.x1,self.y1], [self.x1,self.y2], [self.x2,self.y2],[self.x2,self.y1]]])
    #         return self.point
    #     def roi_get(self,point):
    #         self.roi = cv2.bitwise_and(img,self.mask) #img不知道會不會error
    #         return self.roi
    #     def brightness_get(self,roi):
    #         im = Image.fromarray(cv2.cvtColor(self.roi, cv2.COLOR_BGR2RGB))
    #         img = im.convert('L')
    #         stat = ImageStat.Stat(img)
    #         return stat
def get_brightness_right(img,a,b,c,d):
    x1 = int(c - 5)
    y1 = int(b - 0.3 * (b - d))
    x2 = int(c - 0.25 * (c - a))
    y2 = int(b - 0.55 * (b - d))
    mask = np.zeros_like(img)  # 全黑遮罩
    point_right = np.array([[[x1, y1], [x1, y2], [x2, y2], [x2, y1]]])
    cv2.fillPoly(mask, point_right, 255)  # 多邊三角形 只吃int值
    roi = cv2.bitwise_and(img, mask)
    im = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    img = im.convert('L')
    stat = ImageStat.Stat(img)
    # print(stat.mean[0])
    return stat.mean[0]

def get_roi_brightness(img,a,b,c,d):
    mask = np.zeros_like(img)
    points = np.array([[[int(a+0.4*(c-a)),int(b-0.5*(b-d))], [int(a+0.6*(c-a)),int(b-0.5*(b-d))], [int(a+0.4*(c-a)), int(b-0.7*(b-d))],[int(a+0.4*(c-a)),int(b-0.5*(b-d))]]])
    cv2.fillPoly(mask, points, 255)    # 多邊三角形
    roi = cv2.bitwise_and(img, mask)
    cv2.imshow('left', roi)
    # im = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    # img = im.convert('L')
    # stat = ImageStat.Stat(img)
    # return stat.mean[0]




