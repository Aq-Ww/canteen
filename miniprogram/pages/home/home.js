// pages/home/home.js
const { request } = require('../../utils/request.js');

Page({
  data: {
    recommendations: [],
    shops: []
  },

  onLoad() {
    this.fetchData();
  },

  fetchData() {
    this.fetchRecommendations();
    this.fetchShops();
  },

  fetchRecommendations() {
    // 获取用户ID
    const userId = wx.getStorageSync('userId') || 1;
    // Fetch Recommendations with user ID
    return request(`/api/recommendations?userId=${userId}`)
      .then(res => {
        this.setData({ recommendations: res.data || [] });
      })
      .catch(() => {
        // Remove mock data, use empty array instead
        this.setData({ recommendations: [] });
      });
  },

  fetchShops() {
    // Fetch Shops
    return request('/api/shops')
      .then(res => {
        this.setData({ shops: res.data || [] });
      })
      .catch(() => {
        // Remove mock data, use empty array instead
        this.setData({ shops: [] });
      });
  },

  goToDish(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/dish/dish?id=${id}` });
  },

  goToShop(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/shop/shop?id=${id}` });
  }
});
