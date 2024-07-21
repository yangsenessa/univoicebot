import cv2
from ..tonwallet import config
from  loguru import logger
import os
'''
#加载背景图片
bk_img = cv2.imread("background.jpg")
#在图片上添加文字信息
cv2.putText(bk_img,"Hello World", (100,300), cv2.FONT_HERSHEY_SIMPLEX, 
0.7,(255,255,255), 1, cv2.LINE_AA)
#显示图片
cv2.imshow("add_text",bk_img)
cv2.waitKey()
#保存图片
cv2.imwrite("add_text.jpg",bk_img)
'''



def marked_record_suc(user_id:str,text:str, img_path:str,abs_path:str):
    
    imageout:str
    bk_img = cv2.imread(img_path)
    cv2.putText(bk_img,"Upload successful!", (431,80), cv2.FONT_HERSHEY_SIMPLEX, 
1.6,(255,255,255), 5, cv2.LINE_8)
    cv2.putText(bk_img,text, (431,185), cv2.FONT_HERSHEY_SIMPLEX, 
1.6,(255,255,255), 5, cv2.LINE_8)
    cv2.putText(bk_img,"You can claim them", (431,295), cv2.FONT_HERSHEY_SIMPLEX, 
1.2,(255,255,255), 5, cv2.LINE_8)
   
        #cv2.imshow(f"{user_id}",bk_img)
    imageout= os.path.join(abs_path,f"{user_id}.jpg")
    cv2.imwrite(imageout,bk_img)
    return imageout
        
def marked_record_update(user_id:str, texts:list,img_path:str,abs_path:str )  :
    imageout:str
    bk_img = cv2.imread(img_path)
    x_loc = 65
    for text in texts :
       cv2.putText(bk_img,text, (510,x_loc), cv2.FONT_HERSHEY_SIMPLEX, 
                    1.2,(255,255,255), 3, cv2.LINE_8)
       x_loc += 45
    imageout= os.path.join(abs_path,f"{user_id}.jpg")
    cv2.imwrite(imageout,bk_img)
    return imageout

def marked_claim_notify(user_id:str, texts:list,img_path:str,abs_path:str )  :
    imageout:str
    bk_img = cv2.imread(img_path)
    x_loc = 135
    i = 0
    for text in texts :
       if i==0:
          cv2.putText(bk_img,text, (435,x_loc), cv2.FONT_HERSHEY_SIMPLEX, 
                    2,(255,255,255), 5, cv2.LINE_8) 
       else:
          cv2.putText(bk_img,text, (435,x_loc), cv2.FONT_HERSHEY_SIMPLEX, 
                        2,(255,255,255), 5, cv2.LINE_8)
       x_loc += 85
       i+=1
    imageout= os.path.join(abs_path,f"{user_id}.jpg")
    cv2.imwrite(imageout,bk_img)
    return imageout

def marked_claimed(user_id:str, texts:list,img_path:str,abs_path:str )  :
    imageout:str
    bk_img = cv2.imread(img_path)
    x_loc = 85
    for text in texts :
       cv2.putText(bk_img,text, (435,x_loc), cv2.FONT_HERSHEY_SIMPLEX, 
                    1.5,(255,255,255), 3, cv2.LINE_8)
       x_loc += 95
    imageout= os.path.join(abs_path,f"{user_id}.jpg")
    cv2.imwrite(imageout,bk_img)
    return imageout

def marked_claimed_invited(user_id:str, texts:list,img_path:str,abs_path:str )  :
    imageout:str
    bk_img = cv2.imread(img_path)
    x_loc = 185
    for text in texts :
       cv2.putText(bk_img,text, (580,x_loc), cv2.FONT_HERSHEY_SIMPLEX, 
                    2,(255,255,255), 3, cv2.LINE_8)
       x_loc += 95
    imageout= os.path.join(abs_path,f"{user_id}.jpg")
    cv2.imwrite(imageout,bk_img)
    return imageout


