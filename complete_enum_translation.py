#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完成所有枚举成员的翻译"""

import json
import re

# 完整翻译词典
TRANSLATIONS = {
    # UI和显示相关
    'UI': 'UI',
    'HUD': 'HUD',
    'VR': 'VR',
    
    # 动作相关
    'ATTACK': '攻击',
    'WALK': '行走',
    'RUN': '奔跑',
    'IDLE': '待机',
    'MOVE': '移动',
    'JUMP': '跳跃',
    'LAND': '着陆',
    'FALL': '坠落',
    'SLIDE': '滑行',
    'SWIM': '游泳',
    'FLY': '飞行',
    'CROUCH': '蹲下',
    'PRONE': '卧倒',
    'STAND': '站立',
    'SIT': '坐下',
    'TURN': '转身',
    'SPIN': '旋转',
    'ROLL': '翻滚',
    'DODGE': '闪避',
    'CLIMB': '攀爬',
    'HANG': '悬挂',
    
    # 武器和战斗
    'FIRE': '开火',
    'SHOOT': '射击',
    'RELOAD': '装填',
    'AIM': '瞄准',
    'SCOPE': '瞄准镜',
    'DRAW': '拔出',
    'HOLSTER': '收起',
    'THROW': '投掷',
    'MELEE': '近战',
    'PUNCH': '拳击',
    'KICK': '踢击',
    'SLASH': '斩击',
    'STAB': '刺击',
    'BLOCK': '格挡',
    'PARRY': '招架',
    'GRENADE': '手雷',
    'BOMB': '炸弹',
    'MINE': '地雷',
    'KNIFE': '刀',
    'SWORD': '剑',
    'AXE': '斧',
    'HAMMER': '锤',
    'SHIELD': '盾牌',
    'GUN': '枪',
    'PISTOL': '手枪',
    'RIFLE': '步枪',
    'SHOTGUN': '霰弹枪',
    'SMG': '冲锋枪',
    'SNIPER': '狙击',
    'RPG': '火箭筒',
    'LAUNCHER': '发射器',
    'TURRET': '炮塔',
    
    # 状态
    'RELAX': '放松',
    'ALERT': '警觉',
    'COMBAT': '战斗',
    'STEALTH': '潜行',
    'ANGRY': '愤怒',
    'HAPPY': '开心',
    'SAD': '悲伤',
    'SCARED': '害怕',
    'HURT': '受伤',
    'DEAD': '死亡',
    'DYING': '濒死',
    'STUNNED': '眩晕',
    'DAZED': '眩晕',
    
    # 方向
    'LEFT': '左',
    'RIGHT': '右',
    'UP': '上',
    'DOWN': '下',
    'FORWARD': '前',
    'BACK': '后',
    'NORTH': '北',
    'SOUTH': '南',
    'EAST': '东',
    'WEST': '西',
    
    # 游戏相关
    'PDA': 'PDA',
    'CSGO': 'CSGO',
    'CS': 'CS',
    'HL': 'HL',
    'TF': 'TF',
    'DOTA': 'DOTA',
    'PORTAL': '传送门',
    
    # 杂项
    'COOLDOWN': '冷却',
    'MANACOST': '法力消耗',
    'DAMAGE': '伤害',
    'HEAL': '治疗',
    'BUFF': '增益',
    'DEBUFF': '减益',
    'CRIT': '暴击',
    'MISS': '未命中',
    'HIT': '命中',
    'DODGE': '闪避',
    'BLOCK': '格挡',
    'RESIST': '抗性',
    'IMMUNITY': '免疫',
    'STUN': '眩晕',
    'SLOW': '减速',
    'ROOT': '缠绕',
    'SILENCE': '沉默',
    'DISARM': '缴械',
    'FEAR': '恐惧',
    'TAUNT': '嘲讽',
    'CHARM': '魅惑',
    'SLEEP': '睡眠',
    'KNOCKBACK': '击退',
    'KNOCKUP': '击飞',
    'PULL': '拉拽',
    'PUSH': '推开',
    
    # 数值相关
    'MAX': '最大',
    'MIN': '最小',
    'TOTAL': '总计',
    'BASE': '基础',
    'BONUS': '加成',
    'FLAT': '固定',
    'PERCENT': '百分比',
    'RATE': '速率',
    'SPEED': '速度',
    'RANGE': '范围',
    'RADIUS': '半径',
    'DURATION': '持续时间',
    'COOLDOWN': '冷却',
    'COST': '消耗',
    'TIER': '层级',
    'LEVEL': '等级',
    'STACK': '层数',
    'LIMIT': '限制',
    'CAP': '上限',
    
    # 其他常见词
    'ENOUGH': '足够',
    'TAKE': '获取',
    'GIVE': '给予',
    'SELL': '出售',
    'BUY': '购买',
    'PICK': '选择',
    'DROP': '丢弃',
    'USE': '使用',
    'OPEN': '打开',
    'CLOSE': '关闭',
    'START': '开始',
    'END': '结束',
    'STOP': '停止',
    'PAUSE': '暂停',
    'RESUME': '继续',
    'RESET': '重置',
    'CLEAR': '清除',
    'SAVE': '保存',
    'LOAD': '加载',
    'CREATE': '创建',
    'DESTROY': '销毁',
    'SPAWN': '生成',
    'REMOVE': '移除',
    'ADD': '添加',
    'DELETE': '删除',
    'UPDATE': '更新',
    'REFRESH': '刷新',
    'SHOW': '显示',
    'HIDE': '隐藏',
    'ENABLE': '启用',
    'DISABLE': '禁用',
    'LOCK': '锁定',
    'UNLOCK': '解锁',
    'SELECT': '选择',
    'DESELECT': '取消选择',
    'CONFIRM': '确认',
    'CANCEL': '取消',
    'ACCEPT': '接受',
    'REJECT': '拒绝',
    'APPROVE': '批准',
    'DENY': '拒绝',
    'ALLOW': '允许',
    'FORBID': '禁止',
    'REQUIRE': '需要',
    'OPTIONAL': '可选',
    'DEFAULT': '默认',
    'CUSTOM': '自定义',
    'AUTO': '自动',
    'MANUAL': '手动',
    'RANDOM': '随机',
    'FIXED': '固定',
    'DYNAMIC': '动态',
    'STATIC': '静态',
    'GLOBAL': '全局',
    'LOCAL': '本地',
    'PUBLIC': '公开',
    'PRIVATE': '私有',
    'SHARED': '共享',
    'UNIQUE': '唯一',
    'COMMON': '普通',
    'RARE': '稀有',
    'EPIC': '史诗',
    'LEGENDARY': '传奇',
    'MYTHICAL': '神话',
    'IMMORTAL': '不朽',
    'ARCANA': '至宝',
    
    # Source引擎动画相关
    'VM': '视图模型',
    'ACT': '动作',
    'SEQ': '序列',
    'ANIM': '动画',
    'POSE': '姿势',
    'BLEND': '混合',
    'LAYER': '层',
    'LOOP': '循环',
    'ONCE': '单次',
    'HOLD': '保持',
    'SNAP': '快速',
    'SMOOTH': '平滑',
    'EASE': '缓动',
    'LINEAR': '线性',
    'CUBIC': '立方',
    'QUAD': '二次',
    
    # 手势和表情
    'GESTURE': '手势',
    'EMOTE': '表情',
    'WAVE': '挥手',
    'NOD': '点头',
    'SHAKE': '摇头',
    'SHRUG': '耸肩',
    'CLAP': '鼓掌',
    'CHEER': '欢呼',
    'BOW': '鞠躬',
    'SALUTE': '敬礼',
    'POINT': '指向',
    'THUMB': '拇指',
    'FIST': '拳头',
    'PALM': '手掌',
    'FINGER': '手指',
    'HAND': '手',
    'ARM': '手臂',
    'LEG': '腿',
    'FOOT': '脚',
    'HEAD': '头',
    'BODY': '身体',
    'CHEST': '胸部',
    'BACK': '背部',
    'SHOULDER': '肩部',
    'NECK': '颈部',
    'FACE': '脸',
    'EYE': '眼睛',
    'MOUTH': '嘴',
    'NOSE': '鼻子',
    'EAR': '耳朵',
    
    # 其他缩写和专有名词
    'NPC': 'NPC',
    'AI': 'AI',
    'BOT': '机器人',
    'CPU': 'CPU',
    'GPU': 'GPU',
    'FPS': 'FPS',
    'FOV': '视野',
    'LOD': '细节层次',
    'LOF': '视线',
    'LOS': '视线',
    'AOE': '范围效果',
    'DOT': '持续伤害',
    'HOT': '持续治疗',
    'DPS': '每秒伤害',
    'HPS': '每秒治疗',
    'CD': '冷却',
    'GCD': '公共冷却',
    'HP': '生命值',
    'MP': '法力值',
    'XP': '经验',
    'EXP': '经验',
    'LVL': '等级',
    'STR': '力量',
    'AGI': '敏捷',
    'INT': '智力',
    'ATK': '攻击',
    'DEF': '防御',
    'SPD': '速度',
    'ACC': '命中',
    'EVA': '闪避',
    'CRT': '暴击',
    'PEN': '穿透',
    'RES': '抗性',
    'REG': '恢复',
    'VAL': '值',
    'PCT': '百分比',
    'NUM': '数量',
    'CNT': '计数',
    'IDX': '索引',
    'POS': '位置',
    'ROT': '旋转',
    'SCL': '缩放',
    'VEC': '向量',
    'MAT': '矩阵',
    'QUA': '四元数',
    'RGB': 'RGB',
    'HSV': 'HSV',
    'HSL': 'HSL',
    'RGBA': 'RGBA',
    'ARGB': 'ARGB',
}

