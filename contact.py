"""
通讯录存储与检索系统
支持双向链表 + 散列表 + Trie树索引的高效检索
"""

from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class Contact:
    """联系人数据结构"""
    name: str
    phone: str
    remark: str = ""
    
    def __repr__(self):
        return f"Contact(name='{self.name}', phone='{self.phone}', remark='{self.remark}')"


class Node:
    """双向链表节点"""
    def __init__(self, contact: Contact):
        self.contact = contact
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class TrieNode:
    """Trie树节点"""
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.contacts: List[Contact] = []  # 该节点对应的联系人列表


class Trie:
    """Trie树实现，用于前缀检索"""
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, key: str, contact: Contact):
        """向Trie树中插入键值"""
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        if contact not in node.contacts:
            node.contacts.append(contact)
    
    def remove(self, key: str, contact: Contact):
        """从Trie树中移除键值"""
        def _remove(node: TrieNode, key: str, idx: int) -> bool:
            if idx == len(key):
                if contact in node.contacts:
                    node.contacts.remove(contact)
                return len(node.contacts) == 0 and len(node.children) == 0
            
            char = key[idx]
            if char not in node.children:
                return False
            
            should_delete = _remove(node.children[char], key, idx + 1)
            if should_delete:
                del node.children[char]
                return len(node.contacts) == 0 and len(node.children) == 0
            return False
        
        _remove(self.root, key, 0)
    
    def search_prefix(self, prefix: str) -> List[Contact]:
        """按前缀查询"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # 收集该前缀下所有联系人
        contacts = []
        def dfs(n: TrieNode):
            contacts.extend(n.contacts)
            for child in n.children.values():
                dfs(child)
        
        dfs(node)
        return contacts


class ContactSystem:
    """通讯录系统核心类"""
    
    def __init__(self, use_index: bool = True, use_phone_index: bool = True):
        self.head: Optional[Node] = None  # 双向链表头
        self.tail: Optional[Node] = None  # 双向链表尾
        self.size = 0
        
        # 散列表索引
        self.name_hash: Dict[str, List[Contact]] = {}  # 支持重名
        self.phone_hash: Dict[str, Contact] = {}  # 电话号码唯一
        
        # Trie树索引（可选）
        self.use_name_trie = use_index
        self.use_phone_trie = use_phone_index
        self.name_trie = Trie() if use_index else None
        self.phone_trie = Trie() if use_phone_index else None
        
        self.data_file = "contacts.json"
    
    def add_contact(self, name: str, phone: str, remark: str = "") -> Tuple[bool, str]:
        """添加联系人
        
        """
        if not name or not phone:
            return False, "错误：姓名和电话不能为空"
        
        # 检查电话号码是否已存在（电话号码应该唯一）
        if phone in self.phone_hash:
            return False, f"错误：电话号码 {phone} 已存在"
        
        contact = Contact(name, phone, remark)
        
        # 添加到双向链表
        node = Node(contact)
        if self.head is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1
        
        # 更新散列表
        if name not in self.name_hash:
            self.name_hash[name] = []
        self.name_hash[name].append(contact)
        self.phone_hash[phone] = contact
        
        # 更新Trie树
        if self.use_name_trie:
            self.name_trie.insert(name, contact)
        if self.use_phone_trie:
            self.phone_trie.insert(phone, contact)
        
        return True, f"成功：已添加联系人 {name} ({phone})"
    
    def del_contact(self, key: str) -> Tuple[int, str]:
        """删除联系人（按名字或电话号码）
        
        Returns:
            (删除数量, 提示信息)
        """
        deleted_count = 0
        deleted_contacts = []
        
        # 先查找要删除的联系人
        if key in self.phone_hash:
            # 按电话号码精确删除
            contact = self.phone_hash[key]
            deleted_contacts = [contact]
        else:
            # 按名字删除（可能删除多个重名联系人）
            if key in self.name_hash:
                deleted_contacts = self.name_hash[key][:]
        
        if not deleted_contacts:
            return 0, f"错误：未找到联系人 '{key}'"
        
        # 执行删除
        for contact in deleted_contacts:
            # 从双向链表中删除
            node = self._find_node(contact)
            if node:
                if node.prev:
                    node.prev.next = node.next
                else:
                    self.head = node.next
                
                if node.next:
                    node.next.prev = node.prev
                else:
                    self.tail = node.prev
                
                self.size -= 1
                deleted_count += 1
            
            # 更新散列表
            if contact.name in self.name_hash:
                if contact in self.name_hash[contact.name]:
                    self.name_hash[contact.name].remove(contact)
                if not self.name_hash[contact.name]:
                    del self.name_hash[contact.name]
            
            if contact.phone in self.phone_hash:
                del self.phone_hash[contact.phone]
            
            # 更新Trie树
            if self.use_name_trie:
                self.name_trie.remove(contact.name, contact)
            if self.use_phone_trie:
                self.phone_trie.remove(contact.phone, contact)
        
        return deleted_count, f"成功：已删除 {deleted_count} 个联系人"
    
    def find_by_name(self, name_prefix: str) -> List[Contact]:
        """按名字前缀查询"""
        if not name_prefix:
            return []
        
        # 优先使用Trie树
        if self.use_name_trie and self.name_trie:
            return self.name_trie.search_prefix(name_prefix)
        
        # 回退到散列表（精确匹配）
        results = []
        for name, contacts in self.name_hash.items():
            if name.startswith(name_prefix):
                results.extend(contacts)
        return results
    
