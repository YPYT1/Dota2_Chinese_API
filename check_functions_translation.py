#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 functions.json 和 functions_cn.json 的翻译完整性"""

import json

def check_translation():
    # 读取两个文件
    with open('data/luaapi/functions.json', 'r', encoding='utf-8') as f:
        original = json.load(f)

    with open('data/luaapi/functions_cn.json', 'r', encoding='utf-8') as f:
        translated = json.load(f)

    print('=' * 60)
    print('Functions.json 翻译完整性检查报告')
    print('=' * 60)

    # 基本信息
    orig_count = original['metadata']['count']
    trans_count = len(translated['items'])
    print(f'\n📊 基本统计:')
    print(f'   原文函数数量: {orig_count}')
    print(f'   翻译函数数量: {trans_count}')

    # 检查每个函数
    missing_func = []
    missing_params = []
    total_funcs = len(original['items'])
    total_params = 0
    translated_funcs = 0
    translated_params = 0

    for i, orig_func in enumerate(original['items']):
        trans_func = translated['items'][i] if i < len(translated['items']) else None
        
        if not trans_func:
            missing_func.append(f'{orig_func["name"]}: 整个函数缺失')
            continue
        
        # 检查函数翻译
        func_translated = True
        if not trans_func.get('name_cn') or trans_func['name_cn'].strip() == '':
            missing_func.append(f'{orig_func["name"]}: name_cn为空')
            func_translated = False
        
        if not trans_func.get('description_cn') or trans_func['description_cn'].strip() == '':
            if orig_func.get('description'):
                missing_func.append(f'{orig_func["name"]}: description_cn为空')
                func_translated = False
        
        if func_translated:
            translated_funcs += 1
        
        # 检查参数
        orig_params = orig_func.get('parameters', [])
        trans_params = trans_func.get('parameters', [])
        
        for j, orig_param in enumerate(orig_params):
            total_params += 1
            trans_param = trans_params[j] if j < len(trans_params) else None
            
            if not trans_param:
                missing_params.append(f'{orig_func["name"]}({orig_param["name"]}): 参数缺失')
                continue
            
            if not trans_param.get('description_cn') or trans_param['description_cn'].strip() == '':
                missing_params.append(f'{orig_func["name"]}({orig_param["name"]}): description_cn为空')
            else:
                translated_params += 1

    func_pct = translated_funcs * 100 // total_funcs if total_funcs else 0
    param_pct = translated_params * 100 // total_params if total_params else 0

    print(f'\n📈 翻译统计:')
    print(f'   函数: {translated_funcs}/{total_funcs} ({func_pct}%)')
    print(f'   参数: {translated_params}/{total_params} ({param_pct}%)')

    print(f'\n❌ 未翻译的函数 ({len(missing_func)}):')
    for item in missing_func[:20]:
        print(f'   - {item}')
    if len(missing_func) > 20:
        print(f'   ... 还有 {len(missing_func)-20} 项')

    print(f'\n❌ 未翻译的参数 ({len(missing_params)}):')
    for item in missing_params[:20]:
        print(f'   - {item}')
    if len(missing_params) > 20:
        print(f'   ... 还有 {len(missing_params)-20} 项')

    print('\n' + '=' * 60)
    if not missing_func and not missing_params:
        print('✅ 翻译完整，没有遗漏！')
    else:
        total_missing = len(missing_func) + len(missing_params)
        print(f'⚠️ 共有 {total_missing} 处需要翻译')
    
    return {
        'missing_funcs': missing_func,
        'missing_params': missing_params
    }

if __name__ == '__main__':
    check_translation()
