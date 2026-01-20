from flask import Blueprint, request
from models import User, db
from utils.response import success_response, error_response
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    user = User.query.filter_by(username=username, role=role).first()
    
    if user and user.password == password: # 实际应校验Hash
        token = str(uuid.uuid4()) # 模拟Token
        return success_response({
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }, "登录成功")
    
    return error_response("账号或密码错误", 401)
