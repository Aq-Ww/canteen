from flask import Blueprint, request
from models import Shop, Dish, Order, OrderItem, Review, db
from utils.response import success_response, error_response
from services.recommend_service import RecommendService
from services.analysis_service import AnalysisService
from datetime import datetime

user_bp = Blueprint('user', __name__)

# 首页推荐
@user_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    # 假设从header或token获取user_id，这里简化为固定ID或参数
    user_id = 1 
    data = RecommendService.get_recommendations(user_id)
    return success_response(data)

# 店铺列表
@user_bp.route('/shops', methods=['GET'])
def get_shops():
    shops = Shop.query.all()
    data = []
    for s in shops:
        review_count = Review.query.filter_by(shop_id=s.id).count()
        data.append({
            "id": s.id,
            "name": s.name,
            "score": s.score,
            "description": s.description,
            "image": s.image,
            "reviewCount": review_count
        })
    return success_response(data)

# 店铺详情
@user_bp.route('/shop/<int:shop_id>', methods=['GET'])
def get_shop_detail(shop_id):
    shop = Shop.query.get(shop_id)
    if not shop:
        return error_response("店铺不存在")
        
    # 调用分析服务获取情感分析和词云
    analysis = AnalysisService.analyze_sentiment(shop_id)
    
    data = {
        "id": shop.id,
        "name": shop.name,
        "score": shop.score,
        "image": shop.image,
        "sentiment": analysis['sentiment'],
        "keywords": analysis['keywords']
    }
    return success_response(data)

# 店铺菜单
@user_bp.route('/shop/<int:shop_id>/menu', methods=['GET'])
def get_shop_menu(shop_id):
    dishes = Dish.query.filter_by(shop_id=shop_id).all()
    data = [{
        "id": d.id,
        "name": d.name,
        "price": d.price,
        "sales": d.sales,
        "image": d.image,
        "score": d.score
    } for d in dishes]
    return success_response(data)

# 菜品详情
@user_bp.route('/dish/<int:dish_id>', methods=['GET'])
def get_dish_detail(dish_id):
    dish = Dish.query.get(dish_id)
    if not dish:
        return error_response("菜品不存在")
        
    reviews = Review.query.filter_by(dish_id=dish_id).order_by(Review.created_at.desc()).limit(10).all()
    reviews_data = [{
        "id": r.id,
        "username": r.user.username,
        "score": r.score,
        "content": r.content,
        "date": r.created_at.strftime('%Y-%m-%d')
    } for r in reviews]
    
    data = {
        "dish": {
            "id": dish.id,
            "shopId": dish.shop_id,
            "name": dish.name,
            "price": dish.price,
            "score": dish.score,
            "sales": dish.sales,
            "description": dish.description,
            "image": dish.image
        },
        "reviews": reviews_data
    }
    return success_response(data)

# 创建订单
@user_bp.route('/order/create', methods=['POST'])
def create_order():
    data = request.json
    items = data.get('items', [])
    total_price = data.get('total', 0)
    
    # 假设当前用户ID为1（实际应从Token解析）
    user_id = 1
    
    if not items:
        return error_response("订单为空")
        
    # 创建订单
    # 假设所有菜品来自同一个店铺，或者订单归属第一个菜品的店铺
    # 简化处理：取第一个菜品的店铺ID
    shop_id = items[0].get('shopId')
    if not shop_id:
        # Fallback if shopId is missing
        first_dish_id = items[0].get('dishId')
        first_dish = Dish.query.get(first_dish_id)
        shop_id = first_dish.shop_id if first_dish else 1
    
    order = Order(
        user_id=user_id,
        shop_id=shop_id,
        total_price=total_price,
        status='paid', # 模拟支付直接成功
        created_at=datetime.now()
    )
    db.session.add(order)
    db.session.flush() # 获取order.id
    
    # 创建订单项
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            dish_id=item['dishId'],
            count=item['count'],
            price_snapshot=item['price']
        )
        db.session.add(order_item)
        
        # 更新销量
        dish = Dish.query.get(item['dishId'])
        if dish:
            dish.sales += item['count']
            
    db.session.commit()
    
    return success_response({"orderId": order.id}, "订单创建成功")

# 我的订单
@user_bp.route('/orders', methods=['GET'])
def get_my_orders():
    user_id = 1 # Mock
    status = request.args.get('status', 'all')
    
    query = Order.query.filter_by(user_id=user_id)
    if status != 'all':
        query = query.filter_by(status=status)
        
    orders = query.order_by(Order.created_at.desc()).all()
    
    data = []
    for o in orders:
        items = []
        total_count = 0
        for i in o.items:
            items.append({"name": i.dish.name, "count": i.count})
            total_count += i.count
            
        data.append({
            "id": o.id,
            "shopName": o.shop.name,
            "status": o.status,
            "totalPrice": o.total_price,
            "totalCount": total_count,
            "items": items,
            "time": o.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return success_response(data)

# 发布评价
@user_bp.route('/review', methods=['POST'])
def create_review():
    data = request.json
    order_id = data.get('orderId')
    score = data.get('score')
    content = data.get('content')
    user_id = 1
    
    order = Order.query.get(order_id)
    if not order:
        return error_response("订单不存在")
        
    # 简单处理：给订单所属店铺评价，也可以扩展为给每个菜品评价
    review = Review(
        user_id=user_id,
        order_id=order_id,
        shop_id=order.shop_id,
        score=score,
        content=content,
        created_at=datetime.now()
    )
    db.session.add(review)
    
    # 更新订单状态
    order.status = 'completed'
    
    db.session.commit()
    return success_response(None, "评价成功")
