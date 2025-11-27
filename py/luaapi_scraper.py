"""
Dota2 Lua API 爬虫 - 使用 Playwright 从 moddota.com 抓取 Lua API 文档

功能:
- 抓取类、枚举、全局函数、常量等所有 API 信息
- 提取方法参数、返回类型、描述、可用性(服务端/客户端)
- 提取嵌套的 Options 结构 (如 ApplyDamageOptions)
- 提取类字段 (如 Vector 的 x, y, z)
- 结果保存为 JSON 格式
"""
import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

# 配置
BASE_URL = "https://moddota.com/api/#!/vscripts"
OUTPUT_DIR = r"d:\Ability\API\data\lua_api"
REQUEST_DELAY = 0.3  # 请求间隔(秒)
PAGE_TIMEOUT = 30000  # 页面加载超时(毫秒)
MAX_RETRIES = 3  # 最大重试次数

# 从 luaapi.py 导入 URL 列表
try:
    from luaapi import LUA_API_URLS
except ImportError:
    # 如果导入失败，使用内置列表
    print("警告: 无法从 luaapi.py 导入 URL 列表，使用内置列表")
    LUA_API_URLS = []


class LuaAPIScraper:
    """Lua API 爬虫类"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.failed_urls: List[str] = []
        self.success_count = 0
        self.error_count = 0
    
    async def init_browser(self):
        """初始化浏览器"""
        print("正在启动浏览器...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        print("浏览器启动成功")
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("浏览器已关闭")

    async def wait_for_content(self):
        """等待页面内容加载完成"""
        try:
            await self.page.wait_for_selector('main', timeout=10000)
            # 等待动态内容渲染
            await asyncio.sleep(0.8)
        except PlaywrightTimeout:
            print("  警告: 等待 main 元素超时")
        except Exception as e:
            print(f"  警告: 等待内容时出错: {e}")

    async def extract_page_data(self, url: str, retry_count: int = 0) -> dict:
        """提取单个页面的数据，支持重试"""
        page_name = url.split('/')[-1]
        
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=PAGE_TIMEOUT)
            await self.wait_for_content()
        except PlaywrightTimeout:
            if retry_count < MAX_RETRIES:
                print(f"  超时，重试 ({retry_count + 1}/{MAX_RETRIES})...")
                await asyncio.sleep(2)
                return await self.extract_page_data(url, retry_count + 1)
            print(f"  错误: 页面加载超时")
            self.failed_urls.append(url)
            self.error_count += 1
            return {"error": "timeout", "url": url, "name": page_name}
        except Exception as e:
            if retry_count < MAX_RETRIES:
                print(f"  出错，重试 ({retry_count + 1}/{MAX_RETRIES})...")
                await asyncio.sleep(2)
                return await self.extract_page_data(url, retry_count + 1)
            print(f"  错误: {e}")
            self.failed_urls.append(url)
            self.error_count += 1
            return {"error": str(e), "url": url, "name": page_name}

        # 判断页面类型并提取数据
        try:
            if page_name == "constants":
                data = await self.extract_constants()
            elif page_name == "functions":
                data = await self.extract_functions()
            else:
                data = await self.extract_class_or_enum()
            
            # 检查是否提取成功
            if data.get("error"):
                self.error_count += 1
                self.failed_urls.append(url)
            else:
                self.success_count += 1
            
            return data
        except Exception as e:
            print(f"  提取数据时出错: {e}")
            traceback.print_exc()
            self.error_count += 1
            self.failed_urls.append(url)
            return {"error": str(e), "url": url, "name": page_name}

    async def extract_constants(self) -> dict:
        """提取常量页面"""
        return await self.page.evaluate("""
        () => {
            const result = { type: 'constants', constants: [] };
            const container = document.querySelector('main > div:nth-child(2)');
            if (container) {
                container.querySelectorAll(':scope > div').forEach(el => {
                    const textEl = el.querySelector('div');
                    if (textEl) {
                        const text = textEl.textContent.trim();
                        const match = text.match(/^(\\w+):\\s*(-?\\d+)/);
                        if (match) {
                            result.constants.push({
                                name: match[1],
                                value: parseInt(match[2])
                            });
                        }
                    }
                });
            }
            return result;
        }
        """)

    async def extract_functions(self) -> dict:
        """提取全局函数页面"""
        return await self.page.evaluate(EXTRACT_FUNCTIONS_JS)

    async def extract_class_or_enum(self) -> dict:
        """提取类或枚举页面"""
        return await self.page.evaluate(EXTRACT_CLASS_ENUM_JS)

    async def scrape_all(self, urls: List[str] = None):
        """抓取所有页面"""
        if urls is None:
            urls = LUA_API_URLS
        
        if not urls:
            print("错误: URL 列表为空")
            return []
        
        await self.init_browser()
        all_data = []
        total = len(urls)
        start_time = datetime.now()
        
        print(f"\n开始抓取 {total} 个页面...\n")
        
        for i, url in enumerate(urls):
            page_name = url.split('/')[-1]
            print(f"[{i+1:3d}/{total}] {page_name:<45}", end=" ")
            
            data = await self.extract_page_data(url)
            data["url"] = url
            data["name"] = page_name
            all_data.append(data)
            
            # 显示结果
            if data.get("error"):
                print("❌ 失败")
            else:
                data_type = data.get("type", "unknown")
                print(f"✓ {data_type}")
            
            await asyncio.sleep(REQUEST_DELAY)
        
        await self.close_browser()
        
        # 统计
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"抓取完成!")
        print(f"  总计: {total} 个页面")
        print(f"  成功: {self.success_count} 个")
        print(f"  失败: {self.error_count} 个")
        print(f"  耗时: {elapsed:.1f} 秒")
        
        if self.failed_urls:
            print(f"\n失败的 URL:")
            for url in self.failed_urls:
                print(f"  - {url}")
        
        return all_data

    def save_results(self, data: list):
        """保存结果到 JSON 文件"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 分类保存
        classes, enums, functions_data, constants_data, errors = [], [], [], [], []
        
        for item in data:
            if item.get("error"):
                errors.append(item)
                continue
            
            t = item.get("type", "")
            if t == "class":
                classes.append(item)
            elif t == "enum":
                enums.append(item)
            elif t == "functions":
                functions_data.append(item)
            elif t == "constants":
                constants_data.append(item)
        
        # 生成元数据
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_pages": len(data),
            "success_count": len(data) - len(errors),
            "error_count": len(errors),
            "classes_count": len(classes),
            "enums_count": len(enums),
            "functions_pages": len(functions_data),
            "constants_pages": len(constants_data)
        }
        
        # 保存各类型文件
        print(f"\n保存结果到: {OUTPUT_DIR}")
        self._save_json("classes.json", {"metadata": metadata, "data": classes})
        self._save_json("enums.json", {"metadata": metadata, "data": enums})
        self._save_json("functions.json", {"metadata": metadata, "data": functions_data})
        self._save_json("constants.json", {"metadata": metadata, "data": constants_data})
        self._save_json("all_data.json", {"metadata": metadata, "data": data})
        
        if errors:
            self._save_json("errors.json", {"metadata": metadata, "data": errors})
        
        print(f"\n统计:")
        print(f"  类: {len(classes)} 个")
        print(f"  枚举: {len(enums)} 个")
        print(f"  函数页: {len(functions_data)} 个")
        print(f"  常量页: {len(constants_data)} 个")
        if errors:
            print(f"  错误: {len(errors)} 个")

    def _save_json(self, filename: str, data: Any):
        """保存单个 JSON 文件"""
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ {filename}")


