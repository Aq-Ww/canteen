// pages/login/login.js
const { request } = require('../../utils/request.js');

Page({
  data: {
    username: '',
    password: '',
    role: 'user' // user or admin
  },

  onInputUsername(e) {
    this.setData({ username: e.detail.value });
  },

  onInputPassword(e) {
    this.setData({ password: e.detail.value });
  },

  onRoleChange(e) {
    this.setData({ role: e.detail.value });
  },

  handleLogin() {
    const { username, password, role } = this.data;
    if (!username || !password) {
      wx.showToast({ title: '请输入账号密码', icon: 'none' });
      return;
    }

    // Call API
    request('/api/login', 'POST', { username, password, role })
      .then(res => {
        if (res.code === 0 || res.success) { // Adapt to common API formats
          wx.setStorageSync('token', res.data.token);
          wx.setStorageSync('userInfo', res.data.userInfo);
          wx.setStorageSync('role', role);

          wx.showToast({ title: '登录成功' });

          if (role === 'user') {
            wx.switchTab({ url: '/pages/home/home' });
          } else {
            // Canteen dashboard is not a tabbar page usually
            wx.reLaunch({ url: '/pages/canteen/dashboard/dashboard' });
          }
        } else {
          // Mock login for demo if API fails
          this.mockLogin(role);
        }
      })
      .catch(err => {
        // Fallback for demo
        this.mockLogin(role);
      });
  },

  mockLogin(role) {
    wx.setStorageSync('token', 'mock-token-123');
    wx.setStorageSync('role', role);
    wx.showToast({ title: '模拟登录成功' });
    setTimeout(() => {
      if (role === 'user') {
        wx.switchTab({ url: '/pages/home/home' });
      } else {
        wx.reLaunch({ url: '/pages/canteen/dashboard/dashboard' });
      }
    }, 1000);
  }
});
