#!/usr/bin/env python3
"""AI 情报中心数据校验脚本"""

import json
import re
import os
import sys

def normalize_url(s):
    """标准化 URL"""
    if not s:
        return None
    s = re.sub(r'^https?://', '', s)
    s = s.replace('www.', '')
    s = s.rstrip('/')
    return s

def validate_data(data_file):
    """校验单个 data.json"""
    if not os.path.exists(data_file):
        return []
    
    with open(data_file) as f:
        data = json.load(f)
    
    issues = []
    for c in data.get('competitors', []):
        cid = c.get('id', 'unknown')
        name = c.get('name', 'unknown')
        domain = c.get('domain', '')
        url = c.get('url', '')
        
        # 检查必填字段
        if not domain:
            issues.append(f"[{cid}] {name}: 缺少 domain")
        if not url:
            issues.append(f"[{cid}] {name}: 缺少 url")
        
        # 检查 url 格式
        if url and not url.startswith('http'):
            issues.append(f"[{cid}] {name}: url 必须以 http 开头")
        
        # 检查 domain 格式
        if domain and domain.startswith('http'):
            issues.append(f"[{cid}] {name}: domain 不应包含协议")
        
        # 检查一致性
        domain_norm = normalize_url(domain)
        url_norm = normalize_url(url)
        
        if domain_norm and url_norm:
            if domain_norm != url_norm and not url_norm.startswith(domain_norm):
                issues.append(f"[{cid}] {name}: domain 和 url 不一致")
                issues.append(f"    domain: {domain_norm}")
                issues.append(f"    url:    {url_norm}")
    
    return issues

def main():
    dirs = ['.', 'cn', 'skills', 'news', 'models']
    all_issues = []
    
    for dir_name in dirs:
        data_file = f'{dir_name}/data.json'
        issues = validate_data(data_file)
        if issues:
            print(f"\n❌ {data_file}:")
            for i in issues:
                print(f"  {i}")
            all_issues.extend(issues)
    
    if all_issues:
        print(f"\n总计 {len(all_issues)} 个问题")
        sys.exit(1)
    else:
        print("✅ 所有数据校验通过！")
        sys.exit(0)

if __name__ == '__main__':
    main()
