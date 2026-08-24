import asyncio
class ReconnectManager:
    def __init__(self,worker,max_attempts,interval):self.worker=worker;self.max_attempts=max_attempts;self.interval=interval
    async def run(self):
        for i in range(1,self.max_attempts+1):
            self.worker.status.reconnect_count=i; self.worker.log('INFO','RECONNECT_ATTEMPT',f'第{i}次重连'); self.worker.activate_window(); await asyncio.sleep(self.interval)
            if self.worker.window_exists():self.worker.log('INFO','RECONNECT_SUCCESS',f'第{i}次重连窗口恢复');return True
        self.worker.log('WARN','RECONNECT_FAILED','重连次数耗尽');return False
