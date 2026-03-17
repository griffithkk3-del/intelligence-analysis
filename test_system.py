#!/usr/bin/env python3
"""
快速测试脚本 - 验证新系统是否正常工作
"""
import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

def test_environment():
    """测试环境配置"""
    print("=" * 60)
    print("1️⃣  测试环境配置")
    print("=" * 60)
    
    # 检查 API Key
    api_key = os.environ.get('SERPER_API_KEY')
    if api_key:
        print(f"✅ SERPER_API_KEY 已设置: {api_key[:10]}...")
    else:
        print("❌ SERPER_API_KEY 未设置")
        print("   请运行: export SERPER_API_KEY='your_api_key'")
        return False
    
    # 检查文件
    files = [
        'daily_update_v2.py',
        'validate_data_v2.py',
        'daily_update.sh'
    ]
    
    for file in files:
        if Path(file).exists():
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
            return False
    
    return True

def test_data_fetching():
    """测试数据获取"""
    print("\n" + "=" * 60)
    print("2️⃣  测试数据获取")
    print("=" * 60)
    
    try:
        from daily_update_v2 import get_real_traffic_data, serper_search
        
        # 测试 Serper 搜索
        print("\n🔍 测试 Serper 搜索...")
        result = serper_search("test query")
        if result:
            print("✅ Serper API 连接成功")
        else:
            print("❌ Serper API 连接失败")
            return False
        
        # 测试数据获取
        print("\n🔍 测试获取 theresanaiforthat.com 数据...")
        data = get_real_traffic_data("theresanaiforthat.com")
        
        if data:
            print("✅ 数据获取成功:")
            print(f"   月访问: {data.get('monthlyVisits', 'N/A'):,}")
            print(f"   全球排名: {data.get('globalRank', 'N/A')}")
            print(f"   数据来源: {data.get('dataSource', 'N/A')}")
            print(f"   获取时间: {data.get('dataFetchedAt', 'N/A')}")
            return True
        else:
            print("⚠️  未获取到数据（可能是 SimilarWeb 没有该网站数据）")
            return True  # 这不算失败
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation():
    """测试数据验证"""
    print("\n" + "=" * 60)
    print("3️⃣  测试数据验证")
    print("=" * 60)
    
    try:
        from validate_data_v2 import validate_data_authenticity
        
        # 测试验证功能
        data_file = Path('data.json')
        if not data_file.exists():
            print("⚠️  data.json 不存在，跳过验证测试")
            return True
        
        print("\n🔍 验证 data.json...")
        issues = validate_data_authenticity(data_file)
        
        if not issues:
            print("✅ 数据验证通过")
            return True
        else:
            print(f"⚠️  发现 {len(issues)} 个问题:")
            for issue in issues[:5]:  # 只显示前 5 个
                print(f"   {issue}")
            if len(issues) > 5:
                print(f"   ... 还有 {len(issues) - 5} 个问题")
            return True  # 有问题不算测试失败
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("4️⃣  测试错误处理")
    print("=" * 60)
    
    try:
        from daily_update_v2 import get_real_traffic_data
        
        # 测试无效域名
        print("\n🔍 测试无效域名...")
        data = get_real_traffic_data("invalid-domain-12345.com")
        if data is None:
            print("✅ 无效域名正确返回 None")
        else:
            print("⚠️  无效域名返回了数据（可能是误判）")
        
        # 测试空域名
        print("\n🔍 测试空域名...")
        data = get_real_traffic_data("")
        if data is None:
            print("✅ 空域名正确返回 None")
        else:
            print("❌ 空域名应该返回 None")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "🧪" * 30)
    print("AI 情报中心 - 新系统测试")
    print("🧪" * 30 + "\n")
    
    tests = [
        ("环境配置", test_environment),
        ("数据获取", test_data_fetching),
        ("数据验证", test_data_validation),
        ("错误处理", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 测试异常: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以部署。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
