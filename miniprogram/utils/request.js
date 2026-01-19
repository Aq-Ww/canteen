const app = getApp();

/**
 * Unified Request Handler
 * @param {string} url - API Endpoint
 * @param {string} method - GET/POST
 * @param {object} data - Payload
 */
const request = (url, method = 'GET', data = {}) => {
  const fullUrl = 'http://127.0.0.1:5000' + url; // Hardcoded here or access getApp().globalData.baseUrl if possible
  
  return new Promise((resolve, reject) => {
    wx.showLoading({ title: 'Loading...' });
    
    wx.request({
      url: fullUrl,
      method: method,
      data: data,
      header: {
        'content-type': 'application/json',
        'Authorization': wx.getStorageSync('token') || ''
      },
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          wx.showToast({
            title: 'Error: ' + res.statusCode,
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: 'Network Error',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

module.exports = {
  request
};
