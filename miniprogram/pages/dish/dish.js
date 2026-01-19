// pages/dish/dish.js
const app = getApp();
const { request } = require('../../utils/request.js');

Page({
  data: {
    dishId: null,
    dish: {},
    reviews: []
  },

  onLoad(options) {
    this.setData({ dishId: options.id });
    this.fetchData(options.id);
  },

  fetchData(id) {
    request(`/api/dish/${id}`)
      .then(res => {
        this.setData({ 
          dish: res.data.dish,
          reviews: res.data.reviews 
        });
      })
      .catch(() => {
        // Mock Data
        this.setData({
          dish: {
            id: id,
            name: '示例菜品',
            price: 18,
            score: 4.8,
            sales: 1000,
            description: '这是一道非常美味的菜品，深受师生喜爱。'
          },
          reviews: [
            { id: 1, username: 'UserA', score: 5, content: '好吃！', date: '2023-10-01' },
            { id: 2, username: 'UserB', score: 4, content: '还不错，稍微有点咸', date: '2023-10-02' }
          ]
        });
      });
  },

  addToCart() {
    const item = this.data.dish;
    // We need shopId. Usually API returns shopId with dish, or we passed it in url.
    // For now, let's assume dish object has shopId or we mock it.
    const shopId = item.shopId || 1; // Default to 1 for mock

    const cart = app.globalData.cart || [];
    const existing = cart.find(c => c.dishId === item.id);
    
    if (existing) {
      existing.count++;
    } else {
      cart.push({
        shopId: shopId,
        shopName: 'Shop ' + shopId, // Mock
        dishId: item.id,
        name: item.name,
        price: item.price,
        count: 1,
        image: item.image
      });
    }
    app.globalData.cart = cart;
    wx.showToast({ title: '已加入购物车' });
  }
});
