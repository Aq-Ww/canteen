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
    // Fetch Recommendations
    request('/api/recommendations')
      .then(res => {
        this.setData({ recommendations: res.data || [] });
      })
      .catch(() => {
        // Mock Data
        this.setData({
          recommendations: [
            { id: 101, name: '宫保鸡丁', price: 12, image: '' },
            { id: 102, name: '麻婆豆腐', price: 8, image: '' },
            { id: 103, name: '红烧肉', price: 25, image: '' },
            { id: 104, name: '清蒸鱼', price: 30, image: '' }
          ]
        });
      });

    // Fetch Shops
    request('/api/shops')
      .then(res => {
        this.setData({ shops: res.data || [] });
      })
      .catch(() => {
        // Mock Data for 11 Shops
        const mockShops = [];
        for (let i = 1; i <= 11; i++) {
          mockShops.push({
            id: i,
            name: `第${i}食堂`,
            score: (4 + Math.random()).toFixed(1),
            description: `这里是第${i}食堂的特色菜介绍`,
            reviewCount: Math.floor(Math.random() * 500)
          });
        }
        this.setData({ shops: mockShops });
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
