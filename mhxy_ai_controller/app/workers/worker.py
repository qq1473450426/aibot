import asyncio,time
from app.core.models import WorkerStatus,WorkerState
from app.core.state_machine import transition
from app.core.logging_setup import get_logger
from app.services.ai import LocalReasoningEngine

class Worker:
    def __init__(self,account,controller):
        self.controller=controller; self.account_id=account['account_id']; self.name=account['name']; self.hwnd=account.get('hwnd'); self.window_title=account.get('window_title',''); self.priority=int(account.get('priority',0)); self.status=WorkerStatus(self.account_id); self.logger=get_logger('worker',self.account_id); self.running=False; self.task_name=None; self.reasoning=LocalReasoningEngine(); self._last=None
    def log(self,level,event,msg):
        text=f'ACCOUNT={self.account_id} | STATE={self.status.state.value} | EVENT={event} | {msg}'
        getattr(self.logger,{'ERROR':'error','WARN':'warning'}.get(level,'info'))(text); self.controller.db.event(self.account_id,level,event,msg)
    def change_state(self,target):self.status.state=transition(self.status.state,target);self.controller.db.state(self.status);self.log('INFO','STATE_CHANGE',f'-> {target.value}')
    def heartbeat(self):self.status.last_heartbeat=time.time();self.controller.db.state(self.status)
    def window_info(self):return self.controller.window_manager.get_info(hwnd=self.hwnd,title=self.window_title)
    def window_exists(self):return self.window_info() is not None
    def activate_window(self):
        i=self.window_info();return bool(i and self.controller.window_manager.activate(i.hwnd))
    def is_available_for_replacement(self):return self.status.state in {WorkerState.STOPPED,WorkerState.IDLE}
    def start(self):
        if not self.running:self.running=True;self.status.state=WorkerState.STARTING;self.task_handle=asyncio.create_task(self.run())
    async def stop(self):
        self.running=False;self.status.state=WorkerState.STOPPED;self.controller.db.state(self);self.log('INFO','STOP','Worker已停止')
    def set_task(self,name):self.task_name=name;self.status.task_name=name;self.log('INFO','TASK_ASSIGN',name)
    def build_observation(self):
        info=self.window_info(); connected=info is not None; frame=self.capture() if connected else None; battle=dialog=done=False
        for f,k in [('battle_attack.png','battle'),('dialog.png','dialog'),('battle_end.png','done')]:
            try:
                m=self.controller.vision.find(frame,f,self.controller.settings['template_threshold'])
                if m:
                    if k=='battle':battle=True
                    elif k=='dialog':dialog=True
                    else:done=True
            except FileNotFoundError:pass
        return {'state':self.status.state.value,'connected':connected,'battle_detected':battle,'dialog_detected':dialog,'target_found':battle,'task_done':done,'confidence':.9 if connected else .1}
    async def run(self):
        try:
            if not self.window_exists():self.mark_error('未找到游戏窗口');return
            self.change_state(WorkerState.LOGIN);await asyncio.sleep(1);self.change_state(WorkerState.IDLE)
            while self.running:
                self.heartbeat()
                if self.task_name:
                    if self.status.state==WorkerState.IDLE:self.change_state(WorkerState.RUNNING)
                    d=self.reasoning.decide(self.account_id,self.build_observation(),{'task_name':self.task_name});self.status.last_ai_action=d.action;self.log('INFO','LOCAL_AI_DECISION',f'action={d.action} confidence={d.confidence:.2f} reason={d.reason}')
                    if d.action=='RECONNECT':self.handle_disconnect('本地推理判断需要重连')
                    elif d.action=='TASK_COMPLETE':self.task_name=None;self.status.task_name='空闲'
                    elif d.action=='WAIT':await asyncio.sleep(.5)
                    else:await self.execute_task(self.task_name)
                else:await asyncio.sleep(1)
        except asyncio.CancelledError:pass
        except Exception as e:self.mark_error(repr(e))
    async def execute_task(self,name):
        from app.services.task_runner import TaskRunner
        try:await asyncio.to_thread(TaskRunner(self).run_task,name)
        except Exception as e:self.log('ERROR','TASK_ERROR',repr(e));self.handle_disconnect('任务异常')
    def capture(self):
        frame=self.controller.capture.capture_window(self.window_info())
        if frame is not None:self.status.last_screen_change=time.time()
        return frame
    def save_screenshot(self,reason):
        p=self.controller.capture.save(self.capture(),self.account_id,reason)
        if p:self.log('INFO','SCREENSHOT',p)
        return p
    def find_click(self,template,confidence,timeout):
        end=time.time()+timeout
        while time.time()<end and self.running:
            m=self.controller.vision.find(self.capture(),template,confidence)
            if m:
                i=self.window_info();x=i.left+m['x'];y=i.top+m['y']
                if self.controller.settings['dry_run']:self.log('INFO','DRY_RUN_CLICK',f'({x},{y})');return True
                return self.controller.input.move_click(x,y)['ok']
            time.sleep(.15)
        return False
    def click_client(self,x,y):
        i=self.window_info()
        if not i:return False
        if self.controller.settings['dry_run']:self.log('INFO','DRY_RUN_CLICK',f'client=({x},{y})');return True
        return self.controller.input.move_click(i.left+x,i.top+y)['ok']
    def press_key(self,key):
        if self.controller.settings['dry_run']:self.log('INFO','DRY_RUN_KEY',key);return True
        return self.controller.input.press(key)['ok']
    def handle_disconnect(self,reason):
        self.status.error_message=reason;self.status.state=WorkerState.DISCONNECTED;self.controller.db.state(self.status);self.log('WARN','DISCONNECTED',reason);self.save_screenshot('disconnect')
    def mark_error(self,msg):
        self.status.error_message=msg;self.status.state=WorkerState.ERROR;self.controller.db.state(self.status);self.log('ERROR','ERROR',msg)
    def snapshot(self):
        i=self.window_info();return {'account_id':self.account_id,'name':self.name,'state':self.status.state.value,'task_name':self.status.task_name,'running':self.running,'hwnd':i.hwnd if i else None,'reconnect_count':self.status.reconnect_count,'last_ai_action':self.status.last_ai_action,'error_message':self.status.error_message}
