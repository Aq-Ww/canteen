import pandas as pd
import jieba
from collections import Counter
from datetime import datetime, timedelta
import random
from models import Review, Order, db
from sqlalchemy import func

class AnalysisService:
    @staticmethod
    def analyze_sentiment(shop_id):
        """
        对指定店铺评价进行情感分析和词云生成
        """
        reviews = Review.query.filter_by(shop_id=shop_id).all()
        if not reviews:
            return {
                "sentiment": {"positive_ratio": 100, "negative_ratio": 0},
                "keywords": []
            }
            
        # 1. 情感占比分析 (基于数据库已存储的sentiment字段，或者实时简单规则)
        # 这里假设 sentiment 字段在存入时已由 create_review 处理，或者我们这里模拟统计
        # 模拟：score >= 4 positive, < 4 negative
        
        positive_count = sum(1 for r in reviews if r.score >= 4)
        total = len(reviews)
        pos_ratio = int((positive_count / total) * 100)
        neg_ratio = 100 - pos_ratio
        
        # 2. 关键词提取 (Jieba分词)
        all_text = " ".join([r.content for r in reviews if r.content])
        words = jieba.cut(all_text)
        
        # 停用词过滤 (简单列表)
        stop_words = {'的', '了', '是', '我', '都', '很', '也', '在', '吃', '去', '有', '不', '人', '这', '吗'}
        filtered_words = [w for w in words if len(w) > 1 and w not in stop_words]
        
        word_counts = Counter(filtered_words)
        
        # 生成词云格式数据
        keywords = []
        colors = ['#ff9800', '#52c41a', '#1890ff', '#ff4d4f', '#999']
        for word, count in word_counts.most_common(20):
            keywords.append({
                "word": word,
                "weight": count,
                "color": random.choice(colors)
            })
            
        return {
            "sentiment": {
                "positive_ratio": pos_ratio,
                "negative_ratio": neg_ratio
            },
            "keywords": keywords
        }

    @staticmethod
    def predict_sales():
        """
        销量预测：基于历史7天数据预测未来3天
        使用 Pandas 简单移动平均或线性趋势
        """
        # 模拟生成近7天数据 (实际应从Order查询 group by date)
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]
        
        # 模拟真实销量波动
        base_sales = 100
        history_values = [base_sales + random.randint(-20, 50) for _ in range(7)]
        
        sales_history = [{"date": d, "value": v} for d, v in zip(dates, history_values)]
        
        # 简单趋势预测：取后3天平均值 * 增长系数
        avg_last_3 = sum(history_values[-3:]) / 3
        trend = (history_values[-1] - history_values[0]) / 7 # 简单斜率
        
        future_predictions = []
        for i in range(1, 4):
            future_date = (today + timedelta(days=i)).strftime('%m-%d')
            pred_val = int(avg_last_3 + trend * i + random.randint(-5, 5))
            future_predictions.append({"date": future_date, "value": max(0, pred_val)})
            
        return {
            "salesHistory": sales_history,
            "predictions": future_predictions
        }

    @staticmethod
    def cluster_negative_reviews():
        """
        差评聚类分析
        """
        # 获取所有低分评价
        low_score_reviews = Review.query.filter(Review.score <= 3).all()
        
        # 定义常见差评主题关键词
        topics = {
            "口味问题": ["难吃", "咸", "淡", "生", "凉", "腥", "味道"],
            "分量问题": ["少", "不够", "小", "吃不饱"],
            "卫生问题": ["虫", "头发", "脏", "异物", "不卫生"],
            "服务问题": ["慢", "态度", "凶", "等", "排队"]
        }
        
        topic_counts = {k: 0 for k in topics}
        topic_examples = {k: [] for k in topics}
        
        for r in low_score_reviews:
            content = r.content
            matched = False
            for topic, keywords in topics.items():
                if any(k in content for k in keywords):
                    topic_counts[topic] += 1
                    if len(topic_examples[topic]) < 1: # 只留一个典型案例
                        topic_examples[topic].append(content)
                    matched = True
            if not matched:
                # 归类为其他
                pass

        total_issues = sum(topic_counts.values()) or 1
        
        clusters = []
        for topic, count in topic_counts.items():
            if count > 0:
                clusters.append({
                    "topic": topic,
                    "ratio": int((count / total_issues) * 100),
                    "example": topic_examples[topic][0] if topic_examples[topic] else "暂无具体描述"
                })
                
        # 按占比排序
        clusters.sort(key=lambda x: x['ratio'], reverse=True)
        
        return clusters
