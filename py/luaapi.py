"""
Dota2 Lua API 爬虫
步骤一：获取所有页面地址
步骤二：遍历页面提取数据，按类型分类保存到 JSON
"""
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# 配置
ROOT_URL = "https://moddota.com/api/#!/vscripts"
BASE_URL = "https://moddota.com/api/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "luaapi")


# ==================== 步骤一：获取所有页面地址 ====================

async def get_all_api_urls(page):
    """获取所有 API 页面地址"""
    print(f"正在访问: {ROOT_URL}")
    await page.goto(ROOT_URL, wait_until='networkidle')
    await asyncio.sleep(1)
    
    urls = await page.evaluate('''() => {
        const links = new Set();
        document.querySelectorAll('a.Sidebar__SidebarLink-kKnkkd').forEach(a => {
            const href = a.getAttribute('href');
            if (href && href.startsWith('#!/vscripts/')) {
                links.add('https://moddota.com/api/' + href);
            }
        });
        return Array.from(links);
    }''')
    
    return sorted(urls)


# ==================== 步骤二：页面类型识别与数据提取 ====================

async def detect_page_type(page):
    """检测页面类型：class, enum, constant, function"""
    return await page.evaluate('''() => {
        if (document.querySelector('div[class*="ClassDeclaration__ClassWrapper"]')) return 'class';
        if (document.querySelector('div[class*="Enum__EnumHeader"]')) return 'enum';
        if (document.querySelector('div[class*="Constant__ConstantWrapper"]')) return 'constant';
        if (document.querySelector('div[class*="FunctionDeclaration__FunctionWrapper"]')) return 'function';
        return null;
    }''')


