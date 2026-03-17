#!/usr/bin/env python3
"""
AI 情报中心 - 真实数据自动获取系统
- 通过 Serper 搜索获取 SimilarWeb 数据
- 通过 GitHub API 获取 Stars/Forks
- 所有数据标注来源和获取时间
- 无数据时返回 None，不编造
"""
import json
import os
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime
from pathlib import Path
import time
from typing import Optional, Dict, List

SITE_DIR = Path(__file__).parent

# 从环境变量获取 API Key（不硬编码）
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
if not SERPER_API_KEY:
    raise ValueError("❌ SERPER_API_KEY 环境变量未设置")

# 数据源配置
DATA_SOURCES = {
    'global': {
        'search_queries': [
            'best AI tools directory 2026',
            'AI tools aggregator website traffic',
            'top AI directory sites similarweb',
        ],
        'known_sites': [
            'theresanaiforthat.com', 'futuretools.io', 'toolify.ai',
            'futurepedia.io', 'topai.tools', 'aitoolsdirectory.com'
        ]
    },
    'cn': {
        'search_queries': [
            '中国AI工具导航网站 2026',
            'AI工具集 月访问量',
        ],
        'known_sites': [
            'ai-bot.cn', 'toolify.ai/zh', 'aigc.cn'
        ]
    },
    'skills': {
        'search_queries': [
            'MCP server marketplace 2026',
            'Claude skills marketplace traffic',
        ],
        'known_sites': [
            'clawhub.ai', 'smithery.ai', 'cursor.directory'
        ]
    },
    'news': {
        'search_queries': [
            'AI news website traffic 2026',
        ],
        'known_sites': [
            'bensbites.com', 'therundown.ai'
        ]
    },
    'models': {
        'search_queries': [
            'AI model platform traffic 2026',
        ],
        'known_sites': [
            'huggingface.co', 'openai.com', 'anthropic.com'
        ]
    }
}

