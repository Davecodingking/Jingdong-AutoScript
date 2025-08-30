import requests
import time
import json
import threading

# ================= 1. 基本配置 =================

# 目标API的URL
coupon_url = "https://api.m.jd.com/api?fid=bindingQualification"

# 请求头 (Headers) - 注意：Cookie不再需要，因为登录状态由h5st_server.py中的浏览器管理
headers = {
    'authority': 'api.m.jd.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://gov-subsidy.jd.com',
    'referer': 'https://gov-subsidy.jd.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-referer-page': 'https://gov-subsidy.jd.com/pages/details/index',
    'x-rp-client': 'h5_1.0.0',
}

# 基础Payload模板，最关键的h5st, t, body将由服务器动态提供
base_payload = {
    'appid': 'gov-subsidy-h5',
    'channelId': '2025_8_573_ylq',
    'functionId': 'bindingQualification',
    'loginType': 'null',
    'loginWQBiz': '',
}

# ================= 2. 核心函数（已升级为混合模式） =================

def get_latest_h5st_from_server():
    """从本地h5st服务器获取最新的签名"""
    try:
        # 向我们自己搭建的h5st_server发送请求，端口号为5555
        response = requests.post("http://127.0.0.1:5555/get_h5st", timeout=15) # 增加超时以应对浏览器响应慢的情况
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data
    except Exception as e:
        print(f"获取最新h5st失败: {e}")
    return None

def rush_coupon(thread_name):
    """执行抢券请求（动态h5st版）"""
    print(f"线程 {thread_name} 正在向本地服务器请求最新的h5st签名...")
    
    # 1. 获取最新的签名及相关参数
    dynamic_params = get_latest_h5st_from_server()
    
    if not dynamic_params or not dynamic_params.get('h5st'):
        print(f"❌ 线程 {thread_name} 获取h5st失败，取消本次请求。")
        return

    # 2. 动态构建最终的Payload
    final_payload = base_payload.copy()
    final_payload['h5st'] = dynamic_params.get('h5st')
    final_payload['t'] = dynamic_params.get('t')
    # body也使用服务器捕获到的最新版本，以确保一致性
    final_payload['body'] = dynamic_params.get('body') 
    
    # 从h5st_server返回的body中提取x-api-eid-token（如果存在）
    try:
        body_json = json.loads(final_payload['body'])
        if 'eid_token' in body_json:
             final_payload['x-api-eid-token'] = body_json.get('eid_token')
    except:
        pass # 解析失败则忽略

    print(f"线程 {thread_name} 已获取签名，开始尝试抢券...")
    try:
        response = requests.post(coupon_url, headers=headers, data=final_payload, timeout=2)
        
        # 使用我们之前完善的、能分辨失败类型的逻辑
        try:
            result = response.json()
            print(f"线程 {thread_name} 服务器返回: {result}")

            if result.get("success"):
                print(f"🎉🎉🎉 线程 {thread_name} 恭喜！抢券成功！")
                return

            msg = result.get('message') or result.get('originalMsg', '')
            known_business_errors = ["已发完", "火爆", "已领取", "分布式锁", "绑定失败", "未开始", "不符合"]
            is_business_error = any(keyword in msg for keyword in known_business_errors)

            if is_business_error:
                print(f"😥 [业务失败] 线程 {thread_name} 抢券失败: {msg}")
            else:
                print(f"❌ [签名可能无效] 线程 {thread_name} 遭遇未知失败: {msg}")

        except json.JSONDecodeError:
            print(f"❌ [格式错误] 线程 {thread_name} 服务器返回非JSON格式，可能是被安全系统拦截。")
            
    except Exception as e:
        print(f"🚨 [网络异常] 线程 {thread_name} 请求异常: {e}")


# ================= 3. 最终执行入口（定时实战版） =================

if __name__ == '__main__':
    # --- 立即测试（混合模式版） ---
    print("混合模式脚本已启动，立即执行功能性测试...")
    print("请确保 h5st_server.py 正在另一个终端窗口中成功运行。")

    # 为了清晰地看到单次请求的结果，我们先用一个线程测试
    rush_coupon(thread_name="Hybrid-Test-1") 

    print("\n测试执行完毕。")

