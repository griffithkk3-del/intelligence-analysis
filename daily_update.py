#!/usr/bin/env python3
"""
AI 聚合网站情报中心 - 每日自动更新脚本
功能：
1. 从 GitHub 获取最新 AI 目录列表
2. 通过搜索获取流量数据
3. 更新 data.json
4. 推送到 GitHub
"""

import json
import os
import subprocess
import urllib.request
import ssl
from datetime import datetime
from pathlib import Path

# 配置
SITE_DIR = Path(__file__).parent
DATA_FILE = SITE_DIR / "data.json"
SERPER_API_KEY = "374959ea28cae888d8049ea2e34d8acc156c602b"

# SSL 配置
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"competitors": [], "insights": []}

def save_data(data):
    data["lastUpdated"] = datetime.now().astimezone().isoformat()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"数据已保存，共 {len(data['competitors'])} 个网站")

def search_traffic(domain):
    """通过 Serper 搜索获取流量数据"""
    try:
        url = "https://google.serper.dev/search"
        query = f"{domain} similarweb monthly visits traffic 2026"
        payload = json.dumps({"q": query, "num": 5}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as resp:
            result = json.loads(resp.read())
            # 从搜索结果中提取流量信息
            for item in result.get('organic', []):
                snippet = item.get('snippet', '').lower()
                # 尝试提取数字
                if 'visit' in snippet or 'traffic' in snippet:
                    return snippet[:200]
        return None
    except Exception as e:
        return None

def check_site_status(url):
    """检查网站是否可用"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as resp:
            return resp.status == 200
    except:
        return False

def fetch_github_directories():
    """从 GitHub 获取 AI 目录列表"""
    try:
        url = "https://raw.githubusercontent.com/best-of-ai/ai-directories/main/README.md"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15, context=ssl_context) as resp:
            content = resp.read().decode('utf-8')
            # 提取域名
            import re
            domains = re.findall(r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
            # 过滤掉 github.com
            domains = [d for d in domains if 'github.com' not in d]
            return list(set(domains))
    except Exception as e:
        log(f"获取 GitHub 列表失败: {e}")
        return []

def update_competitor_data(data):
    """更新竞品数据"""
    log("开始更新竞品数据...")
    
    # 获取 GitHub 上的新目录
    github_domains = fetch_github_directories()
    log(f"从 GitHub 获取到 {len(github_domains)} 个域名")
    
    # 检查现有竞品的网站状态
    for comp in data['competitors'][:10]:  # 每次检查前 10 个
        domain = comp.get('domain', '')
        if domain:
            url = f"https://{domain}"
            status = check_site_status(url)
            comp['status'] = 'active' if status else 'down'
            log(f"  {domain}: {'✓' if status else '✗'}")
    
    return data

def git_push():
    """推送到 GitHub"""
    try:
        os.chdir(SITE_DIR)
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'auto: daily update {datetime.now().strftime("%Y-%m-%d")}'], 
                      check=True, capture_output=True)
        result = subprocess.run(['git', 'push'], check=True, capture_output=True, text=True)
        log("已推送到 GitHub")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Git 推送失败: {e}")
        return False

def main():
    log("=" * 50)
    log("AI 聚合网站情报中心 - 每日更新")
    log("=" * 50)
    
    # 加载数据
    data = load_data()
    log(f"当前数据: {len(data.get('competitors', []))} 个网站")
    
    # 更新数据
    data = update_competitor_data(data)
    
    # 保存数据
    save_data(data)
    
    # 推送到 GitHub
    git_push()
    
    log("=" * 50)
    log("更新完成！")
    log("=" * 50)
    
    return {
        "success": True,
        "sites_count": len(data.get('competitors', [])),
        "updated_at": data.get('lastUpdated')
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
