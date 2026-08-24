from dataclasses import dataclass, field
from typing import Any

@dataclass
class CandidateAction:
    action: str
    score: float
    reason: str
    params: dict[str, Any] = field(default_factory=dict)

@dataclass
class Decision:
    action: str
    confidence: float
    reason: str
    params: dict[str, Any] = field(default_factory=dict)
    alternatives: list[CandidateAction] = field(default_factory=list)

class LocalReasoningEngine:
    """纯本地 Agent 决策器：感知→候选动作→评分→记忆→下一轮。"""
    def __init__(self):
        self.memory = {}

    def mem(self, account_id):
        return self.memory.setdefault(account_id, {"last_action":"", "last_result":"", "failed":{}, "repeat":0})

    def remember_result(self, account_id, action, result):
        m=self.mem(account_id)
        m["repeat"] = m["repeat"]+1 if m["last_action"]==action else 1
        m["last_action"]=action; m["last_result"]=result
        if result != "success":
            m["failed"][action]=m["failed"].get(action,0)+1

    def candidates(self, obs):
        state=obs.get("state","UNKNOWN"); connected=obs.get("connected",True)
        battle=obs.get("battle_detected",False); dialog=obs.get("dialog_detected",False)
        task_done=obs.get("task_done",False); target=obs.get("target_found",False)
        confidence=float(obs.get("confidence",0.0)); c=[]
        if not connected: c.append(CandidateAction("RECONNECT",1.0,"连接异常优先恢复"))
        if task_done: c.append(CandidateAction("TASK_COMPLETE",0.99,"任务已完成"))
        if battle and target: c.append(CandidateAction("BATTLE_ACTION",0.93,"战斗且目标明确"))
        elif battle: c.append(CandidateAction("WAIT_BATTLE",0.72,"战斗中目标不确定"))
        if dialog: c.append(CandidateAction("HANDLE_DIALOG",0.86,"发现对话界面"))
        if state in ("IDLE","RUNNING") and connected and not task_done:
            c.append(CandidateAction("CONTINUE_TASK",0.82+min(confidence,0.15),"任务仍在运行"))
        c.append(CandidateAction("WAIT",0.35,"证据不足，先观察")); return c

    def decide(self, account_id, observation, task):
        m=self.mem(account_id); c=self.candidates(observation)
        for x in c:
            x.score -= min(m["failed"].get(x.action,0)*0.08,0.30)
            if x.action==m["last_action"] and m["repeat"]>=4: x.score-=0.20
        if m["repeat"]>=4: c.append(CandidateAction("WAIT",0.70,"同一动作重复过多，先观察"))
        c.sort(key=lambda x:x.score, reverse=True); best=c[0]
        return Decision(best.action,max(0,min(1,best.score)),best.reason,best.params,c[:5])
