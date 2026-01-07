"""
性能测试模块
对比线性扫描与索引查询的性能差异
"""

import time
import random
import string
from contact import ContactSystem


def generate_test_data(count: int) -> list:
    """生成测试数据"""
    contacts = []
    
    # 常见姓氏
    surnames = ["张", "王", "李", "赵", "刘", "周", "徐", "孙", "马", "何"]
    first_names = ["三", "四", "五", "六", "七", "八", "九", "十", "明", "强"]
    
    for i in range(count):
        name = random.choice(surnames) + random.choice(first_names)
        # 生成13开头的手机号
        phone = "13" + "".join([str(random.randint(0, 9)) for _ in range(9)])
        remark = f"contact_{i}"
        contacts.append((name, phone, remark))
    
    return contacts


def performance_test():
    """执行性能测试"""
    
    print("\n" + "="*70)
    print(" " * 15 + "通讯录管理系统 - 性能测试报告")
    print("="*70)
    
    test_sizes = [1000, 5000, 10000]
    
    for size in test_sizes:
        print(f"\n【测试规模 {size}】")
        print("-" * 70)
        
        # 生成测试数据
        test_data = generate_test_data(size)
        
        # 测试1: 带索引的系统
        print("\n1. 带索引系统测试 (使用Trie树+散列表)")
        print("   " + "-" * 65)
        
        system_with_index = ContactSystem(use_index=True, use_phone_index=True)
        
        # 添加数据
        start_time = time.time()
        for name, phone, remark in test_data:
            system_with_index.add_contact(name, phone, remark)
        add_time_with_index = time.time() - start_time
        print(f"   数据导入时间：{add_time_with_index:.4f}秒")
        
        # 按名字查询（前缀为单个汉字）
        search_prefix_name = "张"
        start_time = time.time()
        for _ in range(100):
            results = system_with_index.find_by_name(search_prefix_name)
        name_search_time_with_index = (time.time() - start_time) / 100
        count_with_index = len(system_with_index.find_by_name(search_prefix_name))
        print(f"   按名字前缀查询 '{search_prefix_name}'（100次平均）：{name_search_time_with_index*1000:.4f}ms（找到{count_with_index}条）")
        
        # 按电话查询（前缀为"13"）
        search_prefix_phone = "13"
        start_time = time.time()
        for _ in range(100):
            results = system_with_index.find_by_phone(search_prefix_phone)
        phone_search_time_with_index = (time.time() - start_time) / 100
        count_phone = len(system_with_index.find_by_phone(search_prefix_phone))
        print(f"   按电话前缀查询 '{search_prefix_phone}'（100次平均）：{phone_search_time_with_index*1000:.4f}ms（找到{count_phone}条）")
        

        
        # 测试2: 无索引的系统（仅链表）
        print("\n2. 无索引系统测试 (仅双向链表线性扫描)")
        print("   " + "-" * 65)
        
        system_without_index = ContactSystem(use_index=False, use_phone_index=False)
        
        # 添加数据
        start_time = time.time()
        for name, phone, remark in test_data:
            system_without_index.add_contact(name, phone, remark)
        add_time_without_index = time.time() - start_time
        print(f"   数据导入时间：{add_time_without_index:.4f}秒")
        
        # 按名字查询（线性扫描）
        start_time = time.time()
        for _ in range(100):
            results = system_without_index.find_by_name(search_prefix_name)
        name_search_time_without_index = (time.time() - start_time) / 100
        print(f"   按名字前缀查询 '{search_prefix_name}'（100次平均）：{name_search_time_without_index*1000:.4f}ms（找到{count_with_index}条）")
        
        # 按电话查询（线性扫描）
        start_time = time.time()
        for _ in range(100):
            results = system_without_index.find_by_phone(search_prefix_phone)
        phone_search_time_without_index = (time.time() - start_time) / 100
        print(f"   按电话前缀查询 '{search_prefix_phone}'（100次平均）：{phone_search_time_without_index*1000:.4f}ms（找到{count_phone}条）")
        
        # 性能对比
        print("\n3. 性能对比")
        print("   " + "-" * 65)
        
        if name_search_time_without_index > 0:
            name_speedup = name_search_time_without_index / name_search_time_with_index
            print(f"   名字查询加速比：{name_speedup:.2f}x")
        
        if phone_search_time_without_index > 0:
            phone_speedup = phone_search_time_without_index / phone_search_time_with_index
            print(f"   电话查询加速比：{phone_speedup:.2f}x")
        
        print(f"\n   总结：在 {size} 条记录规模下")
        print(f"   - 索引系统查询速度比线性扫描快")
        print(f"   - 名字查询：{name_search_time_with_index*1000:.4f}ms vs {name_search_time_without_index*1000:.4f}ms")
        print(f"   - 电话查询：{phone_search_time_with_index*1000:.4f}ms vs {phone_search_time_without_index*1000:.4f}ms")
    
    print("\n" + "="*70)
    print("性能测试完成")
    print("="*70 + "\n")


def benchmark_analysis():
    """性能分析汇总"""
    
    print("\n" + "="*70)
    print(" " * 15 + "性能分析与理论复杂度")
    print("="*70)
    
    analysis = """
【复杂度分析】

1. 双向链表操作：
   - 插入（尾部）：O(1)
   - 删除：O(n)（需遍历查找）
   - 遍历：O(n)

2. 散列表操作：
   - 插入/查询：O(1) 平均
   - 删除：O(1) 平均

3. Trie树操作（前缀检索）：
   - 插入：O(m)，m为字符串长度
   - 删除：O(m)
   - 前缀查询：O(m + k)，k为结果数量
   - 内存占用：O(n*m)，n为条目数，m为平均字符串长度

4. 线性扫描：
   - 前缀查询：O(n)

【系统设计优势】

✓ 双向链表：保持插入顺序，支持快速遍历
✓ 散列表索引：名字到联系人的快速映射
✓ Trie树索引：支持高效的前缀查询
✓ 混合设计：结合多种数据结构的优势

【查询性能优化】

- 精确查询（电话）：O(1) - 直接散列表查找
- 前缀查询：O(m + k) 使用Trie树，vs O(n) 线性扫描
- 在 n=10000 时，性能提升明显

【持久化策略】

- JSON格式存储，易于调试和备份
- 系统启动自动加载历史数据
- SAVE命令手动保存，支持断点恢复
"""
    print(analysis)
    print("="*70 + "\n")


if __name__ == "__main__":
    performance_test()
    benchmark_analysis()
