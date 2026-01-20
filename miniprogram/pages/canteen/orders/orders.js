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
    request('/api/canteen/orders?status=' + this.data.currentTab)
      .then(res => {
        this.setData({ orders: res.data || [] });
      })
      .catch(err => {
        console.error("Fetch admin orders failed", err);
        // Fallback to Mock Data
        const mockOrders = [
          { id: '1001', time: '12:01', totalPrice: 25, status: 'pending', items: [{name: '示例-红烧肉', count: 1}] },
          { id: '1002', time: '12:05', totalPrice: 15, status: 'processing', items: [{name: '示例-青椒肉丝', count: 1}] }
        ];
        const filtered = mockOrders.filter(o => o.status === this.data.currentTab);
        this.setData({ orders: filtered });
      });
  },

  updateStatus(e) {
    const id = e.currentTarget.dataset.id;
    const status = e.currentTarget.dataset.status;

    wx.showLoading({ title: 'Processing...' });
    
    request('/api/canteen/order/update', 'POST', { id, status })
      .then(() => {
        wx.hideLoading();
        wx.showToast({ title: 'Updated' });
        this.fetchOrders();
      })
      .catch(err => {
        wx.hideLoading();
        wx.showToast({ title: 'Failed', icon: 'none' });
      });
  }
});
