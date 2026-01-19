// pages/canteen/orders/orders.js
const { request } = require('../../../utils/request.js');

Page({
  data: {
    currentTab: 'pending',
    orders: []
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
      { id: '1001', time: '12:01', totalPrice: 25, status: 'pending', items: [{name: '红烧肉', count: 1}] },
      { id: '1002', time: '12:05', totalPrice: 15, status: 'processing', items: [{name: '青椒肉丝', count: 1}] },
      { id: '1003', time: '11:50', totalPrice: 30, status: 'completed', items: [{name: '水煮鱼', count: 1}] }
    ];
    
    const filtered = mockOrders.filter(o => o.status === this.data.currentTab);
    this.setData({ orders: filtered });

    // Real API
    /*
    request('/api/canteen/orders?status=' + this.data.currentTab).then(res => {
      this.setData({ orders: res.data });
    });
    */
  },

  updateStatus(e) {
    const id = e.currentTarget.dataset.id;
    const status = e.currentTarget.dataset.status;

    wx.showLoading({ title: 'Processing...' });
    
    // Mock Update
    setTimeout(() => {
      wx.hideLoading();
      wx.showToast({ title: 'Updated' });
      this.fetchOrders(); // Refresh (in mock, this won't change data unless we modify mockOrders globally, but good enough for demo logic)
    }, 500);

    /*
    request('/api/canteen/order/update', 'POST', { id, status }).then(() => {
      this.fetchOrders();
    });
    */
  }
});
