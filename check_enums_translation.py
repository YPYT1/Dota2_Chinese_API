#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 enums.json 和 enums_cn.json 的翻译完整性"""

import json

def check_translation():
    with open('data/luaapi/enums.json', 'r', encoding='utf-8') as f:
        original = json.load(f)

    with open('data/luaapi/enums_cn.json', 'r', encoding='utf-8') as f:
        translated = json.load(f)

    print('=' * 60)
    print('Enums.json 翻译完整性检查报告')
    print('=' * 60)

    orig_count = original['metadata']['count']
    trans_count = len(translated['items'])
    print(f'\n📊 基本统计:')
    print(f'   原文枚举数量: {orig_count}')
    print(f'   翻译枚举数量: {trans_count}')

    missing_enums = []
    missing_values = []
    total_enums = len(original['items'])
    total_values = 0
    translated_enums = 0
    translated_values = 0

    for i, orig_enum in enumerate(original['items']):
        trans_enum = translated['items'][i] if i < len(translated['items']) else None
        
        if not trans_enum:
            missing_enums.append(f'{orig_enum["name"]}: 整个枚举缺失')
            continue
        
        # 检查枚举翻译
        enum_translated = True
        if not trans_enum.get('name_cn') or trans_enum['name_cn'].strip() == '':
            missing_enums.append(f'{orig_enum["name"]}: name_cn为空')
            enum_translated = False
        
        if enum_translated:
            translated_enums += 1
        
        # 检查枚举值
        orig_values = orig_enum.get('values', [])
        trans_values = trans_enum.get('values', [])
        
        for j, orig_val in enumerate(orig_values):
            total_values += 1
            trans_val = trans_values[j] if j < len(trans_values) else None
            
            if not trans_val:
                missing_values.append(f'{orig_enum["name"]}.{orig_val["name"]}: 值缺失')
                continue
            
            if not trans_val.get('description_cn') or trans_val['description_cn'].strip() == '':
                missing_values.append(f'{orig_enum["name"]}.{orig_val["name"]}')
            else:
                translated_values += 1

    enum_pct = translated_enums * 100 // total_enums if total_enums else 0
    value_pct = translated_values * 100 // total_values if total_values else 0

    print(f'\n📈 翻译统计:')
    print(f'   枚举: {translated_enums}/{total_enums} ({enum_pct}%)')
    print(f'   枚举值: {translated_values}/{total_values} ({value_pct}%)')

    print(f'\n❌ 未翻译的枚举 ({len(missing_enums)}):')
    for item in missing_enums[:20]:
        print(f'   - {item}')
    if len(missing_enums) > 20:
        print(f'   ... 还有 {len(missing_enums)-20} 项')

    print(f'\n❌ 未翻译的枚举值 ({len(missing_values)}):')
    for item in missing_values[:30]:
        print(f'   - {item}')
    if len(missing_values) > 30:
        print(f'   ... 还有 {len(missing_values)-30} 项')

    print('\n' + '=' * 60)
    if not missing_enums and not missing_values:
        print('✅ 翻译完整，没有遗漏！')
    else:
        total_missing = len(missing_enums) + len(missing_values)
        print(f'⚠️ 共有 {total_missing} 处需要翻译')
    
    return missing_values

if __name__ == '__main__':
    check_translation()
