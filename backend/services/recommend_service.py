import pandas as pd
import numpy as np
import random
from models import Dish, Review, Shop, db
from sqlalchemy import func

class RecommendService:
    @staticmethod
    def get_recommendations(user_id):
        """
        基于用户历史订单和评价的协同过滤/加权推荐
        1. 获取用户常点的菜品标签/店铺
        2. 获取高分菜品
        3. 混合推荐
        """
        # 简单实现：获取全平台评分最高+销量最高的菜品作为"猜你喜欢"
        # 实际协同过滤需要构建 User-Item 矩阵，这里使用 pandas 模拟基于热度的加权推荐
        
        # 获取所有菜品数据
        query = db.session.query(Dish.id, Dish.name, Dish.price, Dish.image, Dish.score, Dish.sales).all()
        if not query:
            return []
            
        df = pd.DataFrame(query, columns=['id', 'name', 'price', 'image', 'score', 'sales'])
        
        # 计算推荐权重：评分 * 0.7 + 归一化销量 * 0.3 + 随机扰动
        max_sales = df['sales'].max() if df['sales'].max() > 0 else 1
        df['weight'] = df['score'] * 0.7 + (df['sales'] / max_sales * 5) * 0.3
        
        # 加入一些随机性模拟"探索"
        df['weight'] += np.random.random(len(df)) * 0.5
        
        # 取前8名
        recommendations = df.nlargest(8, 'weight')
        
        return recommendations.to_dict('records')
