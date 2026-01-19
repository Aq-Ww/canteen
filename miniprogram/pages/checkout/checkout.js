// pages/checkout/checkout.js
const app = getApp();
const { request } = require('../../utils/request.js');

Page({
  data: {
    cart: [],
    totalPrice: 0
  },

  onLoad() {
    const cart = app.globalData.cart || [];
    let total = 0;
    cart.forEach(item => total += item.price * item.count);
    this.setData({
      cart,
      totalPrice: total.toFixed(2)
    });
  },

  handlePay() {
    wx.showLoading({ title: '支付中...' });

    // Mock API Call
    request('/api/order/create', 'POST', { items: this.data.cart, total: this.data.totalPrice })
      .then(res => {
        this.finishPay();
      })
      .catch(() => {
        // Mock Success even if API fails
        setTimeout(() => {
          this.finishPay();
        }, 1500);
      });
  },

  finishPay() {
    wx.hideLoading();
    // Clear Cart
    app.globalData.cart = [];
    wx.navigateTo({
      url: '/pages/pay_result/pay_result?amount=' + this.data.totalPrice
    });
  }
});
