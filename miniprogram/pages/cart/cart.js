// pages/cart/cart.js
const app = getApp();

Page({
  data: {
    cart: [],
    totalPrice: 0,
    totalCount: 0
  },

  onShow() {
    this.loadCart();
  },

  loadCart() {
    const cart = app.globalData.cart || [];
    let totalP = 0;
    let totalC = 0;
    
    cart.forEach(item => {
      totalP += item.price * item.count;
      totalC += item.count;
    });

    this.setData({
      cart: cart,
      totalPrice: totalP.toFixed(2),
      totalCount: totalC
    });
  },

  updateCount(e) {
    const index = e.currentTarget.dataset.index;
    const op = e.currentTarget.dataset.op;
    const cart = this.data.cart;

    if (op === '+') {
      cart[index].count++;
    } else {
      if (cart[index].count > 1) {
        cart[index].count--;
      } else {
        cart.splice(index, 1);
      }
    }

    app.globalData.cart = cart;
    this.loadCart();
  },

  goHome() {
    wx.switchTab({ url: '/pages/home/home' });
  },

  goCheckout() {
    if (this.data.cart.length === 0) return;
    wx.navigateTo({ url: '/pages/checkout/checkout' });
  }
});
