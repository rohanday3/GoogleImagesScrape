import requests

class AutonomousProxy:
    def __init__(self, _apikey):
        self.apikey = _apikey
        self.base_url = "https://proxy.webshare.io/api/v2/"
        self.headers = {
            "Authorization": "Token " + self.apikey,
        }

    def get_proxy(self):
        #https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25
        url = self.base_url + "proxy/list/?mode=direct&page=1&page_size=25"
        response = requests.get(url, headers=self.headers)
        return response.json()
        
    def ReturnTOP10Proxies(self):
        proxies = self.get_proxy()["results"]
        urls = []
        for proxy in proxies:
            urls.append(self.GenerateProxyURL(proxy["username"],proxy["password"],proxy["proxy_address"],str(proxy["port"])))
        return urls[:10]
        
    def GenerateProxyURL(self,username,password,proxyaddress,port):
        return "http://"+username+":"+password+"@"+proxyaddress+":"+port+"/"