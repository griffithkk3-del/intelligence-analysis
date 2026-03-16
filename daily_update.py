#!/usr/bin/env python3
"""
AI 情报中心每日自动更新脚本
- 检查网站可用性
- 更新 lastUpdated 时间戳
- 推送到 GitHub
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

SITE_DIR = Path(__file__).parent

def update_timestamps():
    """更新所有 data.json 的时间戳"""
    now = datetime.now().astimezone().isoformat()
    
    for json_file in SITE_DIR.glob("**/data.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['lastUpdated'] = now
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 更新: {json_file.relative_to(SITE_DIR)}")
        except Exception as e:
            print(f"❌ 失败: {json_file} - {e}")

def git_push():
    """提交并推送到 GitHub"""
    os.chdir(SITE_DIR)
    
    # 检查是否有变更
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if not result.stdout.strip():
        print("📝 无变更，跳过推送")
        return False
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', f'chore: 每日自动更新 {date_str}'], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("🚀 已推送到 GitHub")
    return True

def main():
    print(f"🕐 开始每日更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)
    
    update_timestamps()
    git_push()
    
    print("-" * 40)
    print("✅ 每日更新完成")

if __name__ == "__main__":
    main()
