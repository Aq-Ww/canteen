from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.canteen_routes import canteen_bp
import sys

app = Flask(__name__)
app.config.from_object(Config)

# 初始化DB
db.init_app(app)

# 允许跨域
CORS(app)

# 注册路由
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(canteen_bp, url_prefix='/api')

def check_db_connection():
    """启动时检查数据库连接"""
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            print("==========================================")
            print("✅ 数据库连接成功！后端服务已就绪。")
            print("==========================================")
    except Exception as e:
        print("==========================================")
        print("❌ 数据库连接失败！请检查以下几点：")
        print(f"1. 错误详情: {str(e)}")
        print("2. 请确保本地已安装 MySQL 并启动")
        print("3. 请确保已导入 canteen.sql 到数据库")
        print("4. 请打开 backend/config.py 修改为正确的数据库密码")
        print("==========================================")

if __name__ == '__main__':
    # 启动前检查数据库
    check_db_connection()
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)