# JS 提取代码 - 全局函数
EXTRACT_FUNCTIONS_JS = '''() => {
    const result = { type: "functions", functions: [] };
    
    document.querySelectorAll(".FunctionDeclaration__FunctionWrapper-gYcoXK").forEach(funcEl => {
        const func = {
            name: funcEl.id || "",
            parameters: [],
            returnType: null,
            returnTypeLink: null,
            description: "",
            server: false,
            client: false,
            options: []
        };

        // 签名
        const sig = funcEl.querySelector(".FunctionDeclaration__FunctionSignature-eAuxgh");
        if (sig) {
            sig.querySelectorAll(".types__FunctionParameterWrapper-bUssSi").forEach(paramEl => {
                const text = paramEl.textContent;
                const colonIdx = text.indexOf(":");
                const paramName = colonIdx > -1 ? text.substring(0, colonIdx).trim() : text.trim();
                const typeLink = paramEl.querySelector("a.types__TypeReferenceLink-bpPxLF");
                const typeSpan = paramEl.querySelector(".types__TypeSpan-bcJynW");
                func.parameters.push({
                    name: paramName,
                    type: typeLink?.textContent.trim() || typeSpan?.textContent.trim() || "",
                    typeLink: typeLink?.getAttribute("href") || null,
                    optional: paramName.endsWith("?")
                });
            });

            const allTypeLinks = sig.querySelectorAll(":scope > a.types__TypeReferenceLink-bpPxLF");
            const allTypeSpans = sig.querySelectorAll(":scope > .types__TypeSpan-bcJynW");
            if (allTypeLinks.length > 0) {
                func.returnType = allTypeLinks[allTypeLinks.length - 1].textContent.trim();
                func.returnTypeLink = allTypeLinks[allTypeLinks.length - 1].getAttribute("href");
            } else if (allTypeSpans.length > 0) {
                func.returnType = allTypeSpans[allTypeSpans.length - 1].textContent.trim();
            }
        }

        // 描述
        const descEl = funcEl.querySelector(".styles__Description-enGWpD");
        if (descEl) func.description = descEl.textContent.trim();

        // 可用性
        const badges = funcEl.querySelector(".styles__ElementBadges-frIvDt");
        if (badges) {
            func.server = !!badges.querySelector("[title*='Available on server']");
            func.client = !!badges.querySelector("[title*='Available on client']");
        }

        // 嵌套 Options 结构
        funcEl.querySelectorAll(".FunctionDeclaration__ObjectReferences-icrNNO .styles__CommonGroupWrapper-hQAAsg").forEach(optContainer => {
            const optNameEl = optContainer.querySelector(".ObjectType__ObjectName-fsElmu");
            if (optNameEl) {
                const optObj = { name: optNameEl.textContent.trim(), fields: [] };
                optContainer.querySelectorAll(".Field__FieldWrapper-TgvHu").forEach(fieldEl => {
                    const fieldSig = fieldEl.querySelector(".Field__FieldSignature-septJ");
                    if (fieldSig) {
                        const fieldText = fieldSig.textContent;
                        const colonIdx = fieldText.indexOf(":");
                        const fieldName = colonIdx > -1 ? fieldText.substring(0, colonIdx).trim() : "";
                        const typeLink = fieldSig.querySelector("a.types__TypeReferenceLink-bpPxLF");
                        const typeSpan = fieldSig.querySelector(".types__TypeSpan-bcJynW");
                        optObj.fields.push({
                            name: fieldName,
                            type: typeLink?.textContent.trim() || typeSpan?.textContent.trim() || "",
                            typeLink: typeLink?.getAttribute("href") || null,
                            optional: fieldName.endsWith("?")
                        });
                    }
                });
                if (optObj.fields.length > 0) func.options.push(optObj);
            }
        });

        result.functions.push(func);
    });
    
    return result;
}'''


