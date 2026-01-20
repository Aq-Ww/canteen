// pages/canteen/reviews/reviews.js
const { request } = require('../../../utils/request.js');

Page({
  data: {
    reviews: []
  },

  onLoad() {
    this.fetchReviews();
  },

  fetchReviews() {
    request('/api/canteen/reviews')
      .then(res => {
        this.setData({ reviews: res.data || [] });
      })
      .catch(err => {
        console.error("Fetch reviews failed", err);
        // Fallback to Mock Data
        this.setData({
          reviews: [
            { id: 1, username: 'Mock-User', score: 5, content: '后端未连接，显示模拟数据', date: '12:00' }
          ]
        });
      });
  }
});