async def extract_class_data(page):
    """提取类数据"""
    return await page.evaluate('''() => {
        const wrapper = document.querySelector('div[class*="ClassDeclaration__ClassWrapper"]');
        if (!wrapper) return null;
        
        // 类名
        const nameEl = wrapper.querySelector('span[class*="ClassDeclaration__ClassName"]');
        const name = nameEl ? nameEl.textContent.trim() : '';
        
        // 继承
        const extendsWrapper = wrapper.querySelector('span[class*="ClassDeclaration__ClassExtendsWrapper"]');
        let extendsName = null;
        let extendsLink = null;
        if (extendsWrapper) {
            const link = extendsWrapper.querySelector('a[class*="types__TypeReferenceLink"]');
            if (link) {
                extendsName = link.textContent.trim();
                extendsLink = link.getAttribute('href');
            }
        }
        
        // 描述
        const descEl = wrapper.querySelector(':scope > div[class*="styles__Description"]');
        const description = descEl ? descEl.textContent.trim() : null;
        
        // 引用数量
        const refEl = wrapper.querySelector('a[class*="ReferencesLink__StyledReferencesLink"]');
        let references = 0;
        if (refEl) {
            const match = refEl.textContent.match(/(\d+)/);
            references = match ? parseInt(match[1]) : 0;
        }
        
        // 可用性
        const serverEl = wrapper.querySelector('div[title="Available on server-side Lua"]');
        const clientEl = wrapper.querySelector('div[title="Available on client-side Lua"]');
        const server = !!serverEl;
        const client = !!clientEl;
        
        // 锚点链接
        const linkEl = wrapper.querySelector('a[class*="ElementLink__StyledElementLink"]');
        const link = linkEl ? linkEl.getAttribute('href') : null;
        
        // 提取字段
        const fields = [];
        const membersContainer = wrapper.querySelector('div[class*="ClassDeclaration__ClassMembers"]');
        if (membersContainer) {
            membersContainer.querySelectorAll(':scope > div[class*="Field__FieldWrapper"]').forEach(fieldEl => {
                const fieldName = fieldEl.getAttribute('id') || '';
                const sigEl = fieldEl.querySelector('div[class*="Field__FieldSignature"]');
                let fieldType = '';
                let fieldTypeLink = null;
                
                if (sigEl) {
                    const typeLink = sigEl.querySelector('a[class*="types__TypeReferenceLink"]');
                    const typeSpan = sigEl.querySelector('span[class*="types__TypeSpan"]');
                    if (typeLink) {
                        fieldType = typeLink.textContent.trim();
                        fieldTypeLink = typeLink.getAttribute('href');
                    } else if (typeSpan) {
                        fieldType = typeSpan.textContent.trim();
                    }
                }
                
                const fieldLinkEl = fieldEl.querySelector('a[class*="ElementLink__StyledElementLink"]');
                
                fields.push({
                    name: fieldName,
                    type: fieldType,
                    typeLink: fieldTypeLink,
                    link: fieldLinkEl ? fieldLinkEl.getAttribute('href') : null,
                    description_cn: '',
                    type_description_cn: '',
                    notes_cn: ''
                });
            });
        }
        
        // 提取方法
        const methods = [];
        if (membersContainer) {
            membersContainer.querySelectorAll(':scope > div[class*="FunctionDeclaration__FunctionWrapper"]').forEach(funcEl => {
                methods.push(extractFunctionFromElement(funcEl));
            });
        }
        
        return {
            name,
            extends: extendsName,
            extendsLink,
            description,
            references,
            server,
            client,
            link,
            name_cn: '',
            description_cn: '',
            notes_cn: '',
            warnings_cn: '',
            example_ts: '',
            common_usage_cn: '',
            related: [],
            see_also: [],
            tags: [],
            deprecated: false,
            since_version: '',
            fields,
            methods
        };
        
        // 内部函数：从元素提取函数数据
        function extractFunctionFromElement(funcEl) {
            const funcName = funcEl.getAttribute('id') || '';
            
            // 签名
            const sigEl = funcEl.querySelector('div[class*="FunctionDeclaration__FunctionSignature"]');
            const signature = sigEl ? sigEl.textContent.trim() : '';
            
            // 描述
            const descEl = funcEl.querySelector('div[class*="styles__Description"]');
            let description = null;
            if (descEl) {
                // 排除参数描述列表
                const clone = descEl.cloneNode(true);
                clone.querySelectorAll('ul, li').forEach(el => el.remove());
                description = clone.textContent.trim() || null;
            }
            
            // 可用性
            const serverEl = funcEl.querySelector('div[title="Available on server-side Lua"]');
            const clientEl = funcEl.querySelector('div[title="Available on client-side Lua"]');
            
            // 链接
            const githubEl = funcEl.querySelector('a[title="Search on GitHub"]');
            const googleEl = funcEl.querySelector('a[title="Search on Google"]');
            const linkEl = funcEl.querySelector('a[class*="ElementLink__StyledElementLink"]');
            
            // 参数
            const parameters = [];
            if (sigEl) {
                sigEl.querySelectorAll('span[class*="types__FunctionParameterWrapper"]').forEach(paramEl => {
                    const spans = paramEl.querySelectorAll(':scope > span');
                    let paramName = '';
                    let paramType = '';
                    let paramTypeLink = null;
                    
                    if (spans.length > 0) {
                        paramName = spans[0].textContent.replace(':', '').trim();
                    }
                    
                    // 类型可能是引用类型或基础类型，可能是联合类型
                    const typeLinks = paramEl.querySelectorAll('a[class*="types__TypeReferenceLink"]');
                    const typeSpans = paramEl.querySelectorAll('span[class*="types__TypeSpan"]');
                    
                    const types = [];
                    paramEl.childNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element
                            if (node.matches && node.matches('a[class*="types__TypeReferenceLink"]')) {
                                types.push(node.textContent.trim());
                                if (!paramTypeLink) paramTypeLink = node.getAttribute('href');
                            } else if (node.matches && node.matches('span[class*="types__TypeSpan"]')) {
                                types.push(node.textContent.trim());
                            }
                        }
                    });
                    
                    // 处理联合类型
                    const fullText = paramEl.textContent;
                    if (fullText.includes('|')) {
                        paramType = types.join('|');
                    } else {
                        paramType = types[types.length - 1] || '';
                    }
                    
                    const isOptional = paramName.endsWith('?');
                    if (isOptional) paramName = paramName.slice(0, -1);
                    
                    parameters.push({
                        name: paramName,
                        type: paramType,
                        typeLink: paramTypeLink,
                        isOptional,
                        description: null,
                        description_cn: '',
                        type_description_cn: ''
                    });
                });
            }
            
            // 参数描述
            funcEl.querySelectorAll('li[class*="FunctionDeclaration__ParameterDescription"]').forEach(li => {
                const text = li.textContent.trim();
                const match = text.match(/^(\w+):\s*(.+)$/);
                if (match) {
                    const param = parameters.find(p => p.name === match[1]);
                    if (param) param.description = match[2];
                }
            });
            
            // 返回值
            let returnType = '';
            let returnTypeLink = null;
            if (sigEl) {
                const sigText = sigEl.textContent;
                const colonIndex = sigText.lastIndexOf('):');
                if (colonIndex !== -1) {
                    const returnPart = sigText.slice(colonIndex + 2).trim();
                    returnType = returnPart;
                    
                    // 查找返回类型链接
                    const allLinks = sigEl.querySelectorAll('a[class*="types__TypeReferenceLink"]');
                    const allSpans = sigEl.querySelectorAll('span[class*="types__TypeSpan"]');
                    // 最后一个类型元素可能是返回值
                    if (allLinks.length > 0) {
                        const lastLink = allLinks[allLinks.length - 1];
                        if (!lastLink.closest('span[class*="types__FunctionParameterWrapper"]')) {
                            returnTypeLink = lastLink.getAttribute('href');
                        }
                    }
                }
            }
            
            // Options对象
            const options = [];
            const optionsContainer = funcEl.querySelector('div[class*="FunctionDeclaration__ObjectReferences"]');
            if (optionsContainer) {
                optionsContainer.querySelectorAll('div[class*="styles__CommonGroupWrapper"]').forEach(optEl => {
                    const optNameEl = optEl.querySelector('span[class*="ObjectType__ObjectName"]');
                    const optName = optNameEl ? optNameEl.textContent.trim() : '';
                    
                    // 继承
                    let optExtends = null;
                    const headerText = optEl.querySelector('div[class*="styles__CommonGroupSignature"]')?.textContent || '';
                    const extendsMatch = headerText.match(/extends\s+(\w+)/);
                    if (extendsMatch) optExtends = extendsMatch[1];
                    
                    // 字段
                    const optFields = [];
                    optEl.querySelectorAll('div[class*="Field__FieldWrapper"]').forEach(fieldEl => {
                        const fieldId = fieldEl.getAttribute('id') || '';
                        const fieldSig = fieldEl.querySelector('div[class*="Field__FieldSignature"]');
                        let fName = fieldId;
                        let fType = '';
                        let fTypeLink = null;
                        let fOptional = false;
                        
                        if (fieldSig) {
                            const sigText = fieldSig.textContent;
                            if (sigText.includes('?:')) {
                                fOptional = true;
                                fName = fName.replace('?', '');
                            }
                            
                            const typeLink = fieldSig.querySelector('a[class*="types__TypeReferenceLink"]');
                            const typeSpan = fieldSig.querySelector('span[class*="types__TypeSpan"]');
                            if (typeLink) {
                                fType = typeLink.textContent.trim();
                                fTypeLink = typeLink.getAttribute('href');
                            } else if (typeSpan) {
                                fType = typeSpan.textContent.trim();
                            }
                        }
                        
                        optFields.push({
                            name: fName.replace('?', ''),
                            type: fType,
                            typeLink: fTypeLink,
                            isOptional: fOptional || fName.includes('?'),
                            description_cn: '',
                            type_description_cn: ''
                        });
                    });
                    
                    options.push({
                        name: optName,
                        extends: optExtends,
                        fields: optFields
                    });
                });
            }
            
            return {
                name: funcName,
                signature,
                description,
                server: !!serverEl,
                client: !!clientEl,
                githubLink: githubEl ? githubEl.getAttribute('href') : null,
                googleLink: googleEl ? googleEl.getAttribute('href') : null,
                link: linkEl ? linkEl.getAttribute('href') : null,
                parameters,
                returnType,
                returnTypeLink,
                options,
                name_cn: '',
                description_cn: '',
                returnType_cn: '',
                returnDescription_cn: '',
                example_ts: '',
                notes_cn: '',
                warnings_cn: '',
                common_usage_cn: '',
                related: [],
                tags: [],
                deprecated: false
            };
        }
    }''')


