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

    const orderData = {
      items: this.data.cart,
      total: parseFloat(this.data.totalPrice)
    };

    request('/api/order/create', 'POST', orderData)
      .then(res => {
        this.finishPay();
      })
      .catch(err => {
        wx.hideLoading();
        console.error("Pay failed", err);
        // 如果是演示环境，可以在这里选择是否继续走假成功
        // 但为了排查问题，这里提示错误
        wx.showModal({
          title: '支付请求失败',
          content: '无法连接后端，是否使用模拟支付完成流程？(数据库不会更新)',
          success: (res) => {
            if (res.confirm) {
              this.finishPay();
            }
          }
        });
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
