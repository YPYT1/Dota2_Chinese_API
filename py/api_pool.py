"""
硅基流动 API 池
支持多 Key 轮询、自动切换、余额不足自动跳过
"""
import json
import random
import urllib.request
import urllib.error
import os
import time

class APIPool:
    """API Key 池管理器"""
    
    def __init__(self, keys_file="valid_api_keys.json"):
        """初始化 API 池"""
        self.base_url = "https://api.siliconflow.cn/v1"
        self.keys = self._load_keys(keys_file)
        self.current_index = 0
        self.failed_keys = set()  # 失败的 key（余额不足等）
        
        print(f"API 池初始化完成，共 {len(self.keys)} 个有效 Key")
    
    def _load_keys(self, keys_file):
        """加载 API Keys"""
        # 尝试多个可能的路径
        paths = [
            keys_file,
            os.path.join(os.path.dirname(__file__), "..", keys_file),
            os.path.join(os.path.dirname(__file__), keys_file),
        ]
        
        for path in paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get('keys', [])
        
        raise FileNotFoundError(f"找不到 API Keys 文件: {keys_file}")
    
    def get_available_key(self):
        """获取一个可用的 Key（轮询方式）"""
        attempts = 0
        while attempts < len(self.keys):
            key = self.keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.keys)
            
            if key not in self.failed_keys:
                return key
            
            attempts += 1
        
        raise Exception("所有 API Key 都已失效！")
    
    def get_random_key(self):
        """随机获取一个可用的 Key"""
        available = [k for k in self.keys if k not in self.failed_keys]
        if not available:
            raise Exception("所有 API Key 都已失效！")
        return random.choice(available)
    
    def mark_failed(self, key, reason="unknown"):
        """标记 Key 为失败"""
        self.failed_keys.add(key)
        print(f"⚠️  Key {key[:20]}... 已标记为失效 ({reason})")
        print(f"   剩余可用 Key: {len(self.keys) - len(self.failed_keys)} 个")
    
    def chat(self, messages, model="Qwen/Qwen2.5-7B-Instruct", max_retries=3):
        """
        调用聊天 API，自动处理 Key 切换
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            max_retries: 最大重试次数
        
        Returns:
            AI 回复文本
        """
        for attempt in range(max_retries):
            key = self.get_available_key()
            
            try:
                result = self._call_api(key, messages, model)
                return result
            except Exception as e:
                error_msg = str(e)
                
                # 检查是否是余额不足
                if "余额" in error_msg or "balance" in error_msg.lower() or "quota" in error_msg.lower():
                    self.mark_failed(key, "余额不足")
                elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    print(f"⚠️  Key {key[:20]}... 请求频率限制，等待后重试")
                    time.sleep(2)
                else:
                    print(f"❌ 请求失败 (尝试 {attempt+1}/{max_retries}): {error_msg[:100]}")
                
                if attempt == max_retries - 1:
                    raise
        
        raise Exception("所有重试都失败了")
    
    def _call_api(self, api_key, messages, model):
        """实际调用 API"""
        url = f"{self.base_url}/chat/completions"
        
        data = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"HTTP {e.code}: {error_body}")
    
    def get_status(self):
        """获取 API 池状态"""
        return {
            "total": len(self.keys),
            "available": len(self.keys) - len(self.failed_keys),
            "failed": len(self.failed_keys)
        }


# 测试
if __name__ == "__main__":
    pool = APIPool()
    
    print("\n测试 API 调用...")
    response = pool.chat([
        {"role": "user", "content": "你好，请用一句话介绍 Dota2"}
    ])
    print(f"\nAI 回复: {response}")
    
    print(f"\nAPI 池状态: {pool.get_status()}")
