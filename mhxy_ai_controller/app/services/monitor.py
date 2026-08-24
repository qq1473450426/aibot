import asyncio,time
class Monitor:
    def __init__(self,controller):self.controller=controller;self.running=False
    async def run(self):
        self.running=True
        while self.running:
            now=time.time()
            for w in list(self.controller.workers.values()):
                if not w.running:continue
                if not w.window_exists():w.handle_disconnect('游戏窗口不存在');continue
                if now-w.status.last_heartbeat>self.controller.settings['heartbeat_timeout']:w.mark_error('Worker heartbeat超时')
                if now-w.status.last_screen_change>self.controller.settings['screen_idle_timeout']:w.log('WARN','SCREEN_IDLE','画面长时间没有变化')
            await asyncio.sleep(self.controller.settings['monitor_interval'])
    def stop(self):self.running=False
