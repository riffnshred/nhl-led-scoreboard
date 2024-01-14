class ClientConfig:
    def __init__(self,verbose: bool =False) -> None:
        self.verbose = verbose
        self.api_web_base_url = "https://api-web.nhle.com"
        self.api_web_api_ver = "/v1/"
