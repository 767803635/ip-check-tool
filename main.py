import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from check import IPChecker
import json
import threading
import re
import time
import os
from typing import Dict, List, Any, Optional

class IPCheckerGUI:
    # 常量定义
    DEFAULT_API_KEY = "5c81e37f6af4f95ca00ef2ec4c8d27a19540895a50e1b73b8ee621b2557c9265"
    DEFAULT_USERNAME = "767803635"
    DEFAULT_HOST = 'https://api11.scamalytics.com/'
    CONFIG_FILE = "config.json"
    WINDOW_SIZE = "1200x600"
    
    # 表格列配置
    COLUMNS = [
        {"id": "IP地址", "width": 100},
        {"id": "信誉评分", "width": 80},
        {"id": "ISP 服务商评分", "width": 90},
        {"id": "风险等级", "width": 200},
        {"id": "ISP服务商", "width": 200},
        {"id": "国家", "width": 60},
        {"id": "最后查询时间", "width": 150},
        {"id": "状态", "width": 100}
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("IP 纯净度检测工具")
        self.root.geometry(self.WINDOW_SIZE)
        
        # 加载配置
        self.load_config()
        self.checker = IPChecker(self.username, self.api_key,self.host)
        self.ip_list: List[str] = []
        
        self.create_menu()
        self.setup_gui()
        
    def setup_gui(self) -> None:
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建顶部工具栏
        self.create_toolbar(main_frame)
        
        # 创建表格区域
        self.create_treeview(main_frame)
        
    def create_toolbar(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # 创建IP输入框
        ip_frame = ttk.Frame(toolbar)
        ip_frame.pack(side=tk.LEFT, padx=5)
        
        self.ip_var = tk.StringVar()
        ip_entry = ttk.Entry(ip_frame, textvariable=self.ip_var, width=20)
        ip_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建按钮，使用英文属性名
        self.buttons = {
            'add_ip': ttk.Button(toolbar, text="添加IP", command=self.add_single_ip),
            'add_file': ttk.Button(toolbar, text="添加文件", command=self.add_file),
            'start': ttk.Button(toolbar, text="开始检测", command=self.start_check),
            'clear': ttk.Button(toolbar, text="清空列表", command=self.clear_list),
            'export': ttk.Button(toolbar, text="导出结果", command=self.export_results)
        }
        
        # 放置按钮
        for btn in self.buttons.values():
            btn.pack(side=tk.LEFT, padx=5)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(toolbar, variable=self.progress_var, maximum=100)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
    def create_treeview(self, parent: ttk.Frame) -> None:
        # 创建表格容器
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格和滚动条
        self.tree = ttk.Treeview(tree_frame, columns=[col["id"] for col in self.COLUMNS], show='headings')
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        
        # 配置列
        for col in self.COLUMNS:
            self.tree.heading(col["id"], text=col["id"], anchor=tk.CENTER)
            self.tree.column(col["id"], width=col["width"], anchor=tk.CENTER)
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="复制IP地址", command=self.copy_ip)

        
        # 绑定右键事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def add_file(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                found_ips = set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', content))
                new_ips = found_ips - set(self.ip_list)
                
                for ip in new_ips:
                    self.ip_list.append(ip)
                    self.tree.insert('', tk.END, values=(ip, '', '', '', '', '', '', '待检测'))
                
                self._show_add_result(len(new_ips))
                
        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错：{str(e)}")
    
    def _show_add_result(self, count: int) -> None:
        if count > 0:
            messagebox.showinfo("成功", f"已添加 {count} 个新IP地址")
        else:
            messagebox.showinfo("提示", "没有新的IP地址需要添加")
    
    def load_config(self) -> None:
        """加载配置文件"""
        if not os.path.exists(self.CONFIG_FILE):
            self.api_key = self.DEFAULT_API_KEY
            self.username = self.DEFAULT_USERNAME
            self.host = self.DEFAULT_HOST
            return
            
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get('api_key', '') or self.DEFAULT_API_KEY
                self.username = config.get('username', '') or self.DEFAULT_USERNAME
                self.host = config.get('host', '') or self.DEFAULT_HOST
        except:
            self.api_key = self.DEFAULT_API_KEY
            self.username = self.DEFAULT_USERNAME
            self.host = self.DEFAULT_HOST

    def save_config(self, new_api_key: str, new_username: str, new_host: str) -> bool:
        """保存配置到文件"""
        try:
            config = {
                'api_key': new_api_key,
                'username': new_username,
                'host': new_host
            }
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存配置文件时出错：{str(e)}")
            return False
    
    def start_check(self):
        if not self.api_key:
            messagebox.showerror("错误", "请先在设置中配置 API 密钥！")
            return
        
        if not self.ip_list:
            messagebox.showwarning("警告", "请先添加IP地址")
            return
            
        # 使用新的按钮引用方式
        self.buttons['add_ip']['state'] = 'disabled'
        self.buttons['add_file']['state'] = 'disabled'
        self.buttons['start']['state'] = 'disabled'
        self.buttons['clear']['state'] = 'disabled'
        self.buttons['export']['state'] = 'disabled'
        
        # 在新线程中执行检测
        thread = threading.Thread(target=self.check_all_ips)
        thread.daemon = True
        thread.start()
    
    def check_all_ips(self):
        total = len(self.ip_list)
        for i, ip in enumerate(self.ip_list):
            # 更新进度条
            progress = (i + 1) / total * 100
            self.progress_var.set(progress)
            
            # 获取对应的表格项
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == ip:
                    # 更新状态为"检测中"
                    self.tree.set(item, "状态", "检测中")
                    self.root.update()
                    
                    # 检测IP
                    result = self.checker.check_ip(ip)
                    if isinstance(result, dict):
                        values = [
                            ip,
                            result.get("信誉评分", ""),
                            result.get("ISP 服务商评分", ""),
                            result.get("风险等级", ""),
                            result.get("ISP服务商", ""),
                            result.get("国家", ""),
                            result.get("最后查询时间", ""),
                            "完成"
                        ]
                        self.tree.item(item, values=values)
                    else:
                        self.tree.set(item, "状态", f"错误: {result}")
                    
                    # 强制更新界面
                    self.root.update()
                    
                    # 添加延时以避免API限制
                    time.sleep(1)
                    break
        
        # 恢复按钮状态
        self.buttons['add_ip']['state'] = 'normal'
        self.buttons['add_file']['state'] = 'normal'
        self.buttons['start']['state'] = 'normal'
        self.buttons['clear']['state'] = 'normal'
        self.buttons['export']['state'] = 'normal'
        messagebox.showinfo("完成", "所有IP检测完成！")
    
    def clear_list(self):
        self.ip_list.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.progress_var.set(0)
    
    def export_results(self):
        if not self.tree.get_children():
            messagebox.showwarning("警告", "没有可导出的数据！")
            return
        
        # 获取保存文件路径
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile='ip_check_results.csv'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    # 获取列标题
                    columns = self.tree.cget("columns")
                    
                    # 创建 CSV writer
                    import csv
                    writer = csv.writer(f)
                    
                    # 写入表头
                    writer.writerow(columns)
                    
                    # 写入数据
                    for item in self.tree.get_children():
                        values = self.tree.item(item)['values']
                        writer.writerow(values)
                    
                messagebox.showinfo("成功", f"数据已成功导出到：\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出文件时出错：{str(e)}")
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="添加文件", command=self.add_file)
        file_menu.add_command(label="导出结果", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="API设置", command=self.show_api_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def show_api_settings(self):
        # 创建设置对话框
        settings_window = tk.Toplevel(self.root)
        settings_window.title("API 设置")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # 设置模态窗口
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 创建框架
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Username 输入框
        ttk.Label(frame, text="Username:").pack(anchor=tk.W)
        username_var = tk.StringVar(value=self.username)
        username_entry = ttk.Entry(frame, textvariable=username_var, width=50)
        username_entry.pack(fill=tk.X, pady=(5, 15))
        
        # API密钥输入框
        ttk.Label(frame, text="API 密钥:").pack(anchor=tk.W)
        api_key_var = tk.StringVar(value=self.api_key)
        api_key_entry = ttk.Entry(frame, textvariable=api_key_var, width=50)
        api_key_entry.pack(fill=tk.X, pady=(5, 15))
        
        # 主机输入框
        ttk.Label(frame, text="Host:").pack(anchor=tk.W)
        host_var = tk.StringVar(value=self.host)
        host_entry = ttk.Entry(frame, textvariable=host_var, width=50)
        host_entry.pack(fill=tk.X, pady=(5, 15))
        

        def save_settings():
            new_api_key = api_key_var.get().strip()
            new_username = username_var.get().strip()
            new_host = host_var.get().strip()
            if new_api_key and new_username:
                if self.save_config(new_api_key, new_username,new_host):
                    self.api_key = new_api_key
                    self.username = new_username
                    self.host = new_host
                    self.checker = IPChecker(self.username, self.api_key,self.host)
                    messagebox.showinfo("成功", "设置已更新！")
                    settings_window.destroy()
            else:
                messagebox.showerror("错误", "Username 和 API 密钥不能为空！")
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 保存和取消按钮
        ttk.Button(button_frame, text="保存", command=save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.RIGHT)
    
    def show_about(self):
        about_text = """IP 纯净度检测工具
版本: 1.0
    
本工具用于检测 IP 地址的信誉度和安全性。
使用 AbuseIPDB API 进行数据查询。

使用说明：
1. 在设置中配置您的 API 密钥
2. 添加需要检测的 IP 地址文件
3. 点击开始检测
4. 可以将结果导出为 CSV 文件
"""
        messagebox.showinfo("关于", about_text)
    
    def add_single_ip(self) -> None:
        """添加单个IP地址"""
        ip = self.ip_var.get().strip()
        if not ip:
            messagebox.showwarning("警告", "请输入IP地址")
            return
        
        # 验证IP格式
        ip_pattern = r'^(?:\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, ip):
            messagebox.showerror("错误", "无效的IP地址格式")
            return
        
        # 检查是否已存在
        if ip in self.ip_list:
            messagebox.showinfo("提示", "该IP地址已在列表中")
            return
        
        # 添加到列表和表格
        self.ip_list.append(ip)
        self.tree.insert('', tk.END, values=(ip, '', '', '', '', '', '', '待检测'))
        
        # 清空输入框
        self.ip_var.set('')
        
        messagebox.showinfo("成功", "IP地址已添加")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 获取点击的项
        item = self.tree.identify_row(event.y)
        if item:
            # 选中被点击的项
            self.tree.selection_set(item)
            # 显示菜单
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_ip(self):
        """复制选中行的IP地址"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # 获取选中行的IP地址（第一列）
        item = selection[0]
        ip = self.tree.item(item)['values'][0]
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(ip)
        
        # 可选：显示提示
        messagebox.showinfo("成功", f"IP地址 {ip} 已复制到剪贴板")
    
    # def copy_row(self):
    #     """复制选中行的所有信息"""
    #     selection = self.tree.selection()
    #     if not selection:
    #         return
        
    #     # 获取选中行的所有值
    #     item = selection[0]
    #     values = self.tree.item(item)['values']
        
    #     # 将值转换为制表符分隔的字符串
    #     row_text = '\t'.join(str(v) for v in values)
        
    #     # 复制到剪贴板
    #     self.root.clipboard_clear()
    #     self.root.clipboard_append(row_text)
        
    #     # 可选：显示提示
    #     messagebox.showinfo("成功", "行数据已复制到剪贴板")



def main():
    root = tk.Tk()
    app = IPCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
