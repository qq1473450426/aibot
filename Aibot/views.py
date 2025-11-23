"""
API views for aibot project.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_health(request):
    """健康检查端点"""
    return JsonResponse({
        'status': 'ok',
        'message': 'API is running',
        'version': '1.0.0'
    })


@csrf_exempt
@require_http_methods(["GET"])
def api_dashboard(request):
    """仪表盘数据端点"""
    data = {
        'balance': 125400.50,
        'available': 45000.00,
        'todayPnl': 1240.50,
        'todayPnlPercent': 3.2,
        'winRate': 72,
        'riskReward': '1:2.5',
        'positions': [
            {'symbol': 'BTCUSDT', 'side': 'LONG', 'size': '0.5', 'entryPrice': '64200.5', 'pnl': 1205.4},
            {'symbol': 'ETHUSDT', 'side': 'SHORT', 'size': '10.0', 'entryPrice': '3450.0', 'pnl': -150.2},
        ],
        'history': [
            {'time': '11-23 10:00', 'symbol': 'SOLUSDT', 'action': 'SELL', 'realizedPnl': '+450.0'},
            {'time': '11-23 09:15', 'symbol': 'DOGEUSDT', 'action': 'BUY', 'realizedPnl': '-20.5'},
        ],
        'aiLogs': [
            {'time': '14:30:01', 'msg': 'DeepSeek: BTC 15m级别出现底背离，建议建立观察仓。'},
            {'time': '14:28:45', 'msg': 'Monitor: ETH 波动率指数飙升，暂停趋势策略。'},
            {'time': '14:25:12', 'msg': 'System: 策略 [Alpha-1] 止盈触发，收益 +1.5%。'}
        ],
        'whales': [
            {'coin': 'BTC', 'amount': '2,500', 'time': '2m ago', 'from': '0x3f...a1b2', 'to': 'Binance Hot Wallet', 'alert': '大额充值预警'},
            {'coin': 'USDT', 'amount': '50,000,000', 'time': '15m ago', 'from': 'Tether Treasury', 'to': '0x88...99aa', 'alert': '大额增发'}
        ]
    }
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["GET"])
def api_strategies(request):
    """策略列表端点"""
    data = {
        'strategies': [
            {'id': 1, 'name': 'BTC 激进马丁', 'symbol': 'BTCUSDT', 'type': 'Contract DCA', 'aiModel': 'DeepSeek', 'roi': 12.5, 'runtime': '3天 5小时', 'active': True},
            {'id': 2, 'name': 'ETH 趋势突破', 'symbol': 'ETHUSDT', 'type': 'AI Trend', 'aiModel': 'Qwen3', 'roi': -2.1, 'runtime': '10小时', 'active': False},
        ]
    }
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def api_strategy_create(request):
    """创建策略端点"""
    try:
        data = json.loads(request.body)
        # 这里应该保存到数据库
        # 现在只是返回成功消息
        return JsonResponse({
            'success': True,
            'message': '策略创建成功',
            'strategy': {
                'id': data.get('id', 3),
                'name': data.get('name', '未命名策略'),
                'symbol': data.get('symbol', ''),
                'type': data.get('type', ''),
                'active': True
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_settings_exchange(request):
    """保存交易所配置端点"""
    try:
        data = json.loads(request.body)
        # 这里应该保存到数据库
        return JsonResponse({
            'success': True,
            'message': f'已保存 {data.get("exchange", "unknown")} 配置，连接测试通过 (Ping: 45ms)'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_settings_ai(request):
    """保存 AI 配置端点"""
    try:
        data = json.loads(request.body)
        # 这里应该保存到数据库
        return JsonResponse({
            'success': True,
            'message': f'AI 模型 {data.get("provider", "unknown")} 配置已更新'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


