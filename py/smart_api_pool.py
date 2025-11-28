"""
智能 API 池 - 带权重系统 + 速率限制
特性：
1. 根据余额设置初始权重
2. 请求失败/余额不足自动降权
3. 按权重随机选择（余额多的更容易被选中）
4. 支持持久化权重状态
5. 速率限制控制（防止触发 Rate Limit）
6. 自动限流与重试
"""
import json
import random
import urllib.request
import urllib.error
import os
import time
import threading
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, List
from dataclasses import dataclass, field, asdict
from collections import deque

class RateLimiter:
    """
    速率限制器 - 滑动窗口算法
    控制每个 Key 的请求频率
    """
    def __init__(self, max_requests_per_minute: int = 3, max_requests_per_key_per_minute: int = 2):
        """
        Args:
            max_requests_per_minute: 全局每分钟最大请求数
            max_requests_per_key_per_minute: 每个 Key 每分钟最大请求数
        """
        self.max_rpm = max_requests_per_minute
        self.max_rpm_per_key = max_requests_per_key_per_minute
        self.global_requests = deque()  # 全局请求时间戳
        self.key_requests: Dict[str, deque] = {}  # 每个 key 的请求时间戳
        self.lock = threading.Lock()
    
    def _clean_old_requests(self, request_queue: deque, window_seconds: int = 60):
        """清理超出时间窗口的请求记录"""
        now = time.time()
        while request_queue and now - request_queue[0] > window_seconds:
            request_queue.popleft()
    
    def can_request(self, key: str) -> bool:
        """检查是否可以发起请求"""
        with self.lock:
            now = time.time()
            
            # 清理旧请求
            self._clean_old_requests(self.global_requests)
            
            if key not in self.key_requests:
                self.key_requests[key] = deque()
            self._clean_old_requests(self.key_requests[key])
            
            # 检查全局限制
            if len(self.global_requests) >= self.max_rpm:
                return False
            
            # 检查单个 Key 限制
            if len(self.key_requests[key]) >= self.max_rpm_per_key:
                return False
            
            return True
    
    def record_request(self, key: str):
        """记录一次请求"""
        with self.lock:
            now = time.time()
            self.global_requests.append(now)
            
            if key not in self.key_requests:
                self.key_requests[key] = deque()
            self.key_requests[key].append(now)
    
    def wait_if_needed(self, key: str, timeout: float = 120) -> bool:
        """
        如果需要等待，则等待直到可以请求
        Returns: True 如果可以请求，False 如果超时
        """
        start_time = time.time()
        
        while not self.can_request(key):
            if time.time() - start_time > timeout:
                return False
            
            # 计算需要等待的时间
            wait_time = self._calculate_wait_time(key)
            if wait_time > 0:
                print(f"    ⏳ 速率限制，等待 {wait_time:.1f} 秒...")
                time.sleep(min(wait_time, 5))  # 最多等 5 秒后重新检查
        
        return True
    
    def _calculate_wait_time(self, key: str) -> float:
        """计算需要等待的时间"""
        with self.lock:
            now = time.time()
            wait_times = []
            
            # 全局等待时间
            if self.global_requests and len(self.global_requests) >= self.max_rpm:
                oldest = self.global_requests[0]
                wait_times.append(60 - (now - oldest))
            
            # 单个 Key 等待时间
            if key in self.key_requests and len(self.key_requests[key]) >= self.max_rpm_per_key:
                oldest = self.key_requests[key][0]
                wait_times.append(60 - (now - oldest))
            
            return max(wait_times) if wait_times else 0
    
    def get_status(self) -> dict:
        """获取速率限制状态"""
        with self.lock:
            self._clean_old_requests(self.global_requests)
            return {
                "global_requests_in_window": len(self.global_requests),
                "max_rpm": self.max_rpm,
                "keys_with_requests": len([k for k, v in self.key_requests.items() if len(v) > 0])
            }