async def extract_enum_data(page):
    """提取枚举数据"""
    return await page.evaluate('''() => {
        const header = document.querySelector('div[class*="Enum__EnumHeader"]');
        if (!header) return null;
        
        const wrapper = header.closest('div[class*="styles__CommonGroupWrapper"]');
        if (!wrapper) return null;
        
        // 枚举名称
        const sigEl = header.querySelector('div[class*="styles__CommonGroupSignature"]');
        let name = '';
        if (sigEl) {
            // 移除图标等，只取文本
            const clone = sigEl.cloneNode(true);
            clone.querySelectorAll('svg, img').forEach(el => el.remove());
            name = clone.textContent.trim();
        }
        
        // 描述
        const descEl = wrapper.querySelector(':scope > div[class*="styles__Description"]');
        const description = descEl ? descEl.textContent.trim() : null;
        
        // 引用数量
        const refEl = wrapper.querySelector('a[class*="ReferencesLink__StyledReferencesLink"]');
        let references = 0;
        if (refEl) {
            const match = refEl.textContent.match(/(\d+)/);
            references = match ? parseInt(match[1]) : 0;
        }
        
        // 锚点链接
        const linkEl = wrapper.querySelector('a[class*="ElementLink__StyledElementLink"]');
        const link = linkEl ? linkEl.getAttribute('href') : null;
        
        // 枚举成员
        const members = [];
        const membersContainer = wrapper.querySelector('div[class*="Enum__EnumMembers"]');
        if (membersContainer) {
            membersContainer.querySelectorAll('div[class*="Enum__EnumMemberWrapper"]').forEach(memberEl => {
                const memberId = memberEl.getAttribute('id') || '';
                const memberSig = memberEl.querySelector('div[class*="styles__CommonGroupSignature"]');
                
                let memberName = memberId;
                let memberValue = null;
                
                if (memberSig) {
                    const sigText = memberSig.textContent.trim();
                    const eqIndex = sigText.indexOf('=');
                    if (eqIndex !== -1) {
                        memberName = sigText.slice(0, eqIndex).trim();
                        const valueStr = sigText.slice(eqIndex + 1).trim();
                        memberValue = isNaN(valueStr) ? valueStr : parseInt(valueStr);
                    }
                }
                
                // 成员描述
                const memberDescEl = memberEl.querySelector('div[class*="styles__Description"]');
                const memberDesc = memberDescEl ? memberDescEl.textContent.trim() : null;
                
                members.push({
                    name: memberName,
                    value: memberValue,
                    description: memberDesc,
                    description_cn: ''
                });
            });
        }
        
        return {
            name,
            description,
            references,
            link,
            members,
            name_cn: '',
            description_cn: '',
            example_ts: '',
            notes_cn: '',
            common_usage_cn: '',
            related: [],
            see_also: [],
            tags: []
        };
    }''')


