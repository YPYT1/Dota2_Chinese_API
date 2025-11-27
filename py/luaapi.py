"""
步骤一：获取所有 Lua API 页面地址
根路径为 https://moddota.com/api/#!/vscripts，通过选择器 a.Sidebar__SidebarLink-kKnkkd 
找到所有侧边栏链接，提取其 href 属性，然后拼接根路径得到完整地址。
"""
import asyncio
from playwright.async_api import async_playwright

# 配置
ROOT_URL = "https://moddota.com/api/#!/vscripts"
BASE_URL = "https://moddota.com/api/"


async def get_all_api_urls():
    """获取所有 API 页面地址"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"正在访问: {ROOT_URL}")
        await page.goto(ROOT_URL, wait_until='networkidle')
        await asyncio.sleep(1)  # 等待侧边栏加载
        
        # 提取所有链接
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
        
        await browser.close()
        return urls


async def main():
    urls = await get_all_api_urls()
    
    print(f"\n共找到 {len(urls)} 个 API 页面地址:\n")
    for url in sorted(urls):
        print(url)


if __name__ == "__main__":
    asyncio.run(main())
