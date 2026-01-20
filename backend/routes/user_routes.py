from flask import Blueprint, request
from models import Shop, Dish, Order, OrderItem, Review, db
from utils.response import success_response, error_response
from services.recommend_service import RecommendService
from services.analysis_service import AnalysisService
from datetime import datetime
from sqlalchemy import func

user_bp = Blueprint('user', __name__)

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, '%Y/%m/%d %H:%M')
    except:
        return datetime.now()

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
    # 适配数据库数据不一致问题：Shop ID 是 100x，但 Dish 中的 shop_id 是 1-11
    query_shop_id = shop_id
    if shop_id > 1000:
        query_shop_id = shop_id - 1000
        
    dishes = Dish.query.filter_by(shop_id=query_shop_id).all()
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
        
    reviews = Review.query.filter_by(dish_id=dish_id).all()
    
    # 过滤 None 对象
    reviews = [r for r in reviews if r is not None]

    # Python 侧排序
    reviews.sort(key=lambda x: parse_time(x.created_at) if x.created_at else datetime.min, reverse=True)
    reviews = reviews[:10]
    
    reviews_data = []
    for r in reviews:
        username = "匿名用户"
        if r.user:
            username = r.user.username
            
        reviews_data.append({
            "id": r.id,
            "username": username,
            "score": r.score,
            "content": r.content,
            "date": parse_time(r.created_at).strftime('%Y-%m-%d')
        })
    
    # 修正返回的 shopId，确保前端跳转正确
    real_shop_id = dish.shop_id
    if real_shop_id < 1000:
        real_shop_id += 1000
        
    data = {
        "dish": {
            "id": dish.id,
            "shopId": real_shop_id,
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
    
    # 确保 shop_id 是整数
    try:
        if shop_id:
            shop_id = int(shop_id)
    except (ValueError, TypeError):
        shop_id = None

    if not shop_id:
        # Fallback if shopId is missing or invalid
        first_dish_id = items[0].get('dishId')
        first_dish = Dish.query.get(first_dish_id)
        shop_id = first_dish.shop_id if first_dish else 1
    
    # 修正 shop_id：如果来自 Dish 表 (1-11)，转换为 Shop 表 ID (1001-1011)
    if shop_id < 1000:
        shop_id += 1000

    # 生成不带前导零的日期字符串，匹配 SQL 风格 '2026/1/10 7:03'
    now = datetime.now()
    created_at_str = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}"

    try:
        # 手动生成 Order ID (适配无 AUTO_INCREMENT 的数据库)
        max_order_id = db.session.query(func.max(Order.id)).scalar() or 0
        new_order_id = max_order_id + 1

        order = Order(
            id=new_order_id,
            user_id=user_id,
            shop_id=shop_id,
            total_price=total_price,
            status='paid', # 模拟支付直接成功
            created_at=created_at_str
        )
        db.session.add(order)
        # 不使用 flush，因为我们已经手动指定了 ID
        # db.session.flush() 
        
        # 预先获取 OrderItem 的最大 ID
        max_item_id = db.session.query(func.max(OrderItem.id)).scalar() or 0
        
        # 创建订单项
        for index, item in enumerate(items):
            order_item = OrderItem(
                id=max_item_id + 1 + index,
                order_id=new_order_id,
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
        return success_response({"orderId": new_order_id}, "订单创建成功")
    except Exception as e:
        db.session.rollback()
        print(f"Order Create Error: {e}")
        return error_response(f"订单创建失败: {str(e)}")

# 我的订单
@user_bp.route('/orders', methods=['GET'])
def get_my_orders():
    user_id = 1 # Mock
    status = request.args.get('status', 'all')
    
    query = Order.query.filter_by(user_id=user_id)
    if status != 'all':
        query = query.filter_by(status=status)
        
    orders = query.all()
    
    # 过滤 None 对象
    orders = [o for o in orders if o is not None]

    # Python 侧排序
    orders.sort(key=lambda x: parse_time(x.created_at) if x.created_at else datetime.min, reverse=True)
    
    data = []
    for o in orders:
        items = []
        total_count = 0
        for i in o.items:
            # 防御性处理 dish 关联
            dish_name = "未知菜品"
            if i.dish:
                dish_name = i.dish.name
            items.append({"name": dish_name, "count": i.count})
            total_count += i.count
            
        # 防御性处理 shop 关联
        shop_name = "未知店铺"
        if o.shop:
            shop_name = o.shop.name

        data.append({
            "id": o.id,
            "shopName": shop_name,
            "status": o.status,
            "totalPrice": o.total_price,
            "totalCount": total_count,
            "items": items,
            "time": parse_time(o.created_at).strftime('%Y-%m-%d %H:%M')
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
    
    # 生成不带前导零的日期字符串
    now = datetime.now()
    created_at_str = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}"

    # 手动生成 Review ID
    max_review_id = db.session.query(func.max(Review.id)).scalar() or 0

    # 简单处理：给订单所属店铺评价，也可以扩展为给每个菜品评价
    review = Review(
        id=max_review_id + 1,
        user_id=user_id,
        order_id=order_id,
        shop_id=order.shop_id,
        score=score,
        content=content,
        created_at=created_at_str
    )
    db.session.add(review)
    
    # 更新订单状态
    order.status = 'completed'
    
    db.session.commit()
    return success_response(None, "评价成功")
