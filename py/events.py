"""
Dota2 Panorama Events 爬虫
从 https://moddota.com/api/#!/panorama/events 爬取所有 Panorama 事件
输出到 data/panoramaevents/events.json

特点：只输出有值的字段，无值字段不写入 JSON
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# 配置
ROOT_URL = "https://moddota.com/api/#!/panorama/events"
BASE_URL = "https://moddota.com/api/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "panoramaevents")


# ==================== 步骤一：获取所有事件地址 ====================

async def get_all_event_urls(page):
    """获取所有事件页面地址"""
    print(f"正在访问: {ROOT_URL}")
    await page.goto(ROOT_URL, wait_until='networkidle')
    await asyncio.sleep(1)
    
    # 提取所有链接
    events_info = await page.evaluate('''() => {
        const results = [];
        document.querySelectorAll('a.Sidebar__SidebarLink-kKnkkd').forEach(a => {
            const href = a.getAttribute('href');
            if (href && href.startsWith('#!/panorama/events/')) {
                results.push({
                    url: 'https://moddota.com/api/' + href,
                    href: href,
                    name: a.textContent.trim()
                });
            }
        });
        return results;
    }''')
    
    return events_info


# ==================== 步骤二：提取事件数据 ====================

async def extract_event_data(page, event_info):
    """提取单个事件页面数据，只返回有值的字段"""
    return await page.evaluate('''(eventInfo) => {
        const wrapper = document.querySelector('div[class*="styles__CommonGroupWrapper"]');
        if (!wrapper) return null;
        
        // 基础结果对象
        const result = {};
        
        // 事件名（从签名提取）
        const sigEl = wrapper.querySelector('div[class*="FunctionDeclaration__FunctionSignature"]');
        const sigText = sigEl ? sigEl.textContent.trim() : '';
        
        // 从签名中提取事件名
        const nameMatch = sigText.match(/^([a-zA-Z_][a-zA-Z0-9_]*)/);
        result.name = nameMatch ? nameMatch[1] : eventInfo.name;
        
        // 签名
        result.signature = sigText;
        
        // 描述（可选，只有有值才添加）
        const descEl = wrapper.querySelector('div[class*="styles__Description"]');
        if (descEl) {
            const descText = descEl.textContent.trim();
            if (descText) {
                result.description = descText;
            }
        }
        
        // 参数
        const parameters = [];
        if (sigEl) {
            sigEl.querySelectorAll('span[class*="types__FunctionParameterWrapper"]').forEach(paramEl => {
                const spans = paramEl.querySelectorAll(':scope > span');
                let paramName = '';
                let paramType = '';
                
                if (spans.length > 0) {
                    // 获取参数名（去掉冒号）
                    paramName = spans[0].textContent.replace(':', '').trim();
                }
                
                // 获取类型
                const typeSpan = paramEl.querySelector('span[class*="types__TypeSpan"]');
                if (typeSpan) {
                    paramType = typeSpan.textContent.trim();
                }
                
                // 检查是否有类型链接（引用类型）
                const typeLink = paramEl.querySelector('a[class*="types__TypeReferenceLink"]');
                let typeHref = null;
                if (typeLink) {
                    paramType = typeLink.textContent.trim();
                    typeHref = typeLink.getAttribute('href');
                }
                
                const param = {
                    name: paramName,
                    type: paramType
                };
                
                // 只有有值才添加 typeLink
                if (typeHref) {
                    param.typeLink = typeHref;
                }
                
                // 中文化字段
                param.description_cn = '';
                param.type_description_cn = '';
                
                parameters.push(param);
            });
        }
        result.parameters = parameters;
        
        // 返回值
        let returnType = 'void';
        const colonIdx = sigText.lastIndexOf('):');
        if (colonIdx !== -1) {
            returnType = sigText.slice(colonIdx + 2).trim();
        }
        result.returnType = returnType;
        
        // 参数描述（可选）
        const paramDescs = [];
        wrapper.querySelectorAll('li[class*="FunctionDeclaration__ParameterDescription"]').forEach(li => {
            const nameEl = li.querySelector('span[class*="FunctionDeclaration__ParameterDescriptionName"]');
            if (nameEl) {
                const pName = nameEl.textContent.trim();
                const fullText = li.textContent.trim();
                const idx = fullText.indexOf(':');
                const desc = idx !== -1 ? fullText.slice(idx + 1).trim() : '';
                
                // 更新对应参数的描述
                const param = result.parameters.find(p => p.name === pName);
                if (param && desc) {
                    param.description = desc;
                }
            }
        });
        
        // Options 对象（可选）
        const optionsContainer = wrapper.querySelector('div[class*="FunctionDeclaration__ObjectReferences"]');
        if (optionsContainer) {
            const options = [];
            optionsContainer.querySelectorAll('div[class*="styles__CommonGroupWrapper"]').forEach(optWrapper => {
                const optNameEl = optWrapper.querySelector('span[class*="ObjectType__ObjectName"]');
                if (optNameEl) {
                    const optName = optNameEl.textContent.trim();
                    
                    // 检查是否有 extends
                    const headerText = optWrapper.querySelector('div[class*="CommonGroupSignature"]')?.textContent || '';
                    const extendsMatch = headerText.match(/extends\\s+(\\w+)/);
                    
                    const opt = { name: optName };
                    if (extendsMatch) {
                        opt.extends = extendsMatch[1];
                    }
                    
                    // 字段列表
                    const fields = [];
                    optWrapper.querySelectorAll('div[class*="Field__FieldWrapper"]').forEach(fieldEl => {
                        const fieldName = fieldEl.getAttribute('id') || '';
                        const isOptional = fieldName.endsWith('?');
                        const cleanName = fieldName.replace('?', '');
                        
                        const fieldTypeEl = fieldEl.querySelector('span[class*="types__TypeSpan"]');
                        const fieldType = fieldTypeEl ? fieldTypeEl.textContent.trim() : '';
                        
                        fields.push({
                            name: cleanName,
                            type: fieldType,
                            isOptional: isOptional
                        });
                    });
                    
                    if (fields.length > 0) {
                        opt.fields = fields;
                    }
                    
                    options.push(opt);
                }
            });
            
            if (options.length > 0) {
                result.options = options;
            }
        }
        
        // 可用性（可选）
        const serverAvail = wrapper.querySelector('div[title*="server-side"]');
        const clientAvail = wrapper.querySelector('div[title*="client-side"]');
        
        if (serverAvail) {
            result.serverAvailable = serverAvail.getAttribute('title').includes('Available');
        }
        if (clientAvail) {
            result.clientAvailable = clientAvail.getAttribute('title').includes('Available');
        }
        
        // GitHub 链接
        const githubEl = wrapper.querySelector('a[title="Search on GitHub"]');
        if (githubEl) {
            result.githubLink = githubEl.getAttribute('href');
        }
        
        // Google 链接
        const googleEl = wrapper.querySelector('a[title="Search on Google"]');
        if (googleEl) {
            result.googleLink = googleEl.getAttribute('href');
        }
        
        // 锚点链接
        result.link = eventInfo.href;
        
        // 中文化预留字段（始终保留）
        result.name_cn = '';
        result.description_cn = '';
        result.example_ts = '';
        result.notes_cn = '';
        result.usage_cn = '';
        result.related = [];
        result.see_also = [];
        result.tags = [];
        
        return result;
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
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 步骤一：获取所有事件地址
        print("=" * 60)
        print("步骤一：获取所有事件地址")
        print("=" * 60)
        events_info = await get_all_event_urls(page)
        print(f"共找到 {len(events_info)} 个事件")
        
        # 步骤二：遍历每个事件提取数据
        print("\n" + "=" * 60)
        print("步骤二：提取事件数据")
        print("=" * 60)
        
        for i, event_info in enumerate(events_info):
            print(f"[{i+1}/{len(events_info)}] {event_info['name']}", end='')
            
            data = await crawl_event(page, event_info)
            if data:
                events.append(data)
                params = len(data['parameters'])
                has_desc = '描述' if data.get('description') else ''
                has_opts = f" Options:{len(data['options'])}" if data.get('options') else ''
                print(f" → {params} 参数 {has_desc}{has_opts}")
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
            "type": "panorama_events",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(events)
        },
        "items": events
    }, "events.json")
    
    # 统计
    print("\n" + "=" * 60)
    print("爬取完成！统计:")
    print("=" * 60)
    print(f"  事件总数: {len(events)} 个")
    
    total_params = sum(len(e['parameters']) for e in events)
    with_desc = sum(1 for e in events if e.get('description'))
    with_opts = sum(1 for e in events if e.get('options'))
    
    print(f"  参数总数: {total_params} 个")
    print(f"  带描述的事件: {with_desc} 个")
    print(f"  带 Options 的事件: {with_opts} 个")


if __name__ == "__main__":
    asyncio.run(main())
