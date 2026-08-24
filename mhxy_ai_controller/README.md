# 梦幻西游 AI 多账号主控板（本地 AI 思维版）

这是一个 Windows 桌面自动化与本地 Agent 决策框架。

## 核心架构

```text
游戏窗口
  ↓
截图 / 模板识别
  ↓
结构化观测
  ↓
LocalReasoningEngine
  ↓
候选动作评分
  ↓
历史失败降权 / 重复动作抑制
  ↓
执行动作
  ↓
结果验证与记忆
  ↓
下一轮
```

本版本**不调用任何外部 AI API**，不需要 API Key。

包含：

- 多账号 Worker
- Windows 窗口绑定
- OpenCV 模板识别
- 鼠标/键盘执行
- 本地 Agent 决策
- Monitor 看门狗
- 掉线检测与重连状态机
- 自动换号调度
- SQLite 事件日志
- 每账号日志
- 异常截图
- 任务 JSON 配置
- `xyq-skills` 知识库接口
- dry-run 安全测试模式

## 安装

Windows 10/11 + Python 3.11。

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

打开 `http://127.0.0.1:8000`。

第一次保持 `config/config.json` 中 `dry_run=true`。

## 账号配置

编辑 `config/accounts.json`，可以填写 HWND；如果 HWND 为空，Worker 会按窗口标题寻找。

## 模板

将游戏按钮截图放到 `assets/templates/`，例如：

- `battle_attack.png`
- `battle_end.png`
- `dialog.png`
- `reconnect.png`

## 任务

任务放在 `tasks/`，使用 JSON 定义 `wait`、`key`、`click`、`find_click`、`screenshot`。

## 本地 AI 思维

`app/services/ai.py` 实现本地结构化推理：

1. 感知当前状态
2. 生成候选动作
3. 条件评分
4. 对失败动作降权
5. 对连续重复动作降权
6. 选择最高分动作
7. 执行
8. 记录结果
9. 下一轮重新判断

这是可审计的本地 Agent 决策机制，不是云端大模型隐藏思维链。

## 日志

```text
logs/controller.log
logs/account_A01.log
logs/account_A02.log
 data/mhxy.db
 screenshots/
```

## xyq-skills

可将知识库放到 `knowledge/xyq-skills`，例如：

```bat
git clone https://github.com/MikiVision/xyq-skills.git knowledge/xyq-skills
```

## 注意

本项目不实现封包伪造、协议篡改、进程注入或反作弊绕过。实际使用前请确认客户端和账号规则允许自动化行为。
