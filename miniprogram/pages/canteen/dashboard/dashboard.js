// pages/canteen/dashboard/dashboard.js
const { request } = require('../../../utils/request.js');

Page({
  data: {
    predictions: [],
    clusters: []
  },

  onLoad() {
    this.fetchData();
  },

  fetchData() {
    request('/api/canteen/dashboard')
      .then(res => {
        this.setData({
          predictions: res.data.predictions,
          clusters: res.data.clusters
        });
        this.drawChart(res.data.salesHistory, res.data.predictions);
      })
      .catch(() => {
        // Mock Data
        const predictions = [
          { date: '1-20', value: 120 },
          { date: '1-21', value: 135 },
          { date: '1-22', value: 110 }
        ];
        const clusters = [
          { topic: '口味过咸', ratio: 45, example: '今天的红烧肉太咸了，没法吃' },
          { topic: '分量少', ratio: 30, example: '两口就没了，根本吃不饱' },
          { topic: '服务态度', ratio: 25, example: '阿姨打饭手抖' }
        ];
        const salesHistory = [
          { date: '1-15', value: 100 },
          { date: '1-16', value: 110 },
          { date: '1-17', value: 95 },
          { date: '1-18', value: 130 },
          { date: '1-19', value: 125 }
        ];

        this.setData({ predictions, clusters });
        // Use timeout to ensure canvas node is ready
        setTimeout(() => {
          this.drawChart(salesHistory, predictions);
        }, 100);
      });
  },

  drawChart(history, predictions) {
    const query = wx.createSelectorQuery();
    query.select('#salesChart')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res[0]) return;
        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');

        const dpr = wx.getSystemInfoSync().pixelRatio;
        canvas.width = res[0].width * dpr;
        canvas.height = res[0].height * dpr;
        ctx.scale(dpr, dpr);

        const width = res[0].width;
        const height = res[0].height;

        // Combine data
        const allData = [...history, ...predictions];
        const values = allData.map(d => d.value);
        const maxVal = Math.max(...values) * 1.2;

        const padding = 30;
        const chartW = width - padding * 2;
        const chartH = height - padding * 2;
        
        // Draw Axes
        ctx.beginPath();
        ctx.strokeStyle = '#eee';
        ctx.lineWidth = 1;
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();

        // Draw Line
        ctx.beginPath();
        ctx.strokeStyle = '#007AFF';
        ctx.lineWidth = 2;
        
        const stepX = chartW / (allData.length - 1);
        
        allData.forEach((d, i) => {
          const x = padding + i * stepX;
          const y = height - padding - (d.value / maxVal) * chartH;
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.stroke();

        // Draw Points
        allData.forEach((d, i) => {
          const x = padding + i * stepX;
          const y = height - padding - (d.value / maxVal) * chartH;
          
          ctx.beginPath();
          ctx.fillStyle = i >= history.length ? '#ff4d4f' : '#007AFF'; // Red for prediction
          ctx.arc(x, y, 3, 0, 2 * Math.PI);
          ctx.fill();
        });
      });
  },

  goOrders() {
    wx.navigateTo({ url: '/pages/canteen/orders/orders' });
  },

  goReviews() {
    wx.navigateTo({ url: '/pages/canteen/reviews/reviews' });
  }
});
