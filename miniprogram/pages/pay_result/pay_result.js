// pages/pay_result/pay_result.js
Page({
  data: {
    amount: 0
  },

  onLoad(options) {
    this.setData({ amount: options.amount || 0 });
  },

  goOrders() {
    wx.switchTab({ url: '/pages/orders/orders' });
  },

  goHome() {
    wx.switchTab({ url: '/pages/home/home' });
  }
});
