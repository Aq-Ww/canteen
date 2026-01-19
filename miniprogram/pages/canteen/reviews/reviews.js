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
    // Mock
    this.setData({
      reviews: [
        { id: 1, username: 'UserA', score: 5, content: '非常满意', date: '12:00' },
        { id: 2, username: 'UserB', score: 2, content: '太咸了', date: '11:30' }
      ]
    });
  }
});
