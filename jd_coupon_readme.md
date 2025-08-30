# 🎫 京东抢券脚本（基于 h5st 生成器）

本项目实现了一个自动化的京东抢券流程。  
它通过 **Playwright** 启动一个无头浏览器，生成最新合法的 `h5st` 值，并通过 **Flask** 提供本地 API 服务。  
主脚本 `main.py` 在请求发起前，会向 `h5st_server.py` 请求新的 `h5st`，确保抢券请求始终有效。  

---

## 📑 目录
- [🚀 功能说明](#-功能说明)
- [📦 安装依赖](#-安装依赖)
- [🖥️ 使用步骤](#️-使用步骤)
- [🛠️ 依赖说明](#️-依赖说明)
- [⚠️ 注意事项](#️-注意事项)
- [✨ 示例效果](#-示例效果)
- [📁 项目结构（示例）](#-项目结构示例)
- [📄 可选：requirements.txt](#-可选requirementstxt)

---

## 🚀 功能说明
- **`h5st_server.py`**  
  后台服务，负责启动浏览器、登录京东并生成 `h5st`。  
- **`main.py`**  
  抢券主脚本，在发送请求前调用本地 API 获取最新 `h5st`。  

---

## 📦 安装依赖

请确保已安装 **Python 3.8+**。

```bash
# 安装必要依赖
pip install playwright flask

# 安装 Playwright 所需浏览器
python -m playwright install
```

---

## 🖥️ 使用步骤

1. **保存脚本**
   - 将仓库中的 `h5st_server.py` 和 `main.py` 放在同一个文件夹下。

2. **启动 h5st 服务器**
   - 打开第一个命令行终端，进入脚本所在目录，运行：
     ```bash
     python h5st_server.py
     ```
   - 第一次运行会弹出浏览器，请扫码登录京东账号。  
   - 登录成功后，终端显示 **“服务器已就绪”**。  
   - ⚠️ 请不要关闭该窗口，让它保持后台运行。

3. **运行抢券脚本**
   - 打开第二个命令行终端，进入同一目录。  
   - 修改 `main.py` 中的 `target_time_tuple` 为你需要的抢券时间。  
   - 在抢券前执行：
     ```bash
     python main.py
     ```

---

## 🛠️ 依赖说明
- [Playwright](https://playwright.dev/)  
  现代化浏览器自动化工具，比 Selenium 更快更稳定。  
- [Flask](https://flask.palletsprojects.com/)  
  轻量级 Web 框架，用于提供本地 API。  

---

## ⚠️ 注意事项
- 请提前扫码并保持 `h5st_server.py` 运行，不要关闭窗口。  
- 抢券时间请提前 **1–2 分钟** 启动 `main.py`，避免延迟。  
- 本项目仅供学习交流，**切勿用于商业用途**。  

---

## ✨ 示例效果
```bash
服务器已就绪
正在获取最新 h5st...
已生成新的 h5st: xxxxxxxxxxxxxx
抢券请求已发送！
```

---

## 📁 项目结构（示例）
```text
.
├─ h5st_server.py
├─ main.py
├─ requirements.txt   # 可选
└─ README.md
```

---

## 📄 可选：requirements.txt
如果想一键安装依赖，可以在仓库根目录新建 `requirements.txt`：
```txt
flask
playwright
```
然后执行：
```bash
pip install -r requirements.txt
python -m playwright install
```

