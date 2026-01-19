// pages/my_reviews/my_reviews.js
const { request } = require('../../utils/request.js');

Page({
  data: {
    reviews: []
  },

  onShow() {
    this.fetchReviews();
  },

  fetchReviews() {
    // Mock
    this.setData({
      reviews: [
        { id: 1, shopName: '第1食堂', score: 5, content: '好吃！', date: '2023-10-01' },
        { id: 2, shopName: '第2食堂', score: 3, content: '一般般', date: '2023-10-05' }
      ]
    });

    /*
    request('/api/my/reviews').then(res => {
      this.setData({ reviews: res.data });
    });
    */
  }
});
