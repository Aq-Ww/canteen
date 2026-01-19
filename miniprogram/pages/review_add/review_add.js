// pages/review_add/review_add.js
const { request } = require('../../utils/request.js');

Page({
  data: {
    orderId: '',
    shopName: '',
    score: 5,
    content: ''
  },

  onLoad(options) {
    this.setData({
      orderId: options.orderId,
      shopName: options.shopName
    });
  },

  setScore(e) {
    this.setData({ score: e.currentTarget.dataset.score });
  },

  onInputContent(e) {
    this.setData({ content: e.detail.value });
  },

  submitReview() {
    if (!this.data.content.trim()) {
      wx.showToast({ title: '写点评价吧', icon: 'none' });
      return;
    }

    request('/api/review', 'POST', {
      orderId: this.data.orderId,
      score: this.data.score,
      content: this.data.content
    }).then(() => {
      wx.showToast({ title: '评价成功' });
      setTimeout(() => wx.navigateBack(), 1500);
    }).catch(() => {
      // Mock Success
      wx.showToast({ title: '评价成功(Mock)' });
      setTimeout(() => wx.navigateBack(), 1500);
    });
  }
});
