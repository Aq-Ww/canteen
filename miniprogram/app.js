// app.js
App({
  onLaunch() {
    // Check login status
    const token = wx.getStorageSync('token');
    if (!token) {
      // wx.reLaunch({ url: '/pages/login/login' }) // Usually handled in page onLoad or generic guard
    }
  },
  globalData: {
    userInfo: null,
    baseUrl: 'http://127.0.0.1:5000', // Python Backend URL
    cart: [] // Global cart: [{shopId, dishId, name, price, count, pic}]
  }
})
