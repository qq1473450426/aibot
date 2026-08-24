import asyncio,json
from pathlib import Path
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.logging_setup import get_logger
from app.services.database import Database
from app.services.window_manager import WindowManager
from app.services.capture import CaptureService
from app.services.vision import VisionService
from app.services.input_controller import InputController
from app.services.scheduler import Scheduler
from app.services.monitor import Monitor
from app.services.knowledge import KnowledgeService
from app.workers.worker import Worker

BASE=Path(__file__).resolve().parents[2]
SETTINGS=json.loads((BASE/'config/config.json').read_text(encoding='utf-8')); ACCOUNTS=json.loads((BASE/'config/accounts.json').read_text(encoding='utf-8'))
app=FastAPI(title='MHXY Local AI Controller'); app.mount('/static',StaticFiles(directory=BASE/'static'),name='static'); templates=Jinja2Templates(directory=BASE/'templates')
db=Database(); window_manager=WindowManager(); capture=CaptureService(); vision=VisionService(SETTINGS['template_threshold']); input_controller=InputController(SETTINGS['dry_run']); scheduler=Scheduler(); knowledge=KnowledgeService(); workers={}; monitor=None; monitor_task=None; logger=get_logger('controller')

class Controller:
    def __init__(self):self.workers=workers;self.db=db;self.settings=SETTINGS;self.window_manager=window_manager;self.capture=capture;self.vision=vision;self.input=input_controller
controller=Controller()

@app.on_event('startup')
async def startup():
    global monitor,monitor_task
    for a in ACCOUNTS:
        if a.get('enabled',True):
            w=Worker(a,controller);workers[w.account_id]=w;scheduler.register(w)
    monitor=Monitor(controller);monitor_task=asyncio.create_task(monitor.run());logger.info('主控启动 Worker=%s dry_run=%s',len(workers),SETTINGS['dry_run'])

@app.on_event('shutdown')
async def shutdown():
    if monitor:monitor.stop()
    if monitor_task:monitor_task.cancel()
    for w in workers.values():await w.stop()

@app.get('/',response_class=HTMLResponse)
async def index(request:Request):return templates.TemplateResponse('index.html',{'request':request,'dry_run':SETTINGS['dry_run']})
@app.get('/api/status')
async def status():return {'dry_run':SETTINGS['dry_run'],'workers':[w.snapshot() for w in workers.values()],'knowledge_available':knowledge.available()}
@app.get('/api/windows')
async def windows():return [{'hwnd':w.hwnd,'title':w.title,'left':w.left,'top':w.top,'right':w.right,'bottom':w.bottom,'width':w.width,'height':w.height} for w in window_manager.enumerate_windows()]
@app.get('/api/logs')
async def logs(limit:int=200):return JSONResponse(db.recent_events(max(1,min(500,limit))))
@app.post('/api/account/{account_id}/start')
async def start(account_id):
    w=workers.get(account_id)
    if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
    w.start();return {'ok':True}
@app.post('/api/account/{account_id}/stop')
async def stop(account_id):
    w=workers.get(account_id)
    if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
    await w.stop();return {'ok':True}
@app.post('/api/account/{account_id}/task')
async def task(account_id,request:Request):
    w=workers.get(account_id)
    if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
    d=await request.json();w.set_task(d['task_name']);w.start();return {'ok':True}
@app.post('/api/account/{account_id}/screenshot')
async def screenshot(account_id):
    w=workers.get(account_id)
    if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
    return {'ok':bool(w.save_screenshot('manual'))}
@app.post('/api/account/{account_id}/simulate-disconnect')
async def simulate(account_id):
    w=workers.get(account_id)
    if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
    w.handle_disconnect('Web控制台模拟掉线');return {'ok':True}
@app.get('/api/knowledge/search')
async def ksearch(q:str):return {'query':q,'results':knowledge.search(q)}
