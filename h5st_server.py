import json
import threading
from flask import Flask, jsonify, request
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- 全局变量 ---
app = Flask(__name__)
page = None
browser_context = None
# 使用Lock来确保同一时间只有一个线程在操作Playwright页面，防止冲突
playwright_lock = threading.Lock()

# --- 核心函数：初始化浏览器并处理登录 ---
def init_browser():
    global page, browser_context
    p = sync_playwright().start()
    # 首次运行时设置为False方便扫码。成功登录一次后，可以改为True，让浏览器在后台静默运行。
    browser = p.chromium.launch(headless=False) 
    
    try:
        with open("jd_storage_state.json", "r") as f:
            storage_state = json.load(f)
        browser_context = browser.new_context(storage_state=storage_state)
        page = browser_context.new_page()
        print("✅ 成功加载已保存的登录状态，正在验证...")
        page.goto("https://home.jd.com/", timeout=20000)
        page.wait_for_selector('.user_name', timeout=10000)
        print("✅ 登录状态验证成功！服务器已就绪。")
    except Exception as e:
        print(f"未能加载登录状态 ({e})，启动手动登录。")
        browser_context = browser.new_context()
        page = browser_context.new_page()
        print("🚀 请在弹出的浏览器窗口中扫码登录...")
        page.goto("https://passport.jd.com/new/login.aspx")
        page.wait_for_url("https://www.jd.com/**", timeout=120000)
        storage = browser_context.storage_state()
        with open("jd_storage_state.json", "w") as f:
            json.dump(storage, f)
        print("✅ 登录成功！登录状态已保存。服务器已就绪。")

# --- API接口：对外提供h5st签名 ---
@app.route('/get_h5st', methods=['POST'])
def get_h5st():
    if not page:
        return jsonify({"error": "浏览器服务尚未准备就绪"}), 500

    with playwright_lock: # 获取锁，确保操作的原子性
        try:
            final_result = {}
            
            # 定义一个处理函数，用于从拦截到的请求中提取信息
            def handle_request(req):
                nonlocal final_result
                if "api?fid=bindingQualification" in req.url and req.method == 'POST':
                    try:
                        post_data = req.post_data_json
                        final_result = {
                            'h5st': post_data.get('h5st'),
                            't': post_data.get('t'),
                            'body': post_data.get('body')
                        }
                        print(f"✅ 成功捕获到新的h5st: {final_result.get('h5st', '')[:30]}...")
                    except Exception as e:
                        print(f"解析拦截请求失败: {e}")

            # 注册一次性的请求拦截器
            page.on("request", handle_request)
            
            # 导航到活动页面，这会触发页面加载时的各种API请求，包括我们需要的那个
            # wait_until='domcontentloaded' 表示DOM加载完成即可，无需等待所有图片等资源
            page.goto("https://gov-subsidy.jd.com/pages/details/index", wait_until='domcontentloaded', timeout=20000)
            
            # 给页面一些时间来发送异步请求
            page.wait_for_timeout(2000)

            # 移除拦截器，避免影响下一次调用
            page.remove_listener("request", handle_request)

            if final_result and final_result.get('h5st'):
                return jsonify({"success": True, **final_result})
            else:
                # 如果页面加载时没有自动触发，我们可以尝试模拟一次点击
                print("页面加载未捕获到签名，尝试模拟点击...")
                page.on("request", handle_request)
                try:
                    # 点击页面上最可能触发API的元素
                    page.locator('text=立即领取').click(timeout=5000)
                    page.wait_for_timeout(2000)
                except PlaywrightTimeoutError:
                    print("模拟点击超时或未找到元素。")
                
                page.remove_listener("request", handle_request)
                
                if final_result and final_result.get('h5st'):
                    return jsonify({"success": True, **final_result})
                else:
                    return jsonify({"error": "未能捕获到h5st签名，请检查活动页面逻辑。"}), 400

        except Exception as e:
            return jsonify({"error": f"生成h5st时发生异常: {str(e)}"}), 500

# --- 启动入口 ---
if __name__ == '__main__':
    browser_thread = threading.Thread(target=init_browser, daemon=True)
    browser_thread.start()
    app.run(host='0.0.0.0', port=5555)