async def extract_constant_data(page):
    """提取常量数据（常量页面可能有多个常量）"""
    return await page.evaluate('''() => {
        const constants = [];
        
        document.querySelectorAll('div[class*="Constant__ConstantWrapper"]').forEach(wrapper => {
            const name = wrapper.getAttribute('id') || '';
            
            const sigEl = wrapper.querySelector('div[class*="Constant__ConstantSignature"]');
            let value = null;
            let valueType = 'unknown';
            
            if (sigEl) {
                const sigText = sigEl.textContent.trim();
                const colonIndex = sigText.indexOf(':');
                if (colonIndex !== -1) {
                    const valueStr = sigText.slice(colonIndex + 1).trim();
                    if (!isNaN(valueStr)) {
                        value = valueStr.includes('.') ? parseFloat(valueStr) : parseInt(valueStr);
                        valueType = valueStr.includes('.') ? 'float' : 'int';
                    } else {
                        value = valueStr;
                        valueType = 'string';
                    }
                }
            }
            
            const linkEl = wrapper.querySelector('a[class*="ElementLink__StyledElementLink"]');
            
            constants.push({
                name,
                value,
                valueType,
                link: linkEl ? linkEl.getAttribute('href') : null,
                name_cn: '',
                description_cn: '',
                example_ts: '',
                notes_cn: '',
                common_usage_cn: '',
                related: [],
                see_also: [],
                tags: []
            });
        });
        
        return constants;
    }''')


