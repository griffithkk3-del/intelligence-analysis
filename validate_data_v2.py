#!/usr/bin/env python3
"""
数据真实性验证脚本
- 检查所有数据是否有来源标注
- 验证数据的合理性
- 检测可能的模拟数据
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

def validate_data_authenticity(data_file: Path) -> List[str]:
    """验证数据真实性"""
    if not data_file.exists():
        return [f"❌ 文件不存在: {data_file}"]
    
    with open(data_file) as f:
        data = json.load(f)
    
    issues = []
    competitors = data.get('competitors', [])
    
    for comp in competitors:
        comp_id = comp.get('id', 'unknown')
        name = comp.get('name', 'unknown')
        
        # 检查 1: 有流量数据但缺少数据来源
        if comp.get('monthlyVisits') and not comp.get('dataSource'):
            issues.append(
                f"❌ [{comp_id}] {name}: 有流量数据但缺少 dataSource 字段"
            )
        
        # 检查 2: 有数据来源但缺少获取时间
        if comp.get('dataSource') and not comp.get('dataFetchedAt'):
            issues.append(
                f"⚠️  [{comp_id}] {name}: 有数据来源但缺少 dataFetchedAt 字段"
            )
        
        # 检查 3: 数据是否过期（超过 30 天）
        if comp.get('dataFetchedAt'):
            try:
                fetched_at = datetime.fromisoformat(comp['dataFetchedAt'].replace('Z', '+00:00'))
                age = datetime.now().astimezone() - fetched_at
                if age.days > 30:
                    issues.append(
                        f"⚠️  [{comp_id}] {name}: 数据已过期 {age.days} 天"
                    )
            except (ValueError, AttributeError):
                issues.append(
                    f"❌ [{comp_id}] {name}: dataFetchedAt 格式错误"
                )
        
        # 检查 4: 流量数据合理性
        visits = comp.get('monthlyVisits')
        if visits:
            if visits < 0:
                issues.append(
                    f"❌ [{comp_id}] {name}: 月访问量不能为负数"
                )
            elif visits < 100:
                issues.append(
                    f"⚠️  [{comp_id}] {name}: 月访问量过低 ({visits})，可能不准确"
                )
            elif visits > 1_000_000_000:
                issues.append(
                    f"⚠️  [{comp_id}] {name}: 月访问量过高 ({visits:,})，请验证"
                )
        
        # 检查 5: 全球排名合理性
        rank = comp.get('globalRank')
        if rank:
            if rank < 1:
                issues.append(
                    f"❌ [{comp_id}] {name}: 全球排名不能小于 1"
                )
            elif rank > 100_000_000:
                issues.append(
                    f"⚠️  [{comp_id}] {name}: 全球排名过低 ({rank:,})，可能不准确"
                )
        
        # 检查 6: trafficTrend 如果有数据，必须有来源
        trend = comp.get('trafficTrend', [])
        if len(trend) > 0 and not comp.get('trendDataSource'):
            issues.append(
                f"❌ [{comp_id}] {name}: 有趋势数据但缺少 trendDataSource 字段"
            )
        
        # 检查 7: GitHub 数据验证
        if comp.get('githubStars'):
            if not comp.get('github'):
                issues.append(
                    f"⚠️  [{comp_id}] {name}: 有 GitHub Stars 但缺少 github URL"
                )
            if comp['githubStars'] < 0:
                issues.append(
                    f"❌ [{comp_id}] {name}: GitHub Stars 不能为负数"
                )
        
        # 检查 8: 数据来源 URL 验证
        if comp.get('dataSourceUrl'):
            url = comp['dataSourceUrl']
            if not url.startswith('http'):
                issues.append(
                    f"❌ [{comp_id}] {name}: dataSourceUrl 必须以 http 开头"
                )
    
    return issues

def validate_domain_url_consistency(data_file: Path) -> List[str]:
    """验证 domain 和 url 的一致性"""
    if not data_file.exists():
        return []
    
    with open(data_file) as f:
        data = json.load(f)
    
    issues = []
    
    for comp in data.get('competitors', []):
        comp_id = comp.get('id', 'unknown')
        name = comp.get('name', 'unknown')
        domain = comp.get('domain', '')
        url = comp.get('url', '')
        
        # 检查必填字段
        if not domain:
            issues.append(f"❌ [{comp_id}] {name}: 缺少 domain")
        if not url:
            issues.append(f"❌ [{comp_id}] {name}: 缺少 url")
        
        # 检查格式
        if url and not url.startswith('http'):
            issues.append(f"❌ [{comp_id}] {name}: url 必须以 http 开头")
        
        if domain and domain.startswith('http'):
            issues.append(f"❌ [{comp_id}] {name}: domain 不应包含协议")
        
        # 检查一致性
        if domain and url:
            domain_clean = domain.replace('www.', '').rstrip('/')
            url_clean = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            if domain_clean != url_clean and not url_clean.startswith(domain_clean):
                issues.append(f"⚠️  [{comp_id}] {name}: domain 和 url 不一致")
                issues.append(f"    domain: {domain_clean}")
                issues.append(f"    url:    {url_clean}")
    
    return issues

def generate_report(all_issues: Dict[str, List[str]]) -> None:
    """生成验证报告"""
    print("\n" + "=" * 70)
    print("📊 数据真实性验证报告")
    print("=" * 70)
    
    total_issues = 0
    critical_issues = 0
    warnings = 0
    
    for file_name, issues in all_issues.items():
        if not issues:
            print(f"\n✅ {file_name}: 通过验证")
            continue
        
        print(f"\n📁 {file_name}:")
        for issue in issues:
            print(f"  {issue}")
            total_issues += 1
            if issue.startswith('❌'):
                critical_issues += 1
            elif issue.startswith('⚠️'):
                warnings += 1
    
    print("\n" + "=" * 70)
    print(f"📈 统计:")
    print(f"  总问题数: {total_issues}")
    print(f"  严重问题: {critical_issues}")
    print(f"  警告: {warnings}")
    print("=" * 70)
    
    if critical_issues > 0:
        print("\n❌ 验证失败：存在严重问题")
        return False
    elif warnings > 0:
        print("\n⚠️  验证通过：但有警告")
        return True
    else:
        print("\n✅ 验证通过：所有数据符合规范")
        return True

def main():
    """主函数"""
    base_dir = Path(__file__).parent
    
    # 要验证的文件
    data_files = {
        'global': base_dir / 'data.json',
        'cn': base_dir / 'cn' / 'data.json',
        'skills': base_dir / 'skills' / 'data.json',
        'news': base_dir / 'news' / 'data.json',
        'models': base_dir / 'models' / 'data.json',
    }
    
    all_issues = {}
    
    for name, file_path in data_files.items():
        if not file_path.exists():
            all_issues[name] = [f"⚠️  文件不存在: {file_path}"]
            continue
        
        # 验证数据真实性
        authenticity_issues = validate_data_authenticity(file_path)
        
        # 验证 domain/url 一致性
        consistency_issues = validate_domain_url_consistency(file_path)
        
        all_issues[name] = authenticity_issues + consistency_issues
    
    # 生成报告
    success = generate_report(all_issues)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
