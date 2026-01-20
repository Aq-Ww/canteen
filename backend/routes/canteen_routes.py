from flask import Blueprint, request
from models import Order, Review, db
from utils.response import success_response, error_response
from services.analysis_service import AnalysisService

canteen_bp = Blueprint('canteen', __name__)

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
    
    orders = Order.query.filter_by(status=status).order_by(Order.created_at.desc()).all()
    
    data = []
    for o in orders:
        items = [{"name": i.dish.name, "count": i.count} for i in o.items]
        data.append({
            "id": o.id,
            "time": o.created_at.strftime('%H:%M'),
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
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    data = [{
        "id": r.id,
        "username": r.user.username,
        "score": r.score,
        "content": r.content,
        "date": r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in reviews]
    return success_response(data)
