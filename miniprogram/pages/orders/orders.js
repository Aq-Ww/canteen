// pages/orders/orders.js
const { request } = require('../../utils/request.js');

Page({
  data: {
    currentTab: 'all',
    orders: [],
    statusMap: {
      'pending': '待支付',
      'paid': '已支付',
      'completed': '已完成'
    }
  },

  onShow() {
    this.fetchOrders();
  },

  switchTab(e) {
    this.setData({ currentTab: e.currentTarget.dataset.tab }, () => {
      this.fetchOrders();
    });
  },

  fetchOrders() {
    // Mock Data
    const mockOrders = [
      {
        id: 'O001', shopName: '第1食堂', status: 'completed', totalPrice: 36, totalCount: 2,
        items: [{name: '红烧肉', count: 1}, {name: '米饭', count: 1}]
      },
      {
        id: 'O002', shopName: '第3食堂', status: 'paid', totalPrice: 15, totalCount: 1,
        items: [{name: '青椒肉丝盖饭', count: 1}]
      },
      {
        id: 'O003', shopName: '第2食堂', status: 'pending', totalPrice: 12, totalCount: 1,
        items: [{name: '宫保鸡丁', count: 1}]
      }
    ];

    let filtered = mockOrders;
    if (this.data.currentTab !== 'all') {
      filtered = mockOrders.filter(o => o.status === this.data.currentTab);
    }
    
    this.setData({ orders: filtered });

    // Real Request
    /*
    request('/api/orders?status=' + this.data.currentTab).then(res => {
      this.setData({ orders: res.data });
    });
    */
  },

  goReview(e) {
    const order = e.currentTarget.dataset.order;
    // Assuming reviewing the first item or the whole order. 
    // Requirement says: "Review purchased dishes".
    // Simple implementation: Review the Order (Shop).
    wx.navigateTo({
      url: `/pages/review_add/review_add?orderId=${order.id}&shopName=${order.shopName}`
    });
  }
});