# JS 提取代码 - 类和枚举
EXTRACT_CLASS_ENUM_JS = '''() => {
    const main = document.querySelector("main");
    if (!main) return { error: "main not found" };

    // 检测页面类型
    const isEnum = !!main.querySelector(".Enum__EnumWrapper-cLpxgT, .Enum__EnumMember-hgJCej");
    
    if (isEnum) {
        return extractEnum();
    } else {
        return extractClass();
    }

    function extractEnum() {
        const result = {
            type: "enum",
            name: "",
            description: "",
            references: null,
            members: []
        };

        // 枚举名
        const nameEl = main.querySelector(".Enum__EnumName-fVwvOr, .styles__CommonGroupSignature-gODApT");
        if (nameEl) result.name = nameEl.textContent.trim();

        // 描述
        const descEl = main.querySelector(".styles__Description-enGWpD");
        if (descEl) result.description = descEl.textContent.trim();

        // 引用数
        const refEl = main.querySelector(".References__ReferencesLink-cMYVuI");
        if (refEl) {
            const match = refEl.textContent.match(/(\\d+)/);
            if (match) result.references = parseInt(match[1]);
        }

        // 枚举成员
        main.querySelectorAll(".Enum__EnumMember-hgJCej, .styles__CommonGroupWrapper-hQAAsg").forEach(memberEl => {
            const sig = memberEl.querySelector(".Enum__EnumMemberSignature-eNJwJV, .styles__CommonGroupSignature-gODApT");
            if (sig) {
                const text = sig.textContent.trim();
                const match = text.match(/^(\\w+)\\s*=\\s*(-?\\d+)/);
                if (match) {
                    const member = {
                        name: match[1],
                        value: parseInt(match[2]),
                        description: ""
                    };
                    const descEl = memberEl.querySelector(".styles__Description-enGWpD");
                    if (descEl) member.description = descEl.textContent.trim();
                    result.members.push(member);
                }
            }
        });

        return result;
    }

    function extractClass() {
        const result = {
            type: "class",
            name: "",
            description: "",
            extends: null,
            extendsLink: null,
            references: null,
            server: false,
            client: false,
            fields: [],
            methods: []
        };

        // 类头部
        const header = main.querySelector(".styles__CommonGroupWrapper-hQAAsg");
        if (!header) return result;

        // 类名
        const nameEl = header.querySelector(".Class__ClassName-hbPVWh");
        if (nameEl) {
            const text = nameEl.textContent.trim();
            const idx = text.indexOf("extends");
            result.name = idx > -1 ? text.substring(0, idx).trim() : text;
        }

        // 继承
        const extendsEl = header.querySelector(".Class__ExtendsLink-jOYDME a");
        if (extendsEl) {
            result.extends = extendsEl.textContent.trim();
            result.extendsLink = extendsEl.getAttribute("href");
        }

        // 描述
        const descEl = header.querySelector(".styles__Description-enGWpD");
        if (descEl) result.description = descEl.textContent.trim();

        // 引用数
        const refEl = header.querySelector(".References__ReferencesLink-cMYVuI");
        if (refEl) {
            const match = refEl.textContent.match(/(\\d+)/);
            if (match) result.references = parseInt(match[1]);
        }

        // 可用性
        const badges = header.querySelector(".styles__ElementBadges-frIvDt");
        if (badges) {
            result.server = !!badges.querySelector("[title*='Available on server']");
            result.client = !!badges.querySelector("[title*='Available on client']");
        }

        // 字段 (如 Vector 的 x, y, z)
        main.querySelectorAll(".Field__FieldWrapper-TgvHu").forEach(fieldEl => {
            // 排除方法内的字段
            if (fieldEl.closest(".FunctionDeclaration__ObjectReferences-icrNNO")) return;
            
            const sig = fieldEl.querySelector(".Field__FieldSignature-septJ");
            if (sig) {
                const text = sig.textContent.trim();
                const colonIdx = text.indexOf(":");
                const fieldName = colonIdx > -1 ? text.substring(0, colonIdx).trim() : text;
                const typeLink = sig.querySelector("a.types__TypeReferenceLink-bpPxLF");
                const typeSpan = sig.querySelector(".types__TypeSpan-bcJynW");
                result.fields.push({
                    name: fieldName,
                    type: typeLink?.textContent.trim() || typeSpan?.textContent.trim() || "",
                    typeLink: typeLink?.getAttribute("href") || null,
                    optional: fieldName.endsWith("?")
                });
            }
        });

        // 方法
        main.querySelectorAll(".FunctionDeclaration__FunctionWrapper-gYcoXK").forEach(methodEl => {
            const method = {
                name: methodEl.id || "",
                parameters: [],
                returnType: null,
                returnTypeLink: null,
                description: "",
                server: false,
                client: false,
                options: []
            };

            // 签名
            const sig = methodEl.querySelector(".FunctionDeclaration__FunctionSignature-eAuxgh");
            if (sig) {
                sig.querySelectorAll(".types__FunctionParameterWrapper-bUssSi").forEach(paramEl => {
                    const text = paramEl.textContent;
                    const colonIdx = text.indexOf(":");
                    const paramName = colonIdx > -1 ? text.substring(0, colonIdx).trim() : text.trim();
                    const typeLink = paramEl.querySelector("a.types__TypeReferenceLink-bpPxLF");
                    const typeSpan = paramEl.querySelector(".types__TypeSpan-bcJynW");
                    method.parameters.push({
                        name: paramName,
                        type: typeLink?.textContent.trim() || typeSpan?.textContent.trim() || "",
                        typeLink: typeLink?.getAttribute("href") || null,
                        optional: paramName.endsWith("?")
                    });
                });

                // 返回类型
                const retLinks = sig.querySelectorAll(":scope > a.types__TypeReferenceLink-bpPxLF");
                const retSpans = sig.querySelectorAll(":scope > .types__TypeSpan-bcJynW");
                if (retLinks.length > 0) {
                    method.returnType = retLinks[retLinks.length - 1].textContent.trim();
                    method.returnTypeLink = retLinks[retLinks.length - 1].getAttribute("href");
                } else if (retSpans.length > 0) {
                    method.returnType = retSpans[retSpans.length - 1].textContent.trim();
                }
            }

            // 描述
            const descEl = methodEl.querySelector(".styles__Description-enGWpD");
            if (descEl) method.description = descEl.textContent.trim();

            // 可用性
            const badges = methodEl.querySelector(".styles__ElementBadges-frIvDt");
            if (badges) {
                method.server = !!badges.querySelector("[title*='Available on server']");
                method.client = !!badges.querySelector("[title*='Available on client']");
            }

            // 嵌套 Options
            methodEl.querySelectorAll(".FunctionDeclaration__ObjectReferences-icrNNO .styles__CommonGroupWrapper-hQAAsg").forEach(optContainer => {
                const optNameEl = optContainer.querySelector(".ObjectType__ObjectName-fsElmu");
                if (optNameEl) {
                    const optObj = { name: optNameEl.textContent.trim(), fields: [] };
                    optContainer.querySelectorAll(".Field__FieldWrapper-TgvHu").forEach(fieldEl => {
                        const fieldSig = fieldEl.querySelector(".Field__FieldSignature-septJ");
                        if (fieldSig) {
                            const fieldText = fieldSig.textContent;
                            const colonIdx = fieldText.indexOf(":");
                            const fieldName = colonIdx > -1 ? fieldText.substring(0, colonIdx).trim() : "";
                            const typeLink = fieldSig.querySelector("a.types__TypeReferenceLink-bpPxLF");
                            const typeSpan = fieldSig.querySelector(".types__TypeSpan-bcJynW");
                            optObj.fields.push({
                                name: fieldName,
                                type: typeLink?.textContent.trim() || typeSpan?.textContent.trim() || "",
                                typeLink: typeLink?.getAttribute("href") || null,
                                optional: fieldName.endsWith("?")
                            });
                        }
                    });
                    if (optObj.fields.length > 0) method.options.push(optObj);
                }
            });

            result.methods.push(method);
        });

        return result;
    }
}'''


async def main():
    """主函数"""
    print("=" * 60)
    print("Dota2 Lua API 爬虫")
    print(f"目标: {len(LUA_API_URLS)} 个页面")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    
    scraper = LuaAPIScraper()
    
    try:
        data = await scraper.scrape_all()
        scraper.save_results(data)
        print("\n爬取完成!")
    except KeyboardInterrupt:
        print("\n用户中断")
        await scraper.close_browser()
    except Exception as e:
        print(f"\n发生错误: {e}")
        traceback.print_exc()
        await scraper.close_browser()


def test_single_page(url: str):
    """测试抓取单个页面"""
    async def _test():
        scraper = LuaAPIScraper()
        await scraper.init_browser()
        data = await scraper.extract_page_data(url)
        await scraper.close_browser()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return data
    return asyncio.run(_test())


if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test" and len(sys.argv) > 2:
            # 测试单个 URL
            test_single_page(sys.argv[2])
        elif sys.argv[1] == "--help":
            print("用法:")
            print("  python luaapi_scraper.py          # 抓取所有页面")
            print("  python luaapi_scraper.py --test URL  # 测试单个页面")
        else:
            print(f"未知参数: {sys.argv[1]}")
    else:
        asyncio.run(main())