@dataclass
class APIKeyInfo:
    """API Key 信息"""
    key: str
    weight: float = 100.0  # 初始权重 100
    balance: Optional[float] = None  # 余额
    total_balance: Optional[float] = None  # 总额度
    success_count: int = 0  # 成功次数
    fail_count: int = 0  # 失败次数
    last_used: Optional[str] = None  # 最后使用时间
    status: str = "unknown"  # unknown/normal/low/critical/dead
    
    def to_dict(self):
        return asdict(self)


class SmartAPIPool:
    """智能 API 池管理器"""
    
    # 余额阈值
    BALANCE_NORMAL = 5.0    # >= 5 正常
    BALANCE_LOW = 0.5       # >= 0.5 低余额
    BALANCE_CRITICAL = 0.1  # >= 0.1 严重
    
    # 权重配置
    WEIGHT_NORMAL = 100     # 正常状态权重
    WEIGHT_LOW = 30         # 低余额权重
    WEIGHT_CRITICAL = 5     # 严重状态权重
    WEIGHT_DEAD = 0         # 死亡（不再使用）
    WEIGHT_FAIL_PENALTY = 20  # 每次失败降低的权重
    
    def __init__(self, keys_file="valid_api_keys.json", state_file="api_pool_state.json",
                 max_rpm: int = 60, max_rpm_per_key: int = 3):
        """
        初始化 API 池
        
        Args:
            keys_file: API Keys 文件
            state_file: 状态持久化文件
            max_rpm: 全局每分钟最大请求数（所有 Key 合计）
            max_rpm_per_key: 每个 Key 每分钟最大请求数
        """
        self.base_url = "https://api.siliconflow.cn/v1"
        self.state_file = state_file
        
        # 速率限制器
        self.rate_limiter = RateLimiter(
            max_requests_per_minute=max_rpm,
            max_requests_per_key_per_minute=max_rpm_per_key
        )
        
        # 加载 keys
        raw_keys = self._load_keys(keys_file)
        
        # 加载或初始化状态
        self.keys_info: Dict[str, APIKeyInfo] = {}
        self._load_state(raw_keys)
        
        # 顺序模式：按顺序使用 Key（第一个 Key 优先，用完/失效再换下一个）
        self.key_order = list(self.keys_info.keys())
        self.current_key_index = 0  # 从第一个开始（已验证可用）
        
        print(f"智能 API 池初始化完成")
        print(f"  速率限制: 全局 {max_rpm} 次/分钟, 单 Key {max_rpm_per_key} 次/分钟")
        self._print_status()
    
    def _load_keys(self, keys_file) -> List[str]:
        """加载 API Keys"""
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
    
    def _load_state(self, raw_keys: List[str]):
        """加载状态文件或初始化"""
        state_path = os.path.join(os.path.dirname(__file__), "..", self.state_file)
        
        if os.path.exists(state_path):
            print(f"加载已有状态: {self.state_file}")
            with open(state_path, 'r') as f:
                saved_state = json.load(f)
                for key_data in saved_state.get('keys', []):
                    key = key_data['key']
                    self.keys_info[key] = APIKeyInfo(**key_data)
        
        # 添加新的 keys
        for key in raw_keys:
            if key not in self.keys_info:
                self.keys_info[key] = APIKeyInfo(key=key)
    
    def save_state(self):
        """保存状态到文件"""
        state_path = os.path.join(os.path.dirname(__file__), "..", self.state_file)
        state = {
            "updated_at": datetime.now().isoformat(),
            "keys": [info.to_dict() for info in self.keys_info.values()]
        }
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def check_balance(self, key: str) -> Optional[float]:
        """检查单个 Key 的余额"""
        req = urllib.request.Request(
            f"{self.base_url}/user/info",
            headers={"Authorization": f"Bearer {key}"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('data'):
                    balance = data['data'].get('balance')
                    total = data['data'].get('totalBalance') or data['data'].get('total_balance')
                    return float(balance) if balance else None
        except:
            pass
        return None
    
    def refresh_all_balances(self, concurrency=10):
        """刷新所有 Key 的余额（多线程）"""
        import concurrent.futures
        
        print(f"\n刷新所有 Key 的余额...")
        
        def check_one(key: str) -> tuple:
            balance = self.check_balance(key)
            return key, balance
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(check_one, key): key for key in self.keys_info.keys()}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                key, balance = future.result()
                info = self.keys_info[key]
                
                if balance is not None:
                    info.balance = balance
                    # 根据余额设置状态和权重
                    if balance >= self.BALANCE_NORMAL:
                        info.status = "normal"
                        info.weight = self.WEIGHT_NORMAL
                    elif balance >= self.BALANCE_LOW:
                        info.status = "low"
                        info.weight = self.WEIGHT_LOW
                    elif balance >= self.BALANCE_CRITICAL:
                        info.status = "critical"
                        info.weight = self.WEIGHT_CRITICAL
                    else:
                        info.status = "dead"
                        info.weight = self.WEIGHT_DEAD
                else:
                    info.status = "unknown"
                    info.weight = self.WEIGHT_LOW  # 未知状态给低权重
                
                balance_str = f"{balance:.4f}" if balance else "N/A"
                print(f"  [{i+1}/{len(self.keys_info)}] {key[:20]}... 余额: {balance_str} 状态: {info.status}")
        
        self.save_state()
        self._print_status()
    
    def get_weighted_key(self) -> str:
        """按权重随机选择一个 Key（保留兼容）"""
        # 过滤掉权重为 0 的 key
        available = [(key, info) for key, info in self.keys_info.items() if info.weight > 0]
        
        if not available:
            raise Exception("所有 API Key 都已失效！")
        
        # 按权重随机选择
        total_weight = sum(info.weight for _, info in available)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for key, info in available:
            cumulative += info.weight
            if r <= cumulative:
                return key
        
        return available[-1][0]  # 兜底
    
    def get_sequential_key(self) -> str:
        """
        顺序模式：一个 Key 用到失效再换下一个
        - 优先使用当前 Key
        - 如果当前 Key 失效(dead)，自动切换到下一个
        - unknown 状态的 Key 也可以使用
        """
        total = len(self.key_order)
        tried = 0
        
        while tried < total:
            key = self.key_order[self.current_key_index]
            info = self.keys_info.get(key)
            
            # 检查 Key 是否可用（只有 dead 状态不可用）
            if info and info.status != "dead":
                return key
            
            # 当前 Key 不可用，切换到下一个
            print(f"  🔄 Key #{self.current_key_index + 1} 已失效，切换到下一个...")
            self.current_key_index = (self.current_key_index + 1) % total
            tried += 1
        
        raise Exception("所有 API Key 都已失效！")
    
    def switch_to_next_key(self):
        """手动切换到下一个 Key"""
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.key_order)
        print(f"  🔄 从 Key #{old_index + 1} 切换到 Key #{self.current_key_index + 1}")
    
    def report_success(self, key: str):
        """报告请求成功"""
        if key in self.keys_info:
            info = self.keys_info[key]
            info.success_count += 1
            info.last_used = datetime.now().isoformat()
    
    def report_failure(self, key: str, reason: str = "unknown"):
        """报告请求失败，降低权重"""
        if key in self.keys_info:
            info = self.keys_info[key]
            info.fail_count += 1
            info.last_used = datetime.now().isoformat()
            
            # 根据失败原因调整权重
            if "余额" in reason or "balance" in reason.lower() or "quota" in reason.lower():
                # 余额不足，直接设为 dead
                info.status = "dead"
                info.weight = self.WEIGHT_DEAD
                print(f"⚠️  Key {key[:20]}... 余额不足，已禁用")
            else:
                # 其他失败，降低权重
                info.weight = max(0, info.weight - self.WEIGHT_FAIL_PENALTY)
                if info.weight == 0:
                    info.status = "dead"
                print(f"⚠️  Key {key[:20]}... 权重降低至 {info.weight}")
            
            self.save_state()
    
    def chat(self, messages, model="deepseek-ai/DeepSeek-V3", max_retries=10, wait_for_rate_limit=True):
        """
        调用聊天 API，自动选择 Key 并处理失败
        专为无人值守长时间运行设计
        
        Args:
            messages: 对话消息
            model: 模型名称（默认 DeepSeek-V3，效果好且便宜）
            max_retries: 最大重试次数
            wait_for_rate_limit: 是否等待速率限制
        """
        last_error = None
        consecutive_failures = 0
        
        for attempt in range(max_retries):
            key = self.get_sequential_key()  # 使用顺序模式
            
            # 速率限制检查
            if wait_for_rate_limit:
                if not self.rate_limiter.wait_if_needed(key, timeout=300):  # 增加到 5 分钟
                    print(f"  ⚠️ 速率限制等待超时，尝试其他 Key")
                    continue
            elif not self.rate_limiter.can_request(key):
                found_key = self._find_available_key()
                if found_key:
                    key = found_key
                else:
                    # 所有 key 都在限流，等待后重试
                    wait_time = 30 + (consecutive_failures * 10)  # 递增等待
                    print(f"  ⏳ 所有 Key 限流中，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
            
            try:
                # 记录请求
                self.rate_limiter.record_request(key)
                
                result = self._call_api(key, messages, model)
                self.report_success(key)
                consecutive_failures = 0  # 重置失败计数
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                consecutive_failures += 1
                
                # 根据错误类型处理
                if "50603" in str(e) or "busy" in error_msg or "System is really busy" in str(e):
                    # 服务器繁忙 - 短暂等待后换 Key 重试
                    print(f"  ⚠️ 服务器繁忙 (尝试 {attempt+1}/{max_retries})，等待 3 秒后换 Key...")
                    time.sleep(3)
                    self.switch_to_next_key()  # 换下一个 Key
                    consecutive_failures = 0  # 换 Key 后重置
                    
                elif "429" in str(e) or "rate" in error_msg or "limit" in error_msg:
                    # 速率限制 - 等待后重试，不降权
                    wait_time = 30 * (2 ** min(consecutive_failures - 1, 4))  # 指数退避，最大 480 秒
                    print(f"  ⚠️ 速率限制 (尝试 {attempt+1}/{max_retries})，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    
                elif "timeout" in error_msg or "timed out" in error_msg:
                    # 超时 - 短暂等待后重试
                    print(f"  ⚠️ 请求超时 (尝试 {attempt+1}/{max_retries})，等待 10 秒...")
                    time.sleep(10)
                    
                elif "502" in str(e) or "503" in str(e) or "504" in str(e) or "server" in error_msg:
                    # 服务器错误 - 等待后重试
                    wait_time = 60 * min(consecutive_failures, 5)
                    print(f"  ⚠️ 服务器错误 (尝试 {attempt+1}/{max_retries})，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    
                elif "余额" in str(e) or "balance" in error_msg or "quota" in error_msg or "insufficient" in error_msg:
                    # 余额不足 - 禁用该 Key
                    self.report_failure(key, "余额不足")
                    consecutive_failures = 0  # 换 key 后重置
                    
                elif "401" in str(e) or "unauthorized" in error_msg or "invalid" in error_msg:
                    # Key 无效 - 禁用该 Key
                    self.report_failure(key, "Key 无效")
                    consecutive_failures = 0
                    
                else:
                    # 其他错误
                    print(f"  ❌ 未知错误 (尝试 {attempt+1}/{max_retries}): {str(e)[:100]}")
                    self.report_failure(key, error_msg[:50])
                    time.sleep(5)
        
        # 所有重试都失败，最后等待一段时间后抛出异常
        print(f"  💤 所有重试失败，等待 5 分钟后可以继续...")
        time.sleep(300)
        raise Exception(f"所有重试都失败: {last_error}")
    
    def chat_safe(self, messages, model="deepseek-ai/DeepSeek-V3", max_global_retries=100) -> Optional[str]:
        """
        安全的聊天接口 - 永远不抛出异常，适合无人值守运行
        如果失败会一直重试，直到成功或达到最大重试次数
        
        Args:
            messages: 对话消息
            model: 模型名称
            max_global_retries: 全局最大重试次数（每次重试包含内部 10 次尝试）
        
        Returns:
            成功返回 AI 回复，失败返回 None
        """
        for global_attempt in range(max_global_retries):
            try:
                return self.chat(messages, model=model)
            except Exception as e:
                print(f"\n🔄 全局重试 {global_attempt + 1}/{max_global_retries}")
                print(f"   错误: {str(e)[:100]}")
                
                # 检查是否还有可用的 Key
                status = self.get_status()
                if status['available'] == 0:
                    print("❌ 所有 API Key 都已失效，无法继续")
                    return None
                
                # 继续重试
                print(f"   可用 Key: {status['available']} 个，继续尝试...")
                time.sleep(60)  # 等待 1 分钟后重试
        
        print(f"❌ 达到最大全局重试次数 ({max_global_retries})，放弃")
        return None
    
    def _find_available_key(self) -> Optional[str]:
        """找一个当前可以请求的 Key"""
        available = [(key, info) for key, info in self.keys_info.items() 
                     if info.weight > 0 and self.rate_limiter.can_request(key)]
        
        if not available:
            return None
        
        # 按权重随机选择
        total_weight = sum(info.weight for _, info in available)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for key, info in available:
            cumulative += info.weight
            if r <= cumulative:
                return key
        
        return available[-1][0]
    
    def _call_api(self, api_key: str, messages: list, model: str) -> str:
        """实际调用 API"""
        url = f"{self.base_url}/chat/completions"
        
        data = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 8192
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
    
    def _print_status(self):
        """打印当前状态"""
        status_count = {"normal": 0, "low": 0, "critical": 0, "dead": 0, "unknown": 0}
        total_balance = 0
        
        for info in self.keys_info.values():
            status_count[info.status] = status_count.get(info.status, 0) + 1
            if info.balance:
                total_balance += info.balance
        
        print(f"\n📊 API 池状态:")
        print(f"   总数: {len(self.keys_info)} 个")
        print(f"   正常: {status_count['normal']} | 低余额: {status_count['low']} | 严重: {status_count['critical']} | 失效: {status_count['dead']} | 未知: {status_count['unknown']}")
        print(f"   总余额: {total_balance:.4f}")
    
    def get_status(self) -> dict:
        """获取状态摘要"""
        status_count = {"normal": 0, "low": 0, "critical": 0, "dead": 0, "unknown": 0}
        total_balance = 0
        
        for info in self.keys_info.values():
            status_count[info.status] = status_count.get(info.status, 0) + 1
            if info.balance:
                total_balance += info.balance
        
        # available = 所有非 dead 的 Key
        available = status_count['normal'] + status_count['low'] + status_count['critical'] + status_count['unknown']
        
        return {
            "total": len(self.keys_info),
            "available": available,
            "status": status_count,
            "total_balance": total_balance,
            "rate_limit": self.rate_limiter.get_status()
        }


# 测试
if __name__ == "__main__":
    import sys
    
    # 支持命令行参数
    refresh = "--refresh" in sys.argv or "-r" in sys.argv
    
    # 初始化 API 池
    # 速率限制：全局 200 次/分钟（因为有 100 个 key），单 Key 3 次/分钟
    pool = SmartAPIPool(max_rpm=200, max_rpm_per_key=3)
    
    # 刷新余额
    if refresh:
        pool.refresh_all_balances()
    else:
        user_input = input("\n是否刷新所有 Key 的余额？(y/n): ")
        if user_input.lower() == 'y':
            pool.refresh_all_balances()
    
    # 测试 API 调用
    print("\n测试 API 调用 (使用 DeepSeek-V3)...")
    response = pool.chat_safe([
        {"role": "user", "content": "你好，请用一句话介绍 Dota2"}
    ], model="deepseek-ai/DeepSeek-V3")
    
    if response:
        print(f"\n✅ AI 回复: {response}")
    else:
        print(f"\n❌ 调用失败")
    
    print(f"\n最终状态: {pool.get_status()}")
