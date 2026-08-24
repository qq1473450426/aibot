import json,time
from pathlib import Path
class TaskRunner:
    def __init__(self,worker):self.worker=worker
    def load(self,name):return json.loads((Path('tasks')/f'{name}.json').read_text(encoding='utf-8'))
    def run_task(self,name):
        task=self.load(name)
        while self.worker.running:
            for step in task.get('steps',[]):
                if not self.worker.running:return
                typ=step.get('type')
                if typ=='wait':time.sleep(float(step.get('seconds',1)))
                elif typ=='key':self.worker.press_key(step['key'])
                elif typ=='click':self.worker.click_client(int(step['x']),int(step['y']))
                elif typ=='find_click':self.worker.find_click(step['template'],float(step.get('confidence',.88)),float(step.get('timeout',5)))
                elif typ=='screenshot':self.worker.save_screenshot(step.get('reason','manual'))
            if not task.get('loop',False):return
