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
        if (!res.data) throw new Error("No data");
        this.setData({
          predictions: res.data.predictions || [],
          clusters: res.data.clusters || []
        });
        // 延迟绘制以确保节点就绪
        setTimeout(() => {
          this.drawChart(res.data.salesHistory || [], res.data.predictions || []);
        }, 200);
      })
      .catch(err => {
        console.error("Dashboard fetch failed", err);
        // Fallback to Mock Data
        const predictions = [
          { date: '1-13', value: 120 },
          { date: '1-14', value: 135 },
          { date: '1-15', value: 110 }
        ];
        const clusters = [
          { topic: '口味问题', ratio: 33, example: '今天的红烧肉太咸了，没法吃' },
          { topic: '服务问题', ratio: 32, example: '阿姨打饭太慢了，排队等了很久' },
          { topic: '分量问题', ratio: 17, example: '两口就没了，根本吃不饱' },
          { topic: '价格问题', ratio: 15, example: '价格有点贵，性价比不高' },
          { topic: '质量问题', ratio: 3, example: '饭菜里发现了异物，不卫生' }
        ];
        const salesHistory = [
          { date: '1-10', value: 100 },
          { date: '1-11', value: 110 },
          { date: '1-12', value: 125 }
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

        // Combine data to calculate max value
        const allData = [...history, ...predictions];
        const values = allData.map(d => d.value);
        const maxVal = Math.max(...values) * 1.2;

        const padding = 30;
        const chartW = width - padding * 2;
        const chartH = height - padding * 2;
        
        // Calculate stepX once for all uses
        const stepX = allData.length > 1 ? chartW / (allData.length - 1) : 0;
        
        // Draw Axes
        ctx.beginPath();
        ctx.strokeStyle = '#eee';
        ctx.lineWidth = 1;
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();

        // Draw Y-axis Labels (订单数量)
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'right';
        const ySteps = 5; // 5 steps on Y-axis
        for (let i = 0; i <= ySteps; i++) {
          const y = padding + (chartH / ySteps) * i;
          const value = Math.round(maxVal - (maxVal / ySteps) * i);
          
          // Draw grid line
          ctx.beginPath();
          ctx.strokeStyle = '#f0f0f0';
          ctx.lineWidth = 0.5;
          ctx.moveTo(padding, y);
          ctx.lineTo(width - padding, y);
          ctx.stroke();
          
          // Draw label
          ctx.fillText(value, padding - 5, y + 4);
        }

        // Draw History Line (solid line)
        if (history.length > 0) {
          ctx.beginPath();
          ctx.strokeStyle = '#007AFF'; // Blue for history
          ctx.lineWidth = 2;
          ctx.setLineDash([]); // Solid line
          
          history.forEach((d, i) => {
            const x = padding + i * stepX;
            const y = height - padding - (d.value / maxVal) * chartH;
            if (i === 0) {
              ctx.moveTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }
          });
          ctx.stroke();
        }

        // Draw Prediction Line (dashed line)
        if (predictions.length > 0) {
          ctx.beginPath();
          ctx.strokeStyle = '#ff4d4f'; // Red for predictions
          ctx.lineWidth = 2;
          ctx.setLineDash([5, 5]); // Dashed line
          
          const historyLength = history.length;
          
          predictions.forEach((d, i) => {
            const x = padding + (historyLength + i) * stepX;
            const y = height - padding - (d.value / maxVal) * chartH;
            if (i === 0) {
              // Start from the last history point
              const lastHistoryX = padding + (historyLength - 1) * stepX;
              const lastHistoryY = height - padding - (history[historyLength - 1].value / maxVal) * chartH;
              ctx.moveTo(lastHistoryX, lastHistoryY);
              ctx.lineTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }
          });
          ctx.stroke();
        }

        // Draw Points
        allData.forEach((d, i) => {
          const x = padding + i * stepX;
          const y = height - padding - (d.value / maxVal) * chartH;
          
          ctx.beginPath();
          ctx.fillStyle = i >= history.length ? '#ff4d4f' : '#007AFF'; // Red for prediction, blue for history
          ctx.arc(x, y, 3, 0, 2 * Math.PI);
          ctx.fill();
        });

        // Draw X-axis Date Labels
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        allData.forEach((d, i) => {
          const x = padding + i * stepX;
          const y = height - padding + 15; // Position below the x-axis
          ctx.fillText(d.date, x, y);
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