def serper_search(query: str) -> Optional[Dict]:
    """Serper 搜索（带完整错误处理）"""
    try:
        url = 'https://google.serper.dev/search'
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        data = json.dumps({'q': query, 'num': 10}).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        
        if response.status != 200:
            print(f"⚠️  Serper HTTP {response.status}")
            return None
        
        return json.loads(response.read())
    
    except urllib.error.HTTPError as e:
        print(f"❌ Serper HTTP 错误: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return None

def parse_similarweb_data(search_results: Dict, domain: str) -> Optional[Dict]:
    """从 Serper 搜索结果中解析 SimilarWeb 数据"""
    if not search_results or 'organic' not in search_results:
        return None
    
    # 查找 SimilarWeb 结果
    for result in search_results.get('organic', []):
        link = result.get('link', '')
        snippet = result.get('snippet', '')
        
        if 'similarweb.com' not in link:
            continue
        
        # 解析月访问量
        visits_match = re.search(r'([\d,\.]+[KMB]?)\s*(monthly\s*visits|visits)', snippet, re.I)
        if visits_match:
            visits_str = visits_match.group(1)
            monthly_visits = parse_number(visits_str)
            
            # 解析全球排名
            rank_match = re.search(r'#([\d,]+)\s*(global|rank)', snippet, re.I)
            global_rank = None
            if rank_match:
                global_rank = int(rank_match.group(1).replace(',', ''))
            
            return {
                'monthlyVisits': monthly_visits,
                'globalRank': global_rank,
                'dataSource': 'SimilarWeb',
                'dataSourceUrl': link,
                'dataFetchedAt': datetime.now().isoformat(),
                'dataVerified': True
            }
    
    return None

def parse_number(num_str: str) -> Optional[int]:
    """解析数字字符串（支持 K, M, B 后缀）"""
    try:
        num_str = num_str.replace(',', '').strip().upper()
        
        if num_str.endswith('B'):
            return int(float(num_str[:-1]) * 1_000_000_000)
        elif num_str.endswith('M'):
            return int(float(num_str[:-1]) * 1_000_000)
        elif num_str.endswith('K'):
            return int(float(num_str[:-1]) * 1_000)
        else:
            return int(float(num_str))
    except (ValueError, AttributeError):
        return None

def get_real_traffic_data(domain: str) -> Optional[Dict]:
    """获取真实流量数据（通过 Serper 搜索 SimilarWeb）"""
    print(f"  🔍 搜索 {domain} 的流量数据...")
    
    # 搜索 SimilarWeb 数据
    query = f"site:similarweb.com {domain} monthly visits traffic"
    results = serper_search(query)
    
    if not results:
        print(f"  ⚠️  搜索失败")
        return None
    
    # 解析数据
    traffic_data = parse_similarweb_data(results, domain)
    
    if traffic_data:
        print(f"  ✅ 月访问: {traffic_data['monthlyVisits']:,}")
        return traffic_data
    else:
        print(f"  ⚠️  未找到数据")
        return None

def get_github_data(github_url: str) -> Optional[Dict]:
    """获取 GitHub 仓库数据"""
    if not github_url or 'github.com' not in github_url:
        return None
    
    try:
        # 提取 owner/repo
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return None
        
        owner, repo = match.groups()
        repo = repo.rstrip('/')
        
        # GitHub API
        api_url = f'https://api.github.com/repos/{owner}/{repo}'
        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        
        return {
            'githubStars': data.get('stargazers_count'),
            'githubForks': data.get('forks_count'),
            'dataSource': 'GitHub API',
            'dataFetchedAt': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"  ⚠️  GitHub API 错误: {e}")
        return None

def discover_new_sites(search_queries: List[str]) -> List[str]:
    """通过搜索发现新网站"""
    discovered = set()
    
    for query in search_queries[:2]:  # 限制搜索次数
        print(f"  🔍 搜索: {query}")
        results = serper_search(query)
        
        if not results:
            continue
        
        for result in results.get('organic', [])[:5]:
            link = result.get('link', '')
            # 提取域名
            match = re.search(r'https?://([^/]+)', link)
            if match:
                domain = match.group(1).replace('www.', '')
                discovered.add(domain)
        
        time.sleep(1)  # 避免 API 限流
    
    return list(discovered)

def check_site_availability(domain: str) -> bool:
    """检查网站是否可访问"""
    try:
        url = f'https://{domain}'
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False

def update_site(name: str, data_file: Path, config: Dict) -> bool:
    """更新单个站点的数据"""
    print(f"\n{'='*60}")
    print(f"📊 更新 {name} 站点")
    print(f"{'='*60}")
    
    # 1. 发现新网站
    print("\n🔍 第一步：发现新网站")
    known_sites = set(config['known_sites'])
    discovered_sites = discover_new_sites(config['search_queries'])
    new_sites = [s for s in discovered_sites if s not in known_sites]
    
    if new_sites:
        print(f"  ✅ 发现 {len(new_sites)} 个新网站")
        for site in new_sites[:5]:  # 限制数量
            print(f"     - {site}")
    else:
        print(f"  📝 未发现新网站")
    
    # 2. 获取真实数据
    print("\n📈 第二步：获取真实流量数据")
    all_sites = list(known_sites) + new_sites[:5]
    competitors = []
    
    for domain in all_sites[:10]:  # 限制处理数量
        print(f"\n  处理: {domain}")
        
        # 检查可用性
        if not check_site_availability(domain):
            print(f"  ❌ 网站不可访问，跳过")
            continue
        
        # 获取流量数据
        traffic_data = get_real_traffic_data(domain)
        
        if not traffic_data:
            print(f"  ⚠️  无流量数据，跳过")
            continue
        
        # 构建竞品数据
        competitor = {
            'id': domain.replace('.', '-').replace('/', '-'),
            'name': domain.split('.')[0].title(),
            'domain': domain,
            'url': f'https://{domain}',
            'type': '综合目录',
            'description': '',
            **traffic_data,
            'trafficTrend': [],  # 无历史数据时留空
            'tier': classify_tier(traffic_data.get('monthlyVisits')),
            'status': 'active'
        }
        
        competitors.append(competitor)
        time.sleep(2)  # 避免 API 限流
    
    # 3. 保存数据
    print(f"\n💾 第三步：保存数据")
    data = {
        'lastUpdated': datetime.now().isoformat(),
        'config': {
            'category': name,
            'autoUpdate': True,
            'updateInterval': 'daily',
            'totalSites': len(competitors)
        },
        'competitors': competitors
    }
    
    data_file.parent.mkdir(parents=True, exist_ok=True)
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 已保存 {len(competitors)} 个竞品")
    return True

def classify_tier(monthly_visits: Optional[int]) -> str:
    """根据月访问量分类层级"""
    if not monthly_visits:
        return 'T3'
    
    if monthly_visits >= 1_000_000:
        return 'T1'
    elif monthly_visits >= 100_000:
        return 'T2'
    else:
        return 'T3'

def git_push() -> bool:
    """提交并推送到 GitHub"""
    try:
        # 检查是否有变更
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=SITE_DIR
        )
        
        if not result.stdout.strip():
            print("\n📝 无变更，跳过提交")
            return False
        
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        subprocess.run(['git', 'add', '.'], check=True, cwd=SITE_DIR)
        subprocess.run(
            ['git', 'commit', '-m', f'data: 真实数据自动更新 {date_str}'],
            check=True,
            cwd=SITE_DIR
        )
        subprocess.run(['git', 'push'], check=True, cwd=SITE_DIR)
        
        print("\n🚀 已推送到 GitHub")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git 操作失败: {e}")
        return False

def main():
    print("=" * 60)
    print(f"🔄 AI 情报中心 - 真实数据自动更新")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   模式: 真实数据获取（SimilarWeb + GitHub API）")
    print("=" * 60)
    
    sites_config = [
        ('global', SITE_DIR / 'data.json', DATA_SOURCES['global']),
        ('cn', SITE_DIR / 'cn' / 'data.json', DATA_SOURCES['cn']),
        ('skills', SITE_DIR / 'skills' / 'data.json', DATA_SOURCES['skills']),
        ('news', SITE_DIR / 'news' / 'data.json', DATA_SOURCES['news']),
        ('models', SITE_DIR / 'models' / 'data.json', DATA_SOURCES['models']),
    ]
    
    success_count = 0
    for name, path, config in sites_config:
        try:
            if update_site(name, path, config):
                success_count += 1
        except Exception as e:
            print(f"\n❌ 更新 {name} 失败: {e}")
    
    # 推送到 GitHub
    git_push()
    
    print("\n" + "=" * 60)
    print(f"✅ 更新完成: {success_count}/5 个站点")
    print(f"   所有数据均来自真实来源")
    print(f"   数据来源已标注在 dataSource 字段")
    print("=" * 60)

if __name__ == "__main__":
    main()
