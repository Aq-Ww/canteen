from flask import Blueprint, request
from models import Order, Review, db
from utils.response import success_response, error_response
from services.analysis_service import AnalysisService
from datetime import datetime

canteen_bp = Blueprint('canteen', __name__)

def parse_time(time_str):
    try:
        # 尝试适配 SQL 文件中的时间格式 '2026/1/10 7:03'
        return datetime.strptime(time_str, '%Y/%m/%d %H:%M')
    except:
        return datetime.now()

# 经营分析看板
@canteen_bp.route('/canteen/dashboard', methods=['GET'])
def get_dashboard():
    # 销量预测
    prediction_data = AnalysisService.predict_sales()
    
    # 差评聚类
    cluster_data = AnalysisService.cluster_negative_reviews()
    
    return success_response({
        "salesHistory": prediction_data['salesHistory'],
        "predictions": prediction_data['predictions'],
        "clusters": cluster_data
    })

# 订单管理
@canteen_bp.route('/canteen/orders', methods=['GET'])
def get_orders():
    # 假设管理员属于某个店铺，这里简化为查看所有或特定店铺
    # 实际应从 login token 获取 shop_id
    status = request.args.get('status', 'pending')
    
    if status == 'pending':
        # "待接单" 包含 pending (未支付/待处理) 和 paid (已支付/待接单)
        orders = Order.query.filter(Order.status.in_(['pending', 'paid'])).all()
    else:
        orders = Order.query.filter_by(status=status).all()
    
    # 过滤 None 对象并安全访问
    orders = [o for o in orders if o is not None]

    # Python 侧排序，因为 created_at 是字符串
    # 增加防御性判断，防止 created_at 为 None 或对象异常
    orders.sort(key=lambda x: parse_time(x.created_at) if x.created_at else datetime.min, reverse=True)
    
    data = []
    for o in orders:
        # 防御性处理：防止 o.items 中的 dish 关联失效 (Dish shop_id=1 vs Shop shop_id=1001)
        items = []
        for i in o.items:
            dish_name = "未知菜品"
            if i.dish:
                dish_name = i.dish.name
            items.append({"name": dish_name, "count": i.count})
            
        # 解析时间字符串用于显示
        dt = parse_time(o.created_at)
        data.append({
            "id": o.id,
            "time": dt.strftime('%H:%M'),
            "totalPrice": o.total_price,
            "status": o.status,
            "items": items
        })
    return success_response(data)

# 更新订单状态
@canteen_bp.route('/canteen/order/update', methods=['POST'])
def update_order():
    data = request.json
    order_id = data.get('id')
    status = data.get('status')
    
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
        return success_response(None, "状态更新成功")
    return error_response("订单不存在")

# 评价管理
@canteen_bp.route('/canteen/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.all()
    
    # 过滤 None 对象
    reviews = [r for r in reviews if r is not None]

    # Python 侧排序
    reviews.sort(key=lambda x: parse_time(x.created_at) if x.created_at else datetime.min, reverse=True)
    
    data = []
    for r in reviews:
        # 防御性处理 user 关联
        username = "匿名用户"
        if r.user:
            username = r.user.username
            
        data.append({
            "id": r.id,
            "username": username,
            "score": r.score,
            "content": r.content,
            "date": parse_time(r.created_at).strftime('%Y-%m-%d %H:%M')
        })
    return success_response(data)
