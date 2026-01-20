import sys
import os
import random
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, User, Shop, Dish, Order, OrderItem, Review

def init_db():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("Tables created.")

        # 1. Create Users (30 preset users)
        users = []
        # Admin
        admin = User(username='admin', password='123', role='admin')
        users.append(admin)
        # Normal Users
        for i in range(1, 31):
            u = User(username=f'user{i}', password='123', role='user')
            users.append(u)
        
        db.session.add_all(users)
        db.session.commit()
        print("30 Users created.")

        # 2. Create Shops (11 shops)
        shops = []
        shop_names = [f'第{i}食堂' for i in range(1, 12)]
        for name in shop_names:
            s = Shop(
                name=name, 
                description=f'{name}欢迎您，提供各类美味佳肴。',
                score=round(random.uniform(3.5, 5.0), 1),
                image='' # Use placeholder on frontend
            )
            shops.append(s)
        db.session.add_all(shops)
        db.session.commit()
        print("11 Shops created.")

        # 3. Create Dishes
        dishes = []
        dish_names = ['红烧肉', '宫保鸡丁', '麻婆豆腐', '青椒肉丝', '番茄炒蛋', '水煮鱼', '回锅肉', '土豆牛腩']
        for shop in shops:
            # Each shop has 5-8 dishes
            num_dishes = random.randint(5, 8)
            shop_dish_names = random.sample(dish_names, num_dishes)
            for d_name in shop_dish_names:
                d = Dish(
                    shop_id=shop.id,
                    name=d_name,
                    price=random.randint(8, 35),
                    description=f'正宗{d_name}，食材新鲜。',
                    score=round(random.uniform(4.0, 5.0), 1),
                    sales=random.randint(50, 500)
                )
                dishes.append(d)
        db.session.add_all(dishes)
        db.session.commit()
        print("Dishes created.")

        # 4. Create Mock Orders & Reviews for Analysis
        # Create some historical orders and reviews
        orders = []
        reviews = []
        
        # Positive reviews keywords
        pos_words = ['好吃', '美味', '不错', '分量足', '便宜', '喜欢']
        # Negative reviews keywords
        neg_words = ['难吃', '太咸', '分量少', '不卫生', '有虫子', '服务差', '慢']

        all_users = User.query.filter_by(role='user').all()
        all_dishes = Dish.query.all()

        for _ in range(100): # 100 historical orders
            user = random.choice(all_users)
            dish = random.choice(all_dishes)
            
            # Create Order
            order = Order(
                user_id=user.id,
                shop_id=dish.shop_id,
                total_price=dish.price,
                status='completed',
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                dish_id=dish.id,
                count=1,
                price_snapshot=dish.price
            )
            db.session.add(item)

            # Create Review (80% positive, 20% negative)
            if random.random() < 0.8:
                score = random.randint(4, 5)
                content = random.choice(pos_words) + "，" + random.choice(pos_words)
            else:
                score = random.randint(1, 3)
                content = random.choice(neg_words) + "，" + random.choice(neg_words)
            
            review = Review(
                user_id=user.id,
                order_id=order.id,
                dish_id=dish.id,
                shop_id=dish.shop_id,
                score=score,
                content=content,
                created_at=order.created_at + timedelta(hours=2)
            )
            db.session.add(review)

        db.session.commit()
        print("Mock Orders and Reviews created.")
        print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