# 特殊模式替换
PATTERNS = [
    (r'STIMULAT\w*', '刺激'),
    (r'AGITAT\w*', '激动'),
    (r'STICKWALL\w*', '贴墙'),
    (r'AUGUN\w*', '自动枪'),
    (r'HAMOUTH', '手嘴'),
    (r'FGERPOT', '手指指向'),
    (r'FTPUMP', '拳头泵'),
    (r'THUMBSUP', '竖拇指'),
    (r'NODYES', '点头是'),
    (r'NODNO', '摇头否'),
    (r'RESTANCE', '抗性'),
    (r'YFIRE', '空射'),
    (r'ATTACKSPE\w*', '攻击速度'),
    (r'PROCATTACK', '触发攻击'),
    (r'DAMAGEOUTGO\w*', '伤害输出'),
    (r'TRIPME\w*', '地雷'),
    (r'READESS', '准备'),
    (r'SHIELDUP', '举盾'),
    (r'RAGDOLLRE\w*', '布娃娃'),
    (r'ANTLCUTTLE', '蚁狮'),
    (r'NIANP\w*', '年兽'),
    (r'POSITI\w*', '位置'),
    (r'TRANSITI\w*', '过渡'),
    (r'EABLE', '可用'),
    (r'REQUIR\w*', '需要'),
    (r'SMACH\w*', '击碎'),
    (r'FLICK', '快速'),
    (r'PRIM\w*', '主要'),
    (r'DET\w*', '爆炸'),
    (r'TRO\w*', ''),
    (r'TAL\w*', '总'),
    (r'SPE\w*', '速度'),
    (r'OPT\w*', '选项'),
    (r'CAG\w*', '笼子'),
    (r'AVOID', '避免'),
    (r'ALT', '替代'),
    (r'GROUP', '组'),
    (r'RAD\w*', '天辉'),
    (r'STASH', '储藏'),
    (r'CL\w{1,2}$', ''),
    (r'^ER$', ''),
    (r'^MS$', '毫秒'),
    (r'^FH$', ''),
    (r'^CT$', ''),
    (r'^OF$', ''),
    (r'^SH$', ''),
    (r'^BE$', ''),
    (r'^RE$', ''),
    (r'^SWG$', ''),
    (r'^ND$', ''),
]

def translate_description(desc):
    """翻译描述文本"""
    result = desc
    
    # 先应用模式替换
    for pattern, replacement in PATTERNS:
        result = re.sub(pattern, replacement, result)
    
    # 再应用词典替换
    for eng, chn in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        result = result.replace(eng, chn)
    
    # 清理多余空格
    result = ' '.join(result.split())
    
    return result

def main():
    with open('data/luaapi/enums_cn.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed = 0
    for item in data['items']:
        for m in item.get('members', []):
            desc = m.get('description_cn', '')
            if re.search(r'[A-Z]{2,}', desc):
                new_desc = translate_description(desc)
                if new_desc != desc:
                    m['description_cn'] = new_desc
                    fixed += 1
    
    with open('data/luaapi/enums_cn.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'修复了 {fixed} 个翻译')
    
    # 统计剩余
    remaining = 0
    for item in data['items']:
        for m in item.get('members', []):
            desc = m.get('description_cn', '')
            if re.search(r'[A-Z]{3,}', desc):
                remaining += 1
    
    print(f'剩余包含英文: {remaining}')

if __name__ == '__main__':
    main()
