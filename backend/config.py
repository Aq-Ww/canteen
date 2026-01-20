import os

class Config:
    # 数据库配置：MySQL
    # 【重要】请接收者根据自己电脑的MySQL密码修改这里！
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1215wogiao#WAQ@127.0.0.1:3306/canteen?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_123456'
    
    # JSON配置
    JSON_AS_ASCII = False