async def extract_function_data(page):
    """提取全局函数数据（函数页面可能有多个函数）"""
    return await page.evaluate('''() => {
        const functions = [];
        
        // 只提取不在类容器内的函数
        document.querySelectorAll('div[class*="FunctionDeclaration__FunctionWrapper"]').forEach(funcEl => {
            // 跳过类方法
            if (funcEl.closest('div[class*="ClassDeclaration__ClassWrapper"]')) return;
            
            functions.push(extractFunctionFromElement(funcEl));
        });
        
        return functions;
        
        function extractFunctionFromElement(funcEl) {
            const funcName = funcEl.getAttribute('id') || '';
            
            const sigEl = funcEl.querySelector('div[class*="FunctionDeclaration__FunctionSignature"]');
            const signature = sigEl ? sigEl.textContent.trim() : '';
            
            const descEl = funcEl.querySelector('div[class*="styles__Description"]');
            let description = null;
            if (descEl) {
                const clone = descEl.cloneNode(true);
                clone.querySelectorAll('ul, li').forEach(el => el.remove());
                description = clone.textContent.trim() || null;
            }
            
            const serverEl = funcEl.querySelector('div[title="Available on server-side Lua"]');
            const clientEl = funcEl.querySelector('div[title="Available on client-side Lua"]');
            
            const githubEl = funcEl.querySelector('a[title="Search on GitHub"]');
            const googleEl = funcEl.querySelector('a[title="Search on Google"]');
            const linkEl = funcEl.querySelector('a[class*="ElementLink__StyledElementLink"]');
            
            // 参数
            const parameters = [];
            if (sigEl) {
                sigEl.querySelectorAll('span[class*="types__FunctionParameterWrapper"]').forEach(paramEl => {
                    const spans = paramEl.querySelectorAll(':scope > span');
                    let paramName = '';
                    let paramType = '';
                    let paramTypeLink = null;
                    
                    if (spans.length > 0) {
                        paramName = spans[0].textContent.replace(':', '').trim();
                    }
                    
                    const types = [];
                    paramEl.querySelectorAll('a[class*="types__TypeReferenceLink"], span[class*="types__TypeSpan"]').forEach(el => {
                        types.push(el.textContent.trim());
                        if (el.matches('a') && !paramTypeLink) {
                            paramTypeLink = el.getAttribute('href');
                        }
                    });
                    
                    const fullText = paramEl.textContent;
                    paramType = fullText.includes('|') ? types.join('|') : (types[types.length - 1] || '');
                    
                    const isOptional = paramName.endsWith('?');
                    if (isOptional) paramName = paramName.slice(0, -1);
                    
                    parameters.push({
                        name: paramName,
                        type: paramType,
                        typeLink: paramTypeLink,
                        isOptional,
                        description: null,
                        description_cn: '',
                        type_description_cn: ''
                    });
                });
            }
            
            // 参数描述
            funcEl.querySelectorAll('li[class*="FunctionDeclaration__ParameterDescription"]').forEach(li => {
                const text = li.textContent.trim();
                const match = text.match(/^(\w+):\s*(.+)$/);
                if (match) {
                    const param = parameters.find(p => p.name === match[1]);
                    if (param) param.description = match[2];
                }
            });
            
            // 返回值
            let returnType = '';
            let returnTypeLink = null;
            if (sigEl) {
                const sigText = sigEl.textContent;
                const colonIndex = sigText.lastIndexOf('):');
                if (colonIndex !== -1) {
                    returnType = sigText.slice(colonIndex + 2).trim();
                    
                    const allLinks = sigEl.querySelectorAll('a[class*="types__TypeReferenceLink"]');
                    if (allLinks.length > 0) {
                        const lastLink = allLinks[allLinks.length - 1];
                        if (!lastLink.closest('span[class*="types__FunctionParameterWrapper"]')) {
                            returnTypeLink = lastLink.getAttribute('href');
                        }
                    }
                }
            }
            
            // Options对象
            const options = [];
            const optionsContainer = funcEl.querySelector('div[class*="FunctionDeclaration__ObjectReferences"]');
            if (optionsContainer) {
                optionsContainer.querySelectorAll('div[class*="styles__CommonGroupWrapper"]').forEach(optEl => {
                    const optNameEl = optEl.querySelector('span[class*="ObjectType__ObjectName"]');
                    const optName = optNameEl ? optNameEl.textContent.trim() : '';
                    
                    let optExtends = null;
                    const headerText = optEl.querySelector('div[class*="styles__CommonGroupSignature"]')?.textContent || '';
                    const extendsMatch = headerText.match(/extends\s+(\w+)/);
                    if (extendsMatch) optExtends = extendsMatch[1];
                    
                    const optFields = [];
                    optEl.querySelectorAll('div[class*="Field__FieldWrapper"]').forEach(fieldEl => {
                        const fieldId = fieldEl.getAttribute('id') || '';
                        const fieldSig = fieldEl.querySelector('div[class*="Field__FieldSignature"]');
                        let fName = fieldId;
                        let fType = '';
                        let fTypeLink = null;
                        let fOptional = fieldId.includes('?');
                        
                        if (fieldSig) {
                            const typeLink = fieldSig.querySelector('a[class*="types__TypeReferenceLink"]');
                            const typeSpan = fieldSig.querySelector('span[class*="types__TypeSpan"]');
                            if (typeLink) {
                                fType = typeLink.textContent.trim();
                                fTypeLink = typeLink.getAttribute('href');
                            } else if (typeSpan) {
                                fType = typeSpan.textContent.trim();
                            }
                        }
                        
                        optFields.push({
                            name: fName.replace('?', ''),
                            type: fType,
                            typeLink: fTypeLink,
                            isOptional: fOptional,
                            description_cn: '',
                            type_description_cn: ''
                        });
                    });
                    
                    options.push({
                        name: optName,
                        extends: optExtends,
                        fields: optFields
                    });
                });
            }
            
            return {
                name: funcName,
                signature,
                description,
                server: !!serverEl,
                client: !!clientEl,
                githubLink: githubEl ? githubEl.getAttribute('href') : null,
                googleLink: googleEl ? googleEl.getAttribute('href') : null,
                link: linkEl ? linkEl.getAttribute('href') : null,
                parameters,
                returnType,
                returnTypeLink,
                options,
                name_cn: '',
                description_cn: '',
                returnType_cn: '',
                returnDescription_cn: '',
                example_ts: '',
                notes_cn: '',
                warnings_cn: '',
                common_usage_cn: '',
                related: [],
                tags: [],
                deprecated: false
            };
        }
    }''')


