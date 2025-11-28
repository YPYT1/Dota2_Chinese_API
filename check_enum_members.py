import json

with open('data/luaapi/enums_cn.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

empty = 0
total = 0
for item in data['items']:
    for m in item.get('members', []):
        total += 1
        if not m.get('description_cn') or m['description_cn'].strip() == '':
            empty += 1

print(f'总枚举成员: {total}')
print(f'未翻译: {empty}')
print(f'已翻译: {total - empty}')
print(f'完成率: {(total-empty)*100//total if total else 0}%')
