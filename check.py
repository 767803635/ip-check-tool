import requests
from datetime import datetime

class IPChecker:
    def __init__(self, username, api_key,host:str):
        self.api_key = api_key
        self.username = username
        self.host = host if not host.endswith('/') else host[:-1]
        self.base_url = f"{self.host}/{self.username}/"
        
    def check_ip(self, ip_address):
        params = {
            'key': self.api_key,
            'ip': ip_address
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._format_result(result)
            else:
                return f"API 请求失败 (状态码: {response.status_code})"
                
        except Exception as e:
            return f"错误: {str(e)}"
    
    def _format_result(self, data):
        result = {
            "IP地址": data.get('ip', '未知'),
            "信誉评分": 100 - int(data.get('score', 0)),  # 转换为纯净度分数
            "ISP 服务商评分": data.get('ISP Fraud Score', '0'),
            "风险等级": data.get('risk', '未知'),
            "ISP服务商": data.get('ISP Name', '未知'),
            "国家": data.get('ip_country_name', '未知'),
            "最后查询时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result