from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 用户表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) # 实际应用应存储Hash
    role = db.Column(db.String(20), default='user') # user, admin
    
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

# 食堂店铺表
class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    image = db.Column(db.String(255))
    score = db.Column(db.Float, default=5.0) # 综合评分
    
    dishes = db.relationship('Dish', backref='shop', lazy=True)
    orders = db.relationship('Order', backref='shop', lazy=True)

# 菜品表
class Dish(db.Model):
    __tablename__ = 'dishes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.String(500))
    score = db.Column(db.Float, default=5.0)
    sales = db.Column(db.Integer, default=0)
    
    # 预留情感分析缓存字段
    sentiment_positive = db.Column(db.Integer, default=0)
    sentiment_negative = db.Column(db.Integer, default=0)

# 订单表
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, processing, completed
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

# 订单详情表
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    count = db.Column(db.Integer, default=1)
    price_snapshot = db.Column(db.Float) # 下单时的价格

    dish = db.relationship('Dish')

# 评价表
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True) # 关联订单
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=True) # 关联菜品(如果是按菜评价)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False) # 1-5
    content = db.Column(db.Text)
    sentiment = db.Column(db.String(20)) # positive, negative, neutral
    created_at = db.Column(db.DateTime, default=datetime.now)