# ==================== 主流程 ====================

async def crawl_page(page, url):
    """爬取单个页面"""
    try:
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(0.5)
        
        page_type = await detect_page_type(page)
        
        if page_type == 'class':
            data = await extract_class_data(page)
            return ('class', data) if data else None
        elif page_type == 'enum':
            data = await extract_enum_data(page)
            return ('enum', data) if data else None
        elif page_type == 'constant':
            data = await extract_constant_data(page)
            return ('constant', data) if data else None
        elif page_type == 'function':
            data = await extract_function_data(page)
            return ('function', data) if data else None
        else:
            print(f"  未知页面类型: {url}")
            return None
    except Exception as e:
        print(f"  爬取失败 {url}: {e}")
        return None


def save_json(data, filename):
    """保存 JSON 文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存: {filepath}")


async def main():
    """主函数"""
    # 数据容器
    classes = []
    enums = []
    constants = []
    functions = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 步骤一：获取所有页面地址
        print("=" * 50)
        print("步骤一：获取所有页面地址")
        print("=" * 50)
        urls = await get_all_api_urls(page)
        print(f"共找到 {len(urls)} 个页面")
        
        # 步骤二：遍历每个页面提取数据
        print("\n" + "=" * 50)
        print("步骤二：提取页面数据")
        print("=" * 50)
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {url}")
            result = await crawl_page(page, url)
            
            if result:
                page_type, data = result
                if page_type == 'class':
                    classes.append(data)
                    print(f"  → 类: {data['name']}")
                elif page_type == 'enum':
                    enums.append(data)
                    print(f"  → 枚举: {data['name']}")
                elif page_type == 'constant':
                    # 常量页面可能有多个常量
                    if isinstance(data, list):
                        constants.extend(data)
                        print(f"  → 常量: {len(data)} 个")
                    else:
                        constants.append(data)
                        print(f"  → 常量: {data['name']}")
                elif page_type == 'function':
                    # 函数页面可能有多个函数
                    if isinstance(data, list):
                        functions.extend(data)
                        print(f"  → 函数: {len(data)} 个")
                    else:
                        functions.append(data)
                        print(f"  → 函数: {data['name']}")
        
        await browser.close()
    
    # 步骤三：保存 JSON 文件
    print("\n" + "=" * 50)
    print("步骤三：保存 JSON 文件")
    print("=" * 50)
    
    now = datetime.now().isoformat()
    
    save_json({
        "metadata": {
            "type": "classes",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(classes)
        },
        "items": classes
    }, "classes.json")
    
    save_json({
        "metadata": {
            "type": "enums",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(enums)
        },
        "items": enums
    }, "enums.json")
    
    save_json({
        "metadata": {
            "type": "constants",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(constants)
        },
        "items": constants
    }, "constants.json")
    
    save_json({
        "metadata": {
            "type": "functions",
            "source": ROOT_URL,
            "crawledAt": now,
            "count": len(functions)
        },
        "items": functions
    }, "functions.json")
    
    # 统计
    print("\n" + "=" * 50)
    print("爬取完成！统计:")
    print("=" * 50)
    print(f"  类: {len(classes)} 个")
    print(f"  枚举: {len(enums)} 个")
    print(f"  常量: {len(constants)} 个")
    print(f"  函数: {len(functions)} 个")
    print(f"  总计: {len(classes) + len(enums) + len(constants) + len(functions)} 个")


if __name__ == "__main__":
    asyncio.run(main())
