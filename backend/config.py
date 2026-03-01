from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "postgresql://duoduo:xcb123#@localhost:5432/postgres"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    
    # DashScope API配置
    # DASHSCOPE_API_KEY: str = "sk-499adf870c5f4f3ebe9b7c4a6b312935"
    # DASHSCOPE_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # DASHSCOPE_MODEL: str = "qwen-plus"
    # DASHSCOPE_API_KEY: str = "bce-v3/ALTAK-7wPBW4K3yRPmFohO553yZ/3cfe8f9a1cb9c73a2f683a6a812b5a48b348eef7"
    # DASHSCOPE_API_URL: str = "https://qianfan.baidubce.com/v2"
    # DASHSCOPE_MODEL: str = "deepseek-v3.1-250821"

    DASHSCOPE_API_KEY: str = "sk-lfjfutnpyspxziizzdtabyqygdajhjayphjaavohdlaqxbin"
    DASHSCOPE_API_URL: str = "https://api.siliconflow.cn/v1"
    DASHSCOPE_MODEL: str = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
    
    # 应用配置
    APP_NAME: str = "AI合同管理平台"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()