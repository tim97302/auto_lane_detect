import cv2
import autolane_module as m
import numpy as np
import pandas as pd
import turn_signal as turn


def lane(img,a,b,c,d,p):
    # ==============查看P值變化，是否有作用============
    # data_row = [p]
    # data.append(data_row)
    # columns = ['p']
    # df = pd.DataFrame(data=data, columns=columns)
    # df.to_csv('./check.csv', index=0)
    # =========做判斷亮度，若有在圖上加工標示============
    left_brightness=m.get_brightness_left(img,a,b,c,d)      # 取得車燈亮度，輸入為yolo車燈區域座標
    text="turn_signal"
    if left_brightness==1:
        cv2.putText(img, text, (10,180), cv2.FONT_HERSHEY_PLAIN,3, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.rectangle(img, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
    # print(left_brightness)
    # =====================車道線辨識===================
    edge = m.get_edge(img)                  # 邊緣偵測
    roi = m.get_roi(edge)                   # 取得 ROI
    lines = cv2.HoughLinesP(image=roi,      # Hough 轉換
                            rho=3,
                            theta=np.pi/180,
                            threshold=30,
                            minLineLength=20,
                            maxLineGap=50)
    avglines = m.get_avglines(lines)          # 取得左右 2 條平均線方程式
    # p = 0
    # ======================切車道辨識=====================
    text = "cross_lane"
    if avglines is None and p==1:
        cv2.putText(img, text, (10, 80), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3, cv2.LINE_AA)
    if avglines is not None:
        lines = m.get_sublines(img, avglines,a,c,d)  # 取得要畫出的左右 2 條線段，並以check_point判斷是否有切車道
        img = m.draw_lines(img, lines[0])  # 畫出線段
        ans=lines[1]
        if ans==1:
            p=1
        if ans==2:
            p=0
        if (ans==0 and p==1) or (ans==1 and p==1):
            cv2.putText(img, text, (10, 80), cv2.FONT_HERSHEY_PLAIN,3, (255, 0, 0), 3, cv2.LINE_AA)


    # print("p,ans",p,ans)
# ===========================================解釋==============================================
        # cv2.putText(影像, 文字,  座標,            字型,        大小, 顏色,    線條寬度, 線條種類)
        # print(img.shape)
        # cv2.imshow('Frame', img)

    # cv2.imshow('Frame', img)  # 顯示影像
    return img,p #P為feedback
    k = cv2.waitKey(1)  # 等待按鍵輸入
    if k == ord('q') or k == ord('Q'):  # 按下 Q(q) 結束迴圈
        print('exit')
        cv2.destroyAllWindows()  # 關閉視窗


