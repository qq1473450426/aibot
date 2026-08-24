from pathlib import Path
import cv2

class VisionService:
    def __init__(self,threshold=.88): self.threshold=threshold; self.cache={}
    def _load(self,template):
        if template not in self.cache:
            img=cv2.imread(str(Path('assets/templates')/template))
            if img is None: raise FileNotFoundError(f'模板不存在：{template}')
            self.cache[template]=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        return self.cache[template]
    def find(self,frame,template,threshold=None):
        if frame is None:return None
        tpl=self._load(template); gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        if gray.shape[0]<tpl.shape[0] or gray.shape[1]<tpl.shape[1]:return None
        r=cv2.matchTemplate(gray,tpl,cv2.TM_CCOEFF_NORMED); _,v,_,loc=cv2.minMaxLoc(r)
        if v<(self.threshold if threshold is None else threshold):return None
        h,w=tpl.shape[:2]
        return {'confidence':float(v),'x':int(loc[0]+w/2),'y':int(loc[1]+h/2),'w':w,'h':h}
