from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.canteen_routes import canteen_bp

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

if __name__ == '__main__':
    # 启动前请确保数据库已创建并配置正确
    # 使用 python utils/db_init.py 初始化数据
    app.run(host='0.0.0.0', port=5000, debug=True)
