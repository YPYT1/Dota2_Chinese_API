"""
Dota2 Game Events 爬虫
从 https://moddota.com/api/#!/events 爬取所有游戏事件
输出到 data/gameevents/events.json
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# 配置
ROOT_URL = "https://moddota.com/api/#!/events"
BASE_URL = "https://moddota.com/api/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gameevents")


# ==================== 步骤一：获取所有事件地址和推荐标记 ====================

async def get_all_event_urls(page):
    """获取所有事件页面地址及推荐标记"""
    print(f"正在访问: {ROOT_URL}")
    await page.goto(ROOT_URL, wait_until='networkidle')
    await asyncio.sleep(1)
    
    # 提取所有链接和推荐状态
    events_info = await page.evaluate('''() => {
        const results = [];
        document.querySelectorAll('a.Sidebar__SidebarLink-kKnkkd').forEach(a => {
            const href = a.getAttribute('href');
            if (href && href.startsWith('#!/events/')) {
                const isRecommended = !!a.querySelector('span[title="This event is useful for custom games"]');
                results.push({
                    url: 'https://moddota.com/api/' + href,
                    href: href,
                    isRecommended: isRecommended
                });
            }
        });
        return results;
    }''')
    
    return events_info


# ==================== 步骤二：提取事件数据 ====================

async def extract_event_data(page, event_info):
    """提取单个事件页面数据"""
    return await page.evaluate('''(eventInfo) => {
        const wrapper = document.querySelector('div[class*="FunctionDeclaration__FunctionWrapper"]');
        if (!wrapper) return null;
        
        // 事件名（从 id 获取）
        const name = wrapper.getAttribute('id') || '';
        
        // 签名
        const sigEl = wrapper.querySelector('div[class*="FunctionDeclaration__FunctionSignature"]');
        const signature = sigEl ? sigEl.textContent.trim() : '';
        
        // 参数
        const parameters = [];
        if (sigEl) {
            sigEl.querySelectorAll('span[class*="types__FunctionParameterWrapper"]').forEach(paramEl => {
                const spans = paramEl.querySelectorAll(':scope > span');
                let paramName = '';
                let paramType = '';
                
                if (spans.length > 0) {
                    paramName = spans[0].textContent.replace(':', '').trim();
                }
                
                // 获取类型
                const typeSpan = paramEl.querySelector('span[class*="types__TypeSpan"]');
                if (typeSpan) {
                    paramType = typeSpan.textContent.trim();
                }
                
                parameters.push({
                    name: paramName,
                    type: paramType,
                    description: null,
                    description_cn: '',
                    type_description_cn: ''
                });
            });
        }
        
        // 参数描述
        wrapper.querySelectorAll('li[class*="FunctionDeclaration__ParameterDescription"]').forEach(li => {
            const nameEl = li.querySelector('span[class*="FunctionDeclaration__ParameterDescriptionName"]');
            if (nameEl) {
                const pName = nameEl.textContent.trim();
                const fullText = li.textContent.trim();
                const colonIdx = fullText.indexOf(':');
                const desc = colonIdx !== -1 ? fullText.slice(colonIdx + 1).trim() : null;
                
                const param = parameters.find(p => p.name === pName);
                if (param) {
                    param.description = desc;
                }
            }
        });
        
        // 事件描述（排除参数描述列表）
        let description = null;
        const descEl = wrapper.querySelector('div[class*="styles__Description"]');
        if (descEl) {
            const clone = descEl.cloneNode(true);
            clone.querySelectorAll('li').forEach(el => el.remove());
            const text = clone.textContent.trim();
            if (text) description = text;
        }
        
        // 返回值
        let returnType = 'void';
        if (sigEl) {
            const sigText = sigEl.textContent;
            const colonIdx = sigText.lastIndexOf('):');
            if (colonIdx !== -1) {
                returnType = sigText.slice(colonIdx + 2).trim();
            }
        }
        
        // 链接
        const githubEl = wrapper.querySelector('a[title="Search on GitHub"]');
        const googleEl = wrapper.querySelector('a[title="Search on Google"]');
        const linkEl = wrapper.querySelector('a[class*="ElementLink__StyledElementLink"]');
        
        return {
            name,
            signature,
            description,
            parameters,
            returnType,
            isRecommended: eventInfo.isRecommended,
            githubLink: githubEl ? githubEl.getAttribute('href') : null,
            googleLink: googleEl ? googleEl.getAttribute('href') : null,
            link: eventInfo.href,
            
            // 中文化预留字段
            name_cn: '',
            description_cn: '',
            example_ts: '',
            notes_cn: '',
            common_usage_cn: '',
            related: [],
            see_also: [],
            tags: []
        };
    }''', event_info)


async def crawl_event(page, event_info):
    """爬取单个事件页面"""
    try:
        await page.goto(event_info['url'], wait_until='networkidle', timeout=30000)
        await asyncio.sleep(0.3)
        
        data = await extract_event_data(page, event_info)
        return data
    except Exception as e:
        print(f"  爬取失败 {event_info['url']}: {e}")
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
    events = []
    recommended_count = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 步骤一：获取所有事件地址
        print("=" * 60)
        print("步骤一：获取所有事件地址")
        print("=" * 60)
        events_info = await get_all_event_urls(page)
        print(f"共找到 {len(events_info)} 个事件")
        recommended_count = sum(1 for e in events_info if e['isRecommended'])
        print(f"其中推荐事件: {recommended_count} 个")
        
        # 步骤二：遍历每个事件提取数据
        print("\n" + "=" * 60)
        print("步骤二：提取事件数据")
        print("=" * 60)
        
        for i, event_info in enumerate(events_info):
            print(f"[{i+1}/{len(events_info)}] {event_info['url'].split('/')[-1]}", end='')
            
            data = await crawl_event(page, event_info)
            if data:
                events.append(data)
                star = ' ⭐' if data['isRecommended'] else ''
                params = len(data['parameters'])
                print(f" → {params} 参数{star}")
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
            "type": "gameevents",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(events),
            "recommendedCount": recommended_count
        },
        "items": events
    }, "events.json")
    
    # 统计
    print("\n" + "=" * 60)
    print("爬取完成！统计:")
    print("=" * 60)
    print(f"  事件总数: {len(events)} 个")
    print(f"  推荐事件: {recommended_count} 个")
    
    total_params = sum(len(e['parameters']) for e in events)
    with_desc = sum(1 for e in events if e['description'])
    params_with_desc = sum(
        sum(1 for p in e['parameters'] if p['description']) 
        for e in events
    )
    
    print(f"  参数总数: {total_params} 个")
    print(f"  带描述的事件: {with_desc} 个")
    print(f"  带描述的参数: {params_with_desc} 个")


if __name__ == "__main__":
    asyncio.run(main())
