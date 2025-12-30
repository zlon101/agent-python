"""
Chrome DevTools Protocol (CDP) 端口检测模块
"""

import asyncio
from typing import Optional


async def find_chrome_cdp_url(ports: list[int] = [9422, 9222, 9223, 9224]) -> Optional[str]:
    """
    自动查找可用的 Chrome CDP 端口
    Args:
        ports: 要检测的端口列表
    Returns:
        str: CDP URL (例如 "http://localhost:9222")
        None: 如果未找到可用端口
    """
    try:
        import aiohttp
    except ImportError:
        print("⚠️  aiohttp not installed. Install with: pip install aiohttp")
        return None
    
    for port in ports:
        url = f"http://localhost:{port}"
        version_url = f"{url}/json/version"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    version_url, 
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        browser_info = data.get('Browser', 'Unknown')
                        websocket_url = data.get('webSocketDebuggerUrl', '')
                        
                        print(f"✅ Found Chrome at port {port}")
                        print(f"   Browser: {browser_info}")
                        
                        if websocket_url:
                            print(f"   WebSocket: {websocket_url}")
                        
                        return url
        except asyncio.TimeoutError:
            continue
        except aiohttp.ClientError:
            continue
        except Exception as e:
            print(f"⚠️  Error checking port {port}: {str(e)}")
            continue
    
    return None


async def check_cdp_connection(cdp_url: str) -> bool:
    """
    检查 CDP 连接是否可用
    Args:
        cdp_url: CDP URL
    Returns:
        bool: 连接是否可用
    """
    try:
        import aiohttp
    except ImportError:
        return False
    
    version_url = f"{cdp_url}/json/version"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                version_url,
                timeout=aiohttp.ClientTimeout(total=3)
            ) as resp:
                return resp.status == 200
    except:
        return False


async def get_chrome_pages(cdp_url: str) -> list[dict]:
    """
    获取 Chrome 中所有打开的页面信息
    
    Args:
        cdp_url: CDP URL
        
    Returns:
        list: 页面信息列表
    """
    try:
        import aiohttp
    except ImportError:
        return []
    
    list_url = f"{cdp_url}/json/list"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                list_url,
                timeout=aiohttp.ClientTimeout(total=3)
            ) as resp:
                if resp.status == 200:
                    pages = await resp.json()
                    return [
                        {
                            "id": page.get("id"),
                            "title": page.get("title"),
                            "url": page.get("url"),
                            "type": page.get("type")
                        }
                        for page in pages
                        if page.get("type") == "page"
                    ]
    except:
        pass
    
    return []