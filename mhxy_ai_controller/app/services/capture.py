from pathlib import Path
import time, cv2, numpy as np
from PIL import ImageGrab

class CaptureService:
    def capture_window(self,window_info):
        if not window_info:return None
        img=ImageGrab.grab(bbox=(window_info.left,window_info.top,window_info.right,window_info.bottom))
        return cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
    def save(self,frame,account_id,reason):
        if frame is None:return None
        root=Path('screenshots')/account_id; root.mkdir(parents=True,exist_ok=True)
        path=root/f'{int(time.time())}_{reason}.png'; cv2.imwrite(str(path),frame); return str(path)
