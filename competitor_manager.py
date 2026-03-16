#!/usr/bin/env python3
"""
竞品分析数据管理工具
用法:
  python3 competitor_manager.py list                    # 列出所有竞品
  python3 competitor_manager.py add <name> <type> <url> # 添加竞品
  python3 competitor_manager.py update <id> <field> <value>  # 更新字段
  python3 competitor_manager.py insight add <title> <content> <color>  # 添加洞察
  python3 competitor_manager.py export                  # 导出数据
"""

import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"lastUpdated": "", "competitors": [], "insights": []}

def save_data(data):
    data["lastUpdated"] = datetime.now().astimezone().isoformat()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存，更新时间: {data['lastUpdated']}")

def list_competitors(data):
    print("\n📋 竞品列表:")
    print("-" * 60)
    for i, c in enumerate(data["competitors"], 1):
        print(f"{i}. {c['name']} ({c['id']})")
        print(f"   类型: {c['type']} | Stars: {c.get('githubStars', '-')} | 月访问: {c.get('monthlyVisits', '-')}")
    print("-" * 60)
    print(f"共 {len(data['competitors'])} 个竞品\n")

def add_competitor(data, name, comp_type, url):
    comp_id = name.lower().replace(' ', '-').replace('.', '-')
    new_comp = {
        "id": comp_id,
        "name": name,
        "type": comp_type,
        "url": url,
        "github": None,
        "githubStars": None,
        "githubForks": None,
        "monthlyVisits": None,
        "totalVisits3m": None,
        "globalRank": None,
        "countryRank": None,
        "avgDuration": None,
        "bounceRate": None,
        "pagesPerVisit": None,
        "desktopPercent": None,
        "mobilePercent": None,
        "mainCountry": None,
        "cdn": None,
        "launchDate": None,
        "color": "blue",
        "badge": None
    }
    data["competitors"].append(new_comp)
    save_data(data)
    print(f"✅ 已添加竞品: {name} (ID: {comp_id})")

def update_competitor(data, comp_id, field, value):
    for c in data["competitors"]:
        if c["id"] == comp_id or c["name"] == comp_id:
            # 自动转换数值类型
            if field in ["githubStars", "githubForks", "monthlyVisits", "totalVisits3m", "globalRank", "countryRank"]:
                value = int(value) if value and value != "null" else None
            elif field in ["bounceRate", "pagesPerVisit", "desktopPercent", "mobilePercent"]:
                value = float(value) if value and value != "null" else None
            elif value == "null":
                value = None
            
            c[field] = value
            save_data(data)
            print(f"✅ 已更新 {c['name']} 的 {field} = {value}")
            return
    print(f"❌ 未找到竞品: {comp_id}")

def add_insight(data, title, content, color="blue"):
    data["insights"].append({
        "title": title,
        "content": content,
        "color": color
    })
    save_data(data)
    print(f"✅ 已添加洞察: {title}")

def export_data(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    data = load_data()
    
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_competitors(data)
    elif cmd == "add" and len(sys.argv) >= 5:
        add_competitor(data, sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "update" and len(sys.argv) >= 5:
        update_competitor(data, sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "insight" and sys.argv[2] == "add" and len(sys.argv) >= 6:
        add_insight(data, sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "blue")
    elif cmd == "export":
        export_data(data)
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
