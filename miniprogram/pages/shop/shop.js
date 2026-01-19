// pages/shop/shop.js
const app = getApp();
const { request } = require('../../utils/request.js');

Page({
  data: {
    shopId: null,
    shop: {},
    menu: [],
    cartCounts: {}, // { dishId: count }
    totalCount: 0,
    totalPrice: 0
  },

  onLoad(options) {
    this.setData({ shopId: options.id });
    this.fetchShopData(options.id);
    this.syncCart();
  },

  onShow() {
    this.syncCart();
  },

  fetchShopData(id) {
    request(`/api/shop/${id}`)
      .then(res => {
        this.setData({ shop: res.data });
      })
      .catch(() => {
        // Mock Shop Data
        this.setData({
          shop: {
            id: id,
            name: `第${id}食堂`,
            score: 4.5,
            image: '',
            sentiment: { positive_ratio: 85, negative_ratio: 15 },
            keywords: [
              { word: '味道好', weight: 8, color: '#ff9800' },
              { word: '分量足', weight: 6, color: '#52c41a' },
              { word: '有点咸', weight: 3, color: '#999' },
              { word: '干净', weight: 7, color: '#1890ff' },
              { word: '阿姨手抖', weight: 5, color: '#ff4d4f' }
            ]
          }
        });
      });

    request(`/api/shop/${id}/menu`)
      .then(res => {
        this.setData({ menu: res.data });
      })
      .catch(() => {
        // Mock Menu
        this.setData({
          menu: [
            { id: 1, name: '招牌红烧肉', price: 18, sales: 200, image: '' },
            { id: 2, name: '土豆牛腩', price: 22, sales: 150, image: '' },
            { id: 3, name: '青椒肉丝', price: 15, sales: 300, image: '' },
            { id: 4, name: '番茄炒蛋', price: 8, sales: 500, image: '' }
          ]
        });
      });
  },

  addToCart(e) {
    const item = e.currentTarget.dataset.item;
    const cart = app.globalData.cart || [];
    const existing = cart.find(c => c.dishId === item.id && c.shopId === this.data.shopId);
    
    if (existing) {
      existing.count++;
    } else {
      cart.push({
        shopId: this.data.shopId,
        shopName: this.data.shop.name,
        dishId: item.id,
        name: item.name,
        price: item.price,
        count: 1,
        image: item.image
      });
    }
    app.globalData.cart = cart;
    this.syncCart();
  },

  removeFromCart(e) {
    const item = e.currentTarget.dataset.item;
    let cart = app.globalData.cart || [];
    const index = cart.findIndex(c => c.dishId === item.id && c.shopId === this.data.shopId);
    
    if (index > -1) {
      if (cart[index].count > 1) {
        cart[index].count--;
      } else {
        cart.splice(index, 1);
      }
    }
    app.globalData.cart = cart;
    this.syncCart();
  },

  syncCart() {
    const cart = app.globalData.cart || [];
    const counts = {};
    let totalC = 0;
    let totalP = 0;

    // Filter cart for current shop if you only want to show current shop's count in the list
    // But total bar usually shows global or shop specific. Let's assume shop specific for "Check out" in a canteen app often means ordering from one place.
    // However, if it's a canteen system, maybe we can order from multiple?
    // Let's stick to: The cart bar shows TOTAL cart value.
    // The +/- buttons show count for that dish.

    cart.forEach(c => {
      counts[c.dishId] = c.count; // Note: if same dish ID exists in other shops, this might be ambiguous. Assuming unique dish IDs or scoped by shop.
      // Better: counts[c.dishId] if we assume dishId is unique globally.
      totalC += c.count;
      totalP += c.count * c.price;
    });

    this.setData({
      cartCounts: counts,
      totalCount: totalC,
      totalPrice: totalP.toFixed(2)
    });
  },

  goToCart() {
    wx.switchTab({ url: '/pages/cart/cart' });
  },

  goToCheckout() {
    if (this.data.totalCount > 0) {
      wx.navigateTo({ url: '/pages/checkout/checkout' });
    }
  },

  goToDish(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/dish/dish?id=${id}` });
  }
});
