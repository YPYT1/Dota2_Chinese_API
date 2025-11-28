#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比 classes.json 和 classes_cn.json 的翻译完整性"""

import json

def check_translation():
    # 读取两个文件
    with open('data/luaapi/classes.json', 'r', encoding='utf-8') as f:
        original = json.load(f)

    with open('data/luaapi/classes_cn.json', 'r', encoding='utf-8') as f:
        translated = json.load(f)

    print('=' * 60)
    print('Classes.json 翻译完整性检查报告')
    print('=' * 60)

    # 基本信息
    print(f'\n📊 基本统计:')
    print(f'   原文类数量: {original["metadata"]["count"]}')
    print(f'   翻译类数量: {len(translated["items"])}')

    # 检查每个类
    missing_class_translations = []
    missing_method_translations = []
    missing_param_translations = []
    total_methods = 0
    total_params = 0
    translated_classes = 0
    translated_methods = 0
    translated_params = 0

    for i, orig_class in enumerate(original['items']):
        trans_class = translated['items'][i] if i < len(translated['items']) else None
        
        if not trans_class:
            missing_class_translations.append(f'{orig_class["name"]}: 整个类缺失')
            continue
        
        # 检查类翻译
        if not trans_class.get('name_cn') or trans_class['name_cn'].strip() == '':
            missing_class_translations.append(f'{orig_class["name"]}: name_cn为空')
        else:
            translated_classes += 1
        
        if not trans_class.get('description_cn') or trans_class['description_cn'].strip() == '':
            if orig_class.get('description'):  # 只有原文有描述时才报告
                missing_class_translations.append(f'{orig_class["name"]}: description_cn为空(原文有描述)')
        
        # 检查方法
        orig_methods = orig_class.get('methods', [])
        trans_methods = trans_class.get('methods', [])
        
        for j, orig_method in enumerate(orig_methods):
            total_methods += 1
            trans_method = trans_methods[j] if j < len(trans_methods) else None
            
            if not trans_method:
                missing_method_translations.append(f'{orig_class["name"]}.{orig_method["name"]}: 方法缺失')
                continue
            
            # 检查方法翻译
            method_translated = True
            if not trans_method.get('name_cn') or trans_method['name_cn'].strip() == '':
                missing_method_translations.append(f'{orig_class["name"]}.{orig_method["name"]}: name_cn为空')
                method_translated = False
            
            if not trans_method.get('description_cn') or trans_method['description_cn'].strip() == '':
                if orig_method.get('description'):
                    missing_method_translations.append(f'{orig_class["name"]}.{orig_method["name"]}: description_cn为空')
                    method_translated = False
            
            if method_translated:
                translated_methods += 1
            
            # 检查参数
            orig_params = orig_method.get('parameters', [])
            trans_params = trans_method.get('parameters', [])
            
            for k, orig_param in enumerate(orig_params):
                total_params += 1
                trans_param = trans_params[k] if k < len(trans_params) else None
                
                if not trans_param:
                    missing_param_translations.append(f'{orig_class["name"]}.{orig_method["name"]}({orig_param["name"]}): 参数缺失')
                    continue
                
                param_translated = True
                if not trans_param.get('description_cn') or trans_param['description_cn'].strip() == '':
                    missing_param_translations.append(f'{orig_class["name"]}.{orig_method["name"]}({orig_param["name"]}): description_cn为空')
                    param_translated = False
                
                if param_translated:
                    translated_params += 1

    print(f'\n📈 翻译统计:')
    class_pct = translated_classes * 100 // len(original["items"]) if original["items"] else 0
    method_pct = translated_methods * 100 // total_methods if total_methods else 0
    param_pct = translated_params * 100 // total_params if total_params else 0
    
    print(f'   类: {translated_classes}/{len(original["items"])} ({class_pct}%)')
    print(f'   方法: {translated_methods}/{total_methods} ({method_pct}%)')
    print(f'   参数: {translated_params}/{total_params} ({param_pct}%)')

    print(f'\n❌ 未翻译的类 ({len(missing_class_translations)}):')
    for item in missing_class_translations[:20]:
        print(f'   - {item}')
    if len(missing_class_translations) > 20:
        print(f'   ... 还有 {len(missing_class_translations)-20} 项')

    print(f'\n❌ 未翻译的方法 ({len(missing_method_translations)}):')
    for item in missing_method_translations[:20]:
        print(f'   - {item}')
    if len(missing_method_translations) > 20:
        print(f'   ... 还有 {len(missing_method_translations)-20} 项')

    print(f'\n❌ 未翻译的参数 ({len(missing_param_translations)}):')
    for item in missing_param_translations[:30]:
        print(f'   - {item}')
    if len(missing_param_translations) > 30:
        print(f'   ... 还有 {len(missing_param_translations)-30} 项')

    print('\n' + '=' * 60)
    
    # 总结
    if not missing_class_translations and not missing_method_translations and not missing_param_translations:
        print('✅ 翻译完整，没有遗漏！')
    else:
        total_missing = len(missing_class_translations) + len(missing_method_translations) + len(missing_param_translations)
        print(f'⚠️ 共有 {total_missing} 处需要翻译')
    
    return {
        'missing_classes': missing_class_translations,
        'missing_methods': missing_method_translations,
        'missing_params': missing_param_translations
    }

if __name__ == '__main__':
    check_translation()
