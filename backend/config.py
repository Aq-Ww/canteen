import os

class Config:
    # 数据库配置：MySQL
    # 请根据实际环境修改用户名(root)、密码(password)、主机(localhost)和端口(3306)
    # 数据库名默认为 smart_canteen
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1215wogiao#WAQ@127.0.0.1:3306/canteen?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_123456'
    
    # JSON配置
    JSON_AS_ASCII = False
