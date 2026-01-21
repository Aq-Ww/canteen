import pandas as pd
import numpy as np
import random
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from models import Dish, Review, Shop, User, db
from sqlalchemy import func

class RecommendService:
    # 1. 定义各方面的标签关键词
    tag_categories = {
        '贵': ['贵', '价格高', '太贵', '很贵','有点贵' ,'不值','价格偏高','不算便宜','价格略高', '性价比有点低', '性价比低', '性价比差','性价比普通','性价比一般'],
        '不贵': ['不贵', '价格低','价格亲民' ,'良心','价格划算','值得','便宜','价格合理','价格便宜', '不昂贵', '价位低','性价比极高', '性价比高', '性价比之王','性价比不错'],
        '质量高': ['质量', '新鲜', '新鲜度', '优质', '干净', '卫生', '整洁'],
        '质量低': ['变质', '劣质', '脏', '不干净', '不卫生'],
        '排队快': ['快', '效率', '速度', '效率高', '速度快', '不排队', '无需等待'],
        '排队慢': ['慢', '久', '等待', '排队', '排队长', '等待久', '效率低'],
        '分量多': ['分量', '量', '多', '足', '够', '大', '充足'],
        '分量少': ['少', '不够', '小', '不足', '量少', '分量少'],
        '清淡': ['淡', '清淡', '没味道', '鲜美',  '甜'],
        '辛辣': ['辣', '咸', '口味重', '麻辣', '香辣','入味', '酸辣']
    }

    # 定义价格标签的归属关系：便宜和不算便宜仍然算在不贵和贵的大类别里
    price_tag_hierarchy = {
        '贵': ['贵', '不算便宜'],  # 不算便宜属于贵的大类
        '不贵': ['不贵', '便宜']  # 便宜属于不贵的大类
    }

    @staticmethod
    def extract_specific_tags(text, categories):
        text = str(text)
        # 提取各分类的标签
        tags = {}
        
        # 1. 先提取所有包含的关键词，不考虑类别
        all_matched_keywords = []
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    all_matched_keywords.append(keyword)
        
        # 2. 为每个关键词分配到正确的类别
        for category, keywords in categories.items():
            category_tags = []
            for keyword in all_matched_keywords:
                if keyword in keywords:
                    # 特殊处理：如果当前类别是"贵"，且关键词是"贵"，需要确保它不是"不贵"的一部分
                    if category == '贵' and keyword == '贵':
                        # 检查"贵"是否出现在"不贵"中
                        if '不贵' in text:
                            # 如果"不贵"在文本中，那么单独的"贵"可能是"不贵"的一部分，所以不添加
                            continue
                    category_tags.append(keyword)
            # 去重
            tags[category] = list(set(category_tags))
        
        # 3. 处理价格标签的归属关系：将细分标签的关键词添加到对应的大类标签中
        # 定义细分标签到大类标签的映射
        sub_to_main = {}
        for main_tag, sub_tags in RecommendService.price_tag_hierarchy.items():
            for sub_tag in sub_tags:
                if sub_tag != main_tag:  # 排除大类标签本身
                    sub_to_main[sub_tag] = main_tag
        
        # 将细分标签的关键词添加到大类标签中
        for sub_tag, main_tag in sub_to_main.items():
            if sub_tag in tags and tags[sub_tag]:
                # 将细分标签的关键词添加到大类标签中
                if main_tag in tags:
                    tags[main_tag] = list(set(tags[main_tag] + tags[sub_tag]))
                else:
                    tags[main_tag] = tags[sub_tag]
        
        return tags

    @staticmethod
    def aggregate_tags(tag_series):
        # 初始化聚合标签字典
        aggregated_tags = {category: [] for category in RecommendService.tag_categories.keys()}
        # 遍历所有评论的标签
        for tag_dict in tag_series:
            for category, tags in tag_dict.items():
                aggregated_tags[category].extend(tags)
        # 去重并排序
        for category in aggregated_tags:
            aggregated_tags[category] = sorted(list(set(aggregated_tags[category])))
        return aggregated_tags

    @staticmethod
    def extract_user_preferences(df):
        # 为每个用户提取评论过的菜品和标签
        user_reviews = df.groupby('用户ID').agg({
            '菜品名称': list,
            '评论内容': list,
            '评分': 'mean',
            '价格': 'mean'
        }).reset_index()
        
        # 为每个用户提取标签特征
        user_reviews['用户标签'] = user_reviews['评论内容'].apply(lambda x: [RecommendService.extract_specific_tags(str(text), RecommendService.tag_categories) for text in x])
        
        # 统计用户标签偏好
        def aggregate_user_tags(tag_list):
            tag_stats = {tag: 0 for tag in RecommendService.tag_categories.keys()}
            for tag_dict in tag_list:
                for tag, keywords in tag_dict.items():
                    if keywords:  # 如果有匹配的关键词
                        tag_stats[tag] += 1
            return tag_stats
        
        user_reviews['标签统计'] = user_reviews['用户标签'].apply(aggregate_user_tags)
        
        return user_reviews

    @staticmethod
    def cluster_users(user_reviews):
        # 构建用户特征矩阵
        user_features = pd.DataFrame()
        user_features['用户ID'] = user_reviews['用户ID']
        user_features['平均评分'] = user_reviews['评分']
        user_features['平均价格'] = user_reviews['价格']
        
        # 原文件中包含正向情感比例特征，但当前数据库没有情感标签字段，故省略
        # user_features['正向情感比例'] = user_reviews['情感标签']
        
        # 添加标签特征
        for tag in RecommendService.tag_categories.keys():
            user_features[tag] = user_reviews['标签统计'].apply(lambda x: x[tag])
        
        # 特征归一化
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(user_features.drop('用户ID', axis=1))
        
        # 用户聚类 - 与原文件保持一致，固定为5个聚类
        n_user_clusters = 5
        kmeans_users = KMeans(n_clusters=n_user_clusters, random_state=42)
        user_features['用户聚类标签'] = kmeans_users.fit_predict(scaled_features)
        
        return user_features

    @staticmethod
    def get_recommendations(user_id):
        """
        基于用户历史订单和评价的协同过滤/加权推荐
        1. 获取用户常点的菜品标签/店铺
        2. 获取高分菜品
        3. 混合推荐
        """
        try:
            print(f"Starting recommendation for user: {user_id}")
            
            # 1. 从数据库获取所有评论数据
            print("Fetching review data from database...")
            review_query = db.session.query(
                Review.id.label('评论ID'),
                Review.user_id.label('用户ID'),
                Review.content.label('评论内容'),
                Review.score.label('评分'),
                Review.created_at.label('评论时间'),
                Dish.id.label('菜品ID'),
                Dish.name.label('菜品名称'),
                Dish.price.label('价格'),
                Shop.id.label('店铺ID'),
                Shop.name.label('店铺名称')
            ).join(Dish, Review.dish_id == Dish.id).join(Shop, Dish.shop_id == Shop.id).all()
            
            print(f"Found {len(review_query)} reviews")
            
            if not review_query:
                # 如果没有评论数据，使用原有的基于热度的推荐
                print("No reviews found, using hot recommendations")
                return RecommendService.get_hot_recommendations()
            
            # 转换为DataFrame
            review_df = pd.DataFrame(review_query)
            print(f"Review DataFrame shape: {review_df.shape}")
            
            # 2. 为每个评论提取标签
            print("Extracting tags from reviews...")
            review_df['评论标签'] = review_df['评论内容'].apply(lambda x: RecommendService.extract_specific_tags(x, RecommendService.tag_categories))
            print(f"Reviews with tags shape: {review_df.shape}")
            
            # 3. 为每个菜品聚合标签
            print("Aggregating tags for dishes...")
            dish_tags = review_df.groupby('菜品名称').agg({
                '评论标签': RecommendService.aggregate_tags,
                '评分': 'mean',
                '价格': 'mean',
                '店铺名称': 'first',
                '菜品ID': 'first',
                '店铺ID': 'first'
            }).reset_index()
            print(f"Dish tags shape: {dish_tags.shape}")
            
            if dish_tags.empty:
                print("Dish tags is empty, using hot recommendations")
                return RecommendService.get_hot_recommendations()
            
            # 4. 提取标签特征用于聚类
            def extract_tag_features_for_clustering(tag_dict_series, categories):
                # 初始化特征DataFrame
                tag_features = pd.DataFrame()
                # 对每个标签类别，计算包含该类标签的评论比例
                for category in categories:
                    tag_features[f'{category}_数量'] = tag_dict_series.apply(lambda x: len(x[category]))
                return tag_features
            
            tag_features = extract_tag_features_for_clustering(dish_tags['评论标签'], RecommendService.tag_categories.keys())
            
            # 5. 合并基础特征和标签特征
            cluster_features = pd.concat([
                dish_tags[['评分', '价格']],
                tag_features
            ], axis=1)
            
            # 6. 特征归一化和聚类
            scaler = MinMaxScaler()
            scaled_features = scaler.fit_transform(cluster_features)
            
            n_clusters = min(10, len(dish_tags))  # 根据菜品数量调整，最多10个聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            dish_tags['聚类标签'] = kmeans.fit_predict(scaled_features)
            
            # 7. 提取用户偏好
            user_reviews = RecommendService.extract_user_preferences(review_df)
            
            if user_reviews.empty:
                return RecommendService.get_hot_recommendations()
            
            # 8. 用户聚类
            user_features = RecommendService.cluster_users(user_reviews)
            
            # 9. 基于用户ID的猜你喜欢推荐
            recommendations = RecommendService.generate_user_based_recommendations(user_id, user_features, dish_tags, review_df)
            
            # 10. 获取推荐菜品的完整信息
            if recommendations:
                # 检查返回格式
                if isinstance(recommendations, list) and recommendations:
                    # 如果返回的是完整的推荐对象列表
                    if 'id' in recommendations[0]:
                        # 直接使用返回的结果
                        result = recommendations[:5]  # 确保只返回5个
                        return result
                    # 如果返回的是菜品名称列表
                    elif isinstance(recommendations[0], dict) and '菜品ID' in recommendations[0]:
                        # 从返回结果中提取菜品ID
                        dish_ids = [rec['菜品ID'] for rec in recommendations[:5]]
                        recommended_dishes = Dish.query.filter(Dish.id.in_(dish_ids)).all()
                        
                        # 转换为API需要的格式
                        result = []
                        for dish in recommended_dishes:
                            result.append({
                                'id': dish.id,
                                'name': dish.name,
                                'price': dish.price,
                                'image': dish.image,
                                'score': dish.score,
                                'sales': dish.sales
                            })
                        
                        # 补充随机推荐确保至少5个
                        if len(result) < 5:
                            hot_recommendations = RecommendService.get_hot_recommendations()
                            # 去重
                            existing_ids = {d['id'] for d in result}
                            for dish in hot_recommendations:
                                if dish['id'] not in existing_ids:
                                    result.append(dish)
                                    if len(result) >= 5:
                                        break
                        
                        return result
            
            # 如果没有推荐结果，返回热度推荐的前5个
            hot_recommendations = RecommendService.get_hot_recommendations()
            return hot_recommendations[:5]
                
        except Exception as e:
            print(f"推荐算法出错: {str(e)}")
            # 出错时使用基于热度的推荐作为备选
            return RecommendService.get_hot_recommendations()

    @staticmethod
    def generate_user_based_recommendations(user_id, user_features, dish_tags, df):
        try:
            # 获取用户评论过的菜品
            user_dishes = df[df['用户ID'] == user_id]['菜品名称'].unique().tolist()
            
            # 1. 基于用户聚类的推荐（权重 0.4）
            user_cluster_recommendations = []
            try:
                user_cluster = user_features[user_features['用户ID'] == user_id]['用户聚类标签'].iloc[0]
                similar_users = user_features[user_features['用户聚类标签'] == user_cluster]['用户ID'].tolist()
                similar_users.remove(user_id) if user_id in similar_users else None
                
                if similar_users:
                    similar_user_dishes = df[df['用户ID'].isin(similar_users)]['菜品名称'].unique().tolist()
                    candidate_dishes = [dish for dish in similar_user_dishes if dish not in user_dishes]
                    
                    for dish in candidate_dishes:
                        dish_info = dish_tags[dish_tags['菜品名称'] == dish]
                        if not dish_info.empty:
                            dish_info = dish_info.iloc[0]
                            user_cluster_recommendations.append({
                                '菜品ID': dish_info['菜品ID'],
                                '菜品名称': dish,
                                '平均评分': dish_info['评分'],
                                '权重': 0.4 * dish_info['评分']
                            })
            except Exception as e:
                print(f"用户聚类推荐出错: {str(e)}")
            
            # 2. 基于历史行为的推荐（权重 0.35）
            historical_recommendations = []
            try:
                if user_dishes:
                    # 基于用户历史订单和评分
                    user_history = df[df['用户ID'] == user_id]
                    # 获取用户喜欢的菜品类目
                    favorite_categories = user_history.groupby('店铺名称')['评分'].mean().nlargest(3).index.tolist()
                    
                    # 推荐同类别但未尝试的菜品
                    for category in favorite_categories:
                        category_dishes = dish_tags[dish_tags['店铺名称'] == category]
                        category_dishes = category_dishes[~category_dishes['菜品名称'].isin(user_dishes)]
                        
                        for _, dish_info in category_dishes.iterrows():
                            historical_recommendations.append({
                                '菜品ID': dish_info['菜品ID'],
                                '菜品名称': dish_info['菜品名称'],
                                '平均评分': dish_info['评分'],
                                '权重': 0.35 * dish_info['评分']
                            })
            except Exception as e:
                print(f"历史行为推荐出错: {str(e)}")
            
            # 3. 基于菜品聚类的推荐（权重 0.25）
            dish_cluster_recommendations = []
            try:
                if user_dishes:
                    import random
                    sample_dish = random.choice(user_dishes)
                    dish_cluster = dish_tags[dish_tags['菜品名称'] == sample_dish]['聚类标签'].iloc[0]
                    
                    cluster_dishes = dish_tags[dish_tags['聚类标签'] == dish_cluster]
                    cluster_dishes = cluster_dishes[~cluster_dishes['菜品名称'].isin(user_dishes)]
                    
                    for _, dish_info in cluster_dishes.iterrows():
                        dish_cluster_recommendations.append({
                            '菜品ID': dish_info['菜品ID'],
                            '菜品名称': dish_info['菜品名称'],
                            '平均评分': dish_info['评分'],
                            '权重': 0.25 * dish_info['评分']
                        })
            except Exception as e:
                print(f"菜品聚类推荐出错: {str(e)}")
            
            # 4. 融合推荐结果
            all_recommendations = user_cluster_recommendations + historical_recommendations + dish_cluster_recommendations
            
            if not all_recommendations:
                # 如果没有推荐结果，使用评分最高的菜品
                top_rated = dish_tags.sort_values('评分', ascending=False).head(5)
                recommended_dish_ids = top_rated['菜品ID'].tolist()
            else:
                # 去重并计算综合权重
                dish_scores = {}
                for rec in all_recommendations:
                    dish_id = rec['菜品ID']
                    if dish_id not in dish_scores:
                        dish_scores[dish_id] = 0
                    dish_scores[dish_id] += rec['权重']
                
                # 按综合权重排序
                sorted_dishes = sorted(dish_scores.items(), key=lambda x: x[1], reverse=True)
                recommended_dish_ids = [dish_id for dish_id, _ in sorted_dishes[:5]]
            
            # 5. 查询完整的菜品信息
            if recommended_dish_ids:
                dish_query = db.session.query(Dish.id, Dish.name, Dish.price, Dish.image, Dish.score, Dish.sales).filter(Dish.id.in_(recommended_dish_ids)).all()
                if dish_query:
                    # 按推荐顺序排序
                    dish_dict = {dish.id: dish for dish in dish_query}
                    ordered_dishes = [dish_dict.get(dish_id) for dish_id in recommended_dish_ids if dish_id in dish_dict]
                    
                    # 转换为与热度推荐相同的格式
                    recommendations = []
                    for dish in ordered_dishes:
                        recommendations.append({
                            'id': dish.id,
                            'name': dish.name,
                            'price': dish.price,
                            'image': dish.image,
                            'score': dish.score,
                            'sales': dish.sales,
                            'weight': dish.score  # 使用评分作为权重
                        })
                    return recommendations
            
            # 如果获取菜品信息失败，使用热度推荐
            print("Failed to get recommended dishes, using hot recommendations")
            return RecommendService.get_hot_recommendations()
            
        except Exception as e:
            print(f"用户推荐出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 出错时使用热度推荐
            return RecommendService.get_hot_recommendations()

    @staticmethod
    def get_hot_recommendations():
        """
        基于热度的推荐作为备选方案
        """
        query = db.session.query(Dish.id, Dish.name, Dish.price, Dish.image, Dish.score, Dish.sales).all()
        if not query:
            return []
            
        df = pd.DataFrame(query, columns=['id', 'name', 'price', 'image', 'score', 'sales'])
        
        # 计算推荐权重：评分 * 0.7 + 归一化销量 * 0.3 + 随机扰动
        max_sales = df['sales'].max() if df['sales'].max() > 0 else 1
        df['weight'] = df['score'] * 0.7 + (df['sales'] / max_sales * 5) * 0.3
        
        # 加入一些随机性模拟"探索"
        df['weight'] += np.random.random(len(df)) * 0.5
        
        # 取前5名
        recommendations = df.nlargest(5, 'weight')
        
        return recommendations.to_dict('records')
