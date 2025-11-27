"""
Dota2 Panorama API 爬虫
从 https://moddota.com/api/#!/panorama/api 爬取所有枚举/常量
输出到 data/panoramaapi/enums.json
"""
import asyncio
import json
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright

# 配置
ROOT_URL = "https://moddota.com/api/#!/panorama/api"
BASE_URL = "https://moddota.com/api/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "panoramaapi")


# ==================== 步骤一：获取所有枚举地址 ====================

async def get_all_enum_urls(page):
    """获取所有枚举页面地址"""
    print(f"正在访问: {ROOT_URL}")
    await page.goto(ROOT_URL, wait_until='networkidle')
    await asyncio.sleep(1)
    
    # 提取所有链接
    enums_info = await page.evaluate('''() => {
        const results = [];
        document.querySelectorAll('a.Sidebar__SidebarLink-kKnkkd').forEach(a => {
            const href = a.getAttribute('href');
            if (href && href.startsWith('#!/panorama/api/')) {
                results.push({
                    url: 'https://moddota.com/api/' + href,
                    href: href,
                    name: a.textContent.trim()
                });
            }
        });
        return results;
    }''')
    
    return enums_info


# ==================== 步骤二：提取枚举数据 ====================

async def extract_enum_data(page, enum_info):
    """提取单个枚举页面数据"""
    return await page.evaluate('''(enumInfo) => {
        // 使用类名选择器找到包装器
        const wrapper = document.querySelector('div[class*="styles__CommonGroupWrapper"]');
        if (!wrapper) return null;
        
        // 获取枚举名称
        const nameEl = wrapper.querySelector('div[class*="CommonGroupSignature"]');
        const enumName = nameEl ? nameEl.textContent.trim() : enumInfo.name;
        
        // 获取 references 链接
        let referencesLink = null;
        const refLink = wrapper.querySelector('a[href*="search=type"]');
        if (refLink) {
            referencesLink = refLink.getAttribute('href');
        }
        
        // 获取成员列表
        const members = [];
        const membersContainer = wrapper.querySelector('div[class*="Enum__EnumMembers"]');
        
        if (membersContainer) {
            // 遍历所有成员 div
            membersContainer.querySelectorAll(':scope > div').forEach(memberDiv => {
                const childDivs = memberDiv.querySelectorAll(':scope > div');
                
                if (childDivs.length >= 1) {
                    // 有子 div 的情况（带描述或方法名）
                    const nameValueText = childDivs[0].textContent.trim();
                    
                    // 解析 NAME = value
                    const eqIdx = nameValueText.indexOf('=');
                    if (eqIdx !== -1) {
                        const name = nameValueText.slice(0, eqIdx).trim();
                        let value = nameValueText.slice(eqIdx + 1).trim();
                        
                        // 尝试转换为数字
                        const numValue = parseInt(value, 10);
                        if (!isNaN(numValue)) {
                            value = numValue;
                        }
                        
                        let description = null;
                        let methodName = null;
                        
                        // 检查是否有描述或方法名
                        if (childDivs.length >= 2) {
                            const descText = childDivs[1].textContent.trim();
                            
                            // 检查是否是 Method Name 格式
                            if (descText.includes('Method Name:')) {
                                const match = descText.match(/Method Name:\\s*`([^`]+)`/);
                                if (match) {
                                    methodName = match[1];
                                }
                            } else if (descText) {
                                description = descText;
                            }
                        }
                        
                        members.push({
                            name,
                            value,
                            description,
                            methodName,
                            description_cn: '',
                            methodName_cn: ''
                        });
                    }
                } else {
                    // 没有子 div，直接解析文本
                    const text = memberDiv.textContent.trim();
                    const eqIdx = text.indexOf('=');
                    if (eqIdx !== -1) {
                        const name = text.slice(0, eqIdx).trim();
                        let value = text.slice(eqIdx + 1).trim();
                        
                        const numValue = parseInt(value, 10);
                        if (!isNaN(numValue)) {
                            value = numValue;
                        }
                        
                        members.push({
                            name,
                            value,
                            description: null,
                            methodName: null,
                            description_cn: '',
                            methodName_cn: ''
                        });
                    }
                }
            });
        }
        
        return {
            name: enumName || enumInfo.name,
            referencesLink,
            link: enumInfo.href,
            members,
            
            // 中文化预留字段
            name_cn: '',
            description_cn: '',
            usage_cn: '',
            example_ts: '',
            notes_cn: '',
            related: [],
            see_also: [],
            tags: []
        };
    }''', enum_info)


async def crawl_enum(page, enum_info):
    """爬取单个枚举页面"""
    try:
        await page.goto(enum_info['url'], wait_until='networkidle', timeout=30000)
        await asyncio.sleep(0.3)
        
        data = await extract_enum_data(page, enum_info)
        return data
    except Exception as e:
        print(f"  爬取失败 {enum_info['url']}: {e}")
        return None


def save_json(data, filename):
    """保存 JSON 文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存: {filepath}")


# ==================== 主流程 ====================

async def main():
    """主函数"""
    enums = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 步骤一：获取所有枚举地址
        print("=" * 60)
        print("步骤一：获取所有枚举地址")
        print("=" * 60)
        enums_info = await get_all_enum_urls(page)
        print(f"共找到 {len(enums_info)} 个枚举/常量")
        
        # 步骤二：遍历每个枚举提取数据
        print("\n" + "=" * 60)
        print("步骤二：提取枚举数据")
        print("=" * 60)
        
        for i, enum_info in enumerate(enums_info):
            print(f"[{i+1}/{len(enums_info)}] {enum_info['name']}", end='')
            
            data = await crawl_enum(page, enum_info)
            if data:
                enums.append(data)
                member_count = len(data['members'])
                has_desc = sum(1 for m in data['members'] if m['description'])
                has_method = sum(1 for m in data['members'] if m['methodName'])
                
                info = f" → {member_count} 成员"
                if has_desc > 0:
                    info += f" ({has_desc} 带描述)"
                if has_method > 0:
                    info += f" ({has_method} 带方法名)"
                print(info)
            else:
                print(" → 失败")
        
        await browser.close()
    
    # 步骤三：保存 JSON 文件
    print("\n" + "=" * 60)
    print("步骤三：保存 JSON 文件")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    
    save_json({
        "metadata": {
            "type": "panorama_api",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(enums)
        },
        "items": enums
    }, "enums.json")
    
    # 统计
    print("\n" + "=" * 60)
    print("爬取完成！统计:")
    print("=" * 60)
    print(f"  枚举/常量总数: {len(enums)} 个")
    
    total_members = sum(len(e['members']) for e in enums)
    with_desc = sum(
        sum(1 for m in e['members'] if m['description'])
        for e in enums
    )
    with_method = sum(
        sum(1 for m in e['members'] if m['methodName'])
        for e in enums
    )
    
    print(f"  成员总数: {total_members} 个")
    print(f"  带描述的成员: {with_desc} 个")
    print(f"  带方法名的成员: {with_method} 个")
    
    # 按成员数量排序显示前 5 个
    print("\n  成员数量前5:")
    sorted_enums = sorted(enums, key=lambda x: len(x['members']), reverse=True)
    for i, e in enumerate(sorted_enums[:5]):
        print(f"    {i+1}. {e['name']}: {len(e['members'])} 个成员")


if __name__ == "__main__":
    asyncio.run(main())
