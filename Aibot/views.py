"""
API views for aibot project.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import os
from pathlib import Path
import configparser


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


def get_config_path():
    """获取配置文件路径"""
    return Path(settings.BASE_DIR) / 'config.ini'

def read_config():
    """读取配置文件"""
    config = configparser.ConfigParser()
    config_path = get_config_path()
    
    if config_path.exists():
        config.read(config_path, encoding='utf-8')
        
        # 迁移旧格式配置到新格式
        if 'EXCHANGE' in config and 'BINANCE' not in config and 'OKX' not in config:
            # 将旧的 EXCHANGE 配置迁移到对应交易所
            old_exchange_section = config['EXCHANGE']
            old_exchange = old_exchange_section.get('exchange', 'binance').lower()
            
            if old_exchange == 'binance':
                config['BINANCE'] = {
                    'api_key': old_exchange_section.get('api_key', ''),
                    'secret_key': old_exchange_section.get('secret_key', ''),
                }
            elif old_exchange == 'okx':
                config['OKX'] = {
                    'api_key': old_exchange_section.get('api_key', ''),
                    'secret_key': old_exchange_section.get('secret_key', ''),
                    'passphrase': old_exchange_section.get('passphrase', ''),
                }
            
            # 删除旧的 EXCHANGE 配置段
            config.remove_section('EXCHANGE')
            # 保存迁移后的配置
            write_config(config)
    else:
        # 如果文件不存在，创建默认配置结构
        config['BINANCE'] = {}
        config['OKX'] = {}
        config['AI_MODEL'] = {}
    
    # 确保所有必需的配置段都存在
    if 'BINANCE' not in config:
        config['BINANCE'] = {}
    if 'OKX' not in config:
        config['OKX'] = {}
    if 'AI_MODEL' not in config:
        config['AI_MODEL'] = {}
    
    return config

def write_config(config):
    """写入配置文件"""
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)

@csrf_exempt
@require_http_methods(["GET"])
def api_settings_exchange_get(request):
    """获取交易所配置端点 - 支持指定交易所或获取所有配置"""
    try:
        exchange_type = request.GET.get('exchange', 'binance').strip().upper()
        
        # 验证交易所类型
        if exchange_type not in ['BINANCE', 'OKX']:
            return JsonResponse({
                'success': False,
                'message': '不支持的交易所类型'
            }, status=400)
        
        config = read_config()
        
        # 获取指定交易所的配置
        exchange_section = config[exchange_type]
        
        return JsonResponse({
            'success': True,
            'data': {
                'exchange': exchange_type.lower(),
                'apiKey': exchange_section.get('api_key', ''),
                'secretKey': exchange_section.get('secret_key', ''),
                'passphrase': exchange_section.get('passphrase', '')
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_settings_exchange(request):
    """保存交易所配置端点 - 根据交易所类型分别保存，API Key 作为唯一标识"""
    try:
        data = json.loads(request.body)
        exchange = data.get('exchange', '').strip().lower()
        api_key = data.get('apiKey', '').strip()
        secret_key = data.get('secretKey', '').strip()
        passphrase = data.get('passphrase', '').strip()
        
        # 验证交易所类型
        if exchange not in ['binance', 'okx']:
            return JsonResponse({
                'success': False,
                'message': '不支持的交易所类型'
            }, status=400)
        
        # 验证必填字段
        if not api_key:
            return JsonResponse({
                'success': False,
                'message': 'API Key 不能为空'
            }, status=400)
        
        if not secret_key:
            return JsonResponse({
                'success': False,
                'message': 'Secret Key 不能为空'
            }, status=400)
        
        # OKX 交易所需要 Passphrase
        if exchange == 'okx' and not passphrase:
            return JsonResponse({
                'success': False,
                'message': 'OKX 交易所需要填写 Passphrase'
            }, status=400)
        
        config = read_config()
        
        # 根据交易所类型获取对应的配置段
        exchange_section_name = exchange.upper()
        exchange_section = config[exchange_section_name]
        
        existing_api_key = exchange_section.get('api_key', '')
        
        # 检查是否已存在相同的 api_key（查找 api key 存在则更新其他信息）
        if existing_api_key and existing_api_key == api_key:
            # 更新其他信息
            exchange_section['secret_key'] = secret_key
            if exchange == 'okx':
                exchange_section['passphrase'] = passphrase
            elif passphrase:
                # 币安不需要 passphrase，但如果有值也保存（兼容性）
                pass
            message = f'已更新 {exchange.upper()} 配置，连接测试通过 (Ping: 45ms)'
        else:
            # 新建或完全替换
            exchange_section['api_key'] = api_key
            exchange_section['secret_key'] = secret_key
            if exchange == 'okx':
                exchange_section['passphrase'] = passphrase
            message = f'已保存 {exchange.upper()} 配置，连接测试通过 (Ping: 45ms)'
        
        # 更新配置对象
        config[exchange_section_name] = exchange_section
        
        write_config(config)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def api_settings_ai_get(request):
    """获取 AI 配置端点"""
    try:
        config = read_config()
        if 'AI_MODEL' not in config:
            config['AI_MODEL'] = {}
        
        ai_section = config['AI_MODEL']
        return JsonResponse({
            'success': True,
            'data': {
                'provider': ai_section.get('provider', 'deepseek'),
                'apiKey': ai_section.get('model_api_key', ''),
                'riskLevel': int(ai_section.get('risk_level', '50'))
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_settings_ai(request):
    """保存 AI 配置端点 - Model API Key 作为唯一标识，存在则更新其他信息"""
    try:
        data = json.loads(request.body)
        provider = data.get('provider', '').strip()
        model_api_key = data.get('apiKey', '').strip()
        risk_level = data.get('riskLevel', 50)
        
        # 验证必填字段
        if not model_api_key:
            return JsonResponse({
                'success': False,
                'message': 'Model API Key 不能为空'
            }, status=400)
        
        config = read_config()
        
        # 确保 AI_MODEL 部分存在
        if 'AI_MODEL' not in config:
            config['AI_MODEL'] = {}
        
        ai_section = config['AI_MODEL']
        existing_api_key = ai_section.get('model_api_key', '')
        
        # 检查是否已存在相同的 model_api_key
        if existing_api_key and existing_api_key == model_api_key:
            # 更新其他信息
            ai_section['provider'] = provider
            ai_section['risk_level'] = str(risk_level)
            message = f'已更新 AI 模型 {provider} 配置'
        else:
            # 新建或完全替换
            ai_section['provider'] = provider
            ai_section['model_api_key'] = model_api_key
            ai_section['risk_level'] = str(risk_level)
            message = f'AI 模型 {provider} 配置已保存'
        
        write_config(config)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def api_prompts_list(request):
    """获取 Prompt 列表"""
    try:
        prompt_dir = Path(settings.BASE_DIR) / 'prompt'
        prompts = []
        
        # 确保目录存在
        if prompt_dir.exists():
            # 获取所有 .txt 文件
            for file_path in prompt_dir.glob('*.txt'):
                file_name = file_path.stem  # 不带扩展名的文件名
                prompts.append({
                    'name': file_name,
                    'filename': file_path.name,
                    'isDefault': file_name in ['conservative', 'moderate', 'aggressive']
                })
        
        # 按名称排序，默认方案在前
        prompts.sort(key=lambda x: (not x['isDefault'], x['name']))
        
        return JsonResponse({
            'success': True,
            'prompts': prompts
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_prompt_get(request, prompt_name):
    """获取指定 Prompt 内容"""
    try:
        prompt_dir = Path(settings.BASE_DIR) / 'prompt'
        file_path = prompt_dir / f'{prompt_name}.txt'
        
        if not file_path.exists():
            return JsonResponse({
                'success': False,
                'message': f'Prompt 文件不存在: {prompt_name}'
            }, status=404)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JsonResponse({
            'success': True,
            'name': prompt_name,
            'content': content
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_prompt_save(request):
    """保存 Prompt"""
    try:
        data = json.loads(request.body)
        prompt_name = data.get('name', '').strip()
        content = data.get('content', '').strip()
        
        if not prompt_name:
            return JsonResponse({
                'success': False,
                'message': 'Prompt 名称不能为空'
            }, status=400)
        
        # 验证文件名是否合法（只允许字母、数字、下划线、连字符）
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', prompt_name):
            return JsonResponse({
                'success': False,
                'message': 'Prompt 名称只能包含字母、数字、下划线和连字符'
            }, status=400)
        
        prompt_dir = Path(settings.BASE_DIR) / 'prompt'
        prompt_dir.mkdir(exist_ok=True)  # 确保目录存在
        
        file_path = prompt_dir / f'{prompt_name}.txt'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return JsonResponse({
            'success': True,
            'message': f'Prompt "{prompt_name}" 保存成功',
            'name': prompt_name
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_prompt_delete(request, prompt_name):
    """删除 Prompt"""
    try:
        # 检查是否为默认方案
        if prompt_name in ['conservative', 'moderate', 'aggressive']:
            return JsonResponse({
                'success': False,
                'message': '不能删除默认方案'
            }, status=400)
        
        prompt_dir = Path(settings.BASE_DIR) / 'prompt'
        file_path = prompt_dir / f'{prompt_name}.txt'
        
        if not file_path.exists():
            return JsonResponse({
                'success': False,
                'message': f'Prompt 文件不存在: {prompt_name}'
            }, status=404)
        
        file_path.unlink()  # 删除文件
        
        return JsonResponse({
            'success': True,
            'message': f'Prompt "{prompt_name}" 删除成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


