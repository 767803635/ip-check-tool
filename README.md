# IP 纯净度检测工具
一个基于 Python 开发的 IP 地址信誉度检测工具，使用 Scamalytics API 进行数据查询。支持批量检测 IP 地址的信誉度、风险等级和其他相关信息。
## 功能特点
- 图形化界面，操作简单直观
 支持单个 IP 地址输入和文件批量导入
 实时显示检测进度
 支持导出检测结果为 CSV 文件
 可配置 API 设置（支持自定义 Host）
 右键菜单支持快速复制 IP
 检测结果表格化展示，一目了然
## 检测信息包括
- IP 地址信誉评分
 ISP 服务商评分
 风险等级评估
 ISP 服务商信息
 地理位置信息
 最后查询时间
## 安装说明
1. 克隆仓库

```bash
git clone https://github.com/lee0033/ip-check-tool.git
```
2. 安装依赖
```bash
pip install -r requirements.txt
``` 
3. 运行程序
```bash
python main.py
```

## 使用说明

1. 首次使用需在设置中配置：
   - Username
   - API Key
   - API Host（可选）

2. 添加 IP 地址：
   - 直接在输入框输入单个 IP
   - 或通过"添加文件"按钮导入含有 IP 地址的文本文件

3. 点击"开始检测"进行批量检测

4. 检测完成后可：
   - 查看详细结果
   - 导出为 CSV 文件
   - 右键复制 IP 地址

## 配置文件

程序会在当前目录创建 `config.json` 文件保存配置信息：

```json
{
  "username": "your_username",
  "api_key": "your_api_key",
  "host": "your_host"
}
```

## 环境要求

- Python 3.6+
- tkinter (Python 自带)
- requests

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 免责声明

本工具仅供学习和研究使用，请勿用于非法用途。使用本工具所产生的一切后果由使用者自行承担。

## 联系方式

如有问题或建议，欢迎提交 Issue 或通过以下方式联系：

- Email: lee0033@126.com
