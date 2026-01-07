"""
单元测试模块
验证通讯录管理系统的各项功能
"""

import unittest
import os
from contact import ContactSystem, Contact, Trie


class TestContact(unittest.TestCase):
    """测试Contact类"""
    
    def test_contact_creation(self):
        """测试联系人对象创建"""
        contact = Contact("张三", "13800000001", "工作")
        self.assertEqual(contact.name, "张三")
        self.assertEqual(contact.phone, "13800000001")
        self.assertEqual(contact.remark, "工作")


class TestContactSystem(unittest.TestCase):
    """测试ContactSystem类"""
    
    def setUp(self):
        """设置测试环境"""
        self.system = ContactSystem(use_index=True, use_phone_index=True)
        # 清理可能存在的测试文件
        if os.path.exists("contacts.json"):
            os.remove("contacts.json")
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists("contacts.json"):
            os.remove("contacts.json")
    
    def test_add_contact(self):
        """测试添加联系人"""
        success, msg = self.system.add_contact("张三", "13800000001", "工作")
        self.assertTrue(success)
        self.assertEqual(self.system.size, 1)
    
    def test_add_contact_duplicate_phone(self):
        """测试添加重复电话号码"""
        self.system.add_contact("张三", "13800000001")
        success, msg = self.system.add_contact("李四", "13800000001")
        self.assertFalse(success)
        self.assertEqual(self.system.size, 1)
    
    def test_add_contact_same_name(self):
        """测试添加同名不同号码"""
        success1, _ = self.system.add_contact("张三", "13800000001")
        success2, _ = self.system.add_contact("张三", "13800000002")
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertEqual(self.system.size, 2)
        self.assertEqual(len(self.system.name_hash["张三"]), 2)
    
    def test_delete_by_phone(self):
        """测试按电话号码删除"""
        self.system.add_contact("张三", "13800000001")
        count, msg = self.system.del_contact("13800000001")
        self.assertEqual(count, 1)
        self.assertEqual(self.system.size, 0)
    
    def test_delete_by_name(self):
        """测试按名字删除"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("张三", "13800000002")
        count, msg = self.system.del_contact("张三")
        self.assertEqual(count, 2)
        self.assertEqual(self.system.size, 0)
    
    def test_delete_nonexistent(self):
        """测试删除不存在的联系人"""
        count, msg = self.system.del_contact("13800000001")
        self.assertEqual(count, 0)
    
    def test_find_by_name_prefix(self):
        """测试按名字前缀查询"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("张四", "13800000002")
        self.system.add_contact("李五", "13800000003")
        
        results = self.system.find_by_name("张")
        self.assertEqual(len(results), 2)
        
        results = self.system.find_by_name("李")
        self.assertEqual(len(results), 1)
    
    def test_find_by_phone_prefix(self):
        """测试按电话前缀查询"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("李四", "13900000001")
        
        results = self.system.find_by_phone("138")
        self.assertEqual(len(results), 1)
        
        results = self.system.find_by_phone("139")
        self.assertEqual(len(results), 1)
    
    def test_list_all(self):
        """测试列出所有联系人"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("李四", "13800000002")
        
        results = self.system.list_all()
        self.assertEqual(len(results), 2)
    
    def test_save_and_load(self):
        """测试数据持久化"""
        self.system.add_contact("张三", "13800000001", "工作")
        self.system.add_contact("李四", "13800000002", "生活")
        
        # 保存
        success, msg = self.system.save_to_file()
        self.assertTrue(success)
        self.assertTrue(os.path.exists("contacts.json"))
        
        # 加载
        new_system = ContactSystem()
        count, msg = new_system.load_from_file()
        self.assertEqual(count, 2)
        
        # 验证加载的数据
        all_contacts = new_system.list_all()
        self.assertEqual(len(all_contacts), 2)
    
    def test_system_stats(self):
        """测试系统统计"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("张四", "13800000002")
        
        stats = self.system.get_stats()
        self.assertEqual(stats["total_contacts"], 2)
        self.assertEqual(stats["unique_names"], 2)


class TestTrie(unittest.TestCase):
    """测试Trie树"""
    
    def setUp(self):
        """设置测试环境"""
        self.trie = Trie()
    
    def test_insert_and_search(self):
        """测试插入和查询"""
        contact1 = Contact("张三", "13800000001")
        contact2 = Contact("张四", "13800000002")
        contact3 = Contact("李五", "13800000003")
        
        self.trie.insert("张三", contact1)
        self.trie.insert("张四", contact2)
        self.trie.insert("李五", contact3)
        
        results = self.trie.search_prefix("张")
        self.assertEqual(len(results), 2)
        
        results = self.trie.search_prefix("李")
        self.assertEqual(len(results), 1)
    
    def test_remove(self):
        """测试删除"""
        contact = Contact("张三", "13800000001")
        self.trie.insert("张三", contact)
        
        results = self.trie.search_prefix("张")
        self.assertEqual(len(results), 1)
        
        self.trie.remove("张三", contact)
        results = self.trie.search_prefix("张")
        self.assertEqual(len(results), 0)


class TestSystemWithoutIndex(unittest.TestCase):
    """测试无索引的系统"""
    
    def setUp(self):
        """设置测试环境"""
        self.system = ContactSystem(use_index=False, use_phone_index=False)
    
    def test_find_by_name_without_index(self):
        """测试无索引时的名字查询"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("张四", "13800000002")
        self.system.add_contact("李五", "13800000003")
        
        results = self.system.find_by_name("张")
        self.assertEqual(len(results), 2)
    
    def test_find_by_phone_without_index(self):
        """测试无索引时的电话查询"""
        self.system.add_contact("张三", "13800000001")
        self.system.add_contact("李四", "13900000001")
        
        results = self.system.find_by_phone("138")
        self.assertEqual(len(results), 1)


def run_tests():
    """运行所有测试"""
    
    print("\n" + "="*70)
    print(" " * 20 + "开始运行单元测试")
    print("="*70 + "\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestContact))
    suite.addTests(loader.loadTestsFromTestCase(TestTrie))
    suite.addTests(loader.loadTestsFromTestCase(TestContactSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemWithoutIndex))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出汇总
    print("\n" + "="*70)
    print("测试汇总")
    print("="*70)
    print(f"运行测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
