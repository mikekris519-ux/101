"""
通讯录交互命令系统
"""

from contact import ContactSystem
from typing import Optional
import sys


class ContactCommandInterface:
    """命令行交互界面"""
    
    def __init__(self, use_index: bool = True, use_phone_index: bool = True):
        self.system = ContactSystem(use_index=use_index, use_phone_index=use_phone_index)
        self.running = True
        
        # 首次启动时尝试加载已有数据
        count, msg = self.system.load_from_file()
        if count > 0:
            print(f"[启动] {msg}")
    
    def print_help(self):
        """打印帮助信息"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║              通讯录管理系统 - 命令帮助                      ║
╚════════════════════════════════════════════════════════════╝

命令格式：
  ADD <姓名> <电话> [备注]         - 添加联系人
  DEL <姓名或电话>                 - 删除联系人
  FIND_NAME <名字前缀>             - 按名字前缀查询
  FIND_PHONE <电话前缀>            - 按电话前缀查询
  LIST                              - 列出所有联系人
  STAT                              - 显示系统统计信息
  SAVE                              - 保存数据到文件
  HELP                              - 显示此帮助信息
  EXIT                              - 退出系统

示例：
  ADD 张三 13800000001 工作电话
  DEL 13800000001
  FIND_NAME 张
  FIND_PHONE 138
  LIST
"""
        print(help_text)
    
    def handle_add(self, parts: list):
        """处理ADD命令"""
        if len(parts) < 3:
            print("✗ 错误：格式不正确。用法：ADD <姓名> <电话> [备注]")
            return
        
        name = parts[1]
        phone = parts[2]
        remark = " ".join(parts[3:]) if len(parts) > 3 else ""
        
        success, msg = self.system.add_contact(name, phone, remark)
        if success:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}")
    
    def handle_del(self, parts: list):
        """处理DEL命令"""
        if len(parts) != 2:
            print("✗ 错误：格式不正确。用法：DEL <姓名或电话>")
            return
        
        key = parts[1]
        count, msg = self.system.del_contact(key)
        
        if count > 0:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}")
    
    def handle_find_name(self, parts: list):
        """处理FIND_NAME命令"""
        if len(parts) != 2:
            print("✗ 错误：格式不正确。用法：FIND_NAME <名字前缀>")
            return
        
        prefix = parts[1]
        results = self.system.find_by_name(prefix)
        
        if not results:
            print(f"✗ 未找到名字前缀为 '{prefix}' 的联系人")
            return
        
        print(f"\n找到 {len(results)} 个联系人：")
        self._print_contacts(results)
    
    def handle_find_phone(self, parts: list):
        """处理FIND_PHONE命令"""
        if len(parts) != 2:
            print("✗ 错误：格式不正确。用法：FIND_PHONE <电话前缀>")
            return
        
        prefix = parts[1]
        results = self.system.find_by_phone(prefix)
        
        if not results:
            print(f"✗ 未找到电话前缀为 '{prefix}' 的联系人")
            return
        
        print(f"\n找到 {len(results)} 个联系人：")
        self._print_contacts(results)
    
    def handle_list(self, parts: list):
        """处理LIST命令"""
        results = self.system.list_all()
        
        if not results:
            print("✗ 通讯录为空")
            return
        
        print(f"\n共 {len(results)} 个联系人：")
        self._print_contacts(results)
    
    def handle_stat(self, parts: list):
        """处理STAT命令"""
        stats = self.system.get_stats()
        
        stat_text = f"""
╔════════════════════════════════════════╗
║         系统统计信息                   ║
╚════════════════════════════════════════╝
总联系人数：       {stats['total_contacts']}
唯一姓名数：       {stats['unique_names']}
姓名索引启用：     {'是 (Trie树)' if stats['use_name_index'] else '否'}
电话索引启用：     {'是 (Trie树)' if stats['use_phone_index'] else '否'}
"""
        print(stat_text)
    
    def handle_save(self, parts: list):
        """处理SAVE命令"""
        success, msg = self.system.save_to_file()
        if success:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}")
    
    def _print_contacts(self, contacts: list):
        """格式化打印联系人列表"""
        print("\n┌─────────────────────────────────────────────────────┐")
        print("│ 序号 │     姓名     │      电话      │      备注      │")
        print("├─────────────────────────────────────────────────────┤")
        for idx, contact in enumerate(contacts, 1):
            name = contact.name[:8]
            phone = contact.phone
            remark = (contact.remark[:8] + "...") if len(contact.remark) > 8 else contact.remark
            print(f"│ {idx:2d}  │ {name:^10s} │ {phone:^14s} │ {remark:^14s} │")
        print("└─────────────────────────────────────────────────────┘\n")
    
    def run(self):
        """运行交互式命令系统"""
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║        欢迎使用通讯录管理系统 v1.0                        ║")
        print("║    输入 HELP 查看帮助，输入 EXIT 退出系统                  ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
        while self.running:
            try:
                user_input = input(">>> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                if len(parts) == 1:
                    parts = [user_input, ""]
                else:
                    # 进一步分割参数
                    parts = user_input.split()
                
                command = parts[0].upper()
                
                if command == "EXIT":
                    print("\n正在退出系统...")
                    self.running = False
                    break
                elif command == "HELP":
                    self.print_help()
                elif command == "ADD":
                    self.handle_add(parts)
                elif command == "DEL":
                    self.handle_del(parts)
                elif command == "FIND_NAME":
                    self.handle_find_name(parts)
                elif command == "FIND_PHONE":
                    self.handle_find_phone(parts)
                elif command == "LIST":
                    self.handle_list(parts)
                elif command == "STAT":
                    self.handle_stat(parts)
                elif command == "SAVE":
                    self.handle_save(parts)
                else:
                    print(f"✗ 未知命令：'{command}'。输入 HELP 查看帮助")
            
            except KeyboardInterrupt:
                print("\n\n[系统] 已中断")
                self.running = False
                break
            except Exception as e:
                print(f"✗ 错误：{str(e)}")


def main():
    """主函数"""
    # 启用索引以提升性能
    interface = ContactCommandInterface(use_index=True, use_phone_index=True)
    interface.run()


if __name__ == "__main__":
    main()
