var linechartDom = document.getElementById("lineChart");
var lineChart = echarts.init(linechartDom);
var optionLine;
var today = new Date();
var dd = String(today.getDate()).padStart(2, "0");
var mm = String(today.getMonth() + 1).padStart(2, "0"); //January is 0!
var yyyy = today.getFullYear();

var app = {};

window.addEventListener('resize', function(){
  lineChart.resize()
})

const categories = (function () {
  let now = new Date();
  let res = [];
  let len = 15;
  while (len--) {
    res.unshift(now.toLocaleTimeString().replace(/^\D*/, ""));
    now = new Date(+now - 2000);
  }
  return res;
})();
const categories2 = (function () {
  let res = [];
  let len = 15;
  while (len--) {
    res.push(15 - len - 1);
  }
  return res;
})();
const data = (function () {
  let res = [];
  let len = 15;
  while (len--) {
    res.push(Math.round(Math.random() * 1000));
  }
  return res;
})();
// const data2 = (function () {
//   let res = [];
//   let len = 0;
//   while (len < 10) {
//     res.push(+(Math.random() * 2).toFixed(1));
//     len++;
//   }
//   return res;
// })();
// const data2 = randR()
// const data3 = randR()
const data2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
const data3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
function randR() {
  let res = [];
  let len = 0;
  while (len < 15) {
    res.push(+(Math.random() * 2).toFixed(1));
    len++;
  }
  return res;
}
optionLine = {
  textStyle: {
    color: "#fff",
  },
  // Make gradient line here
  visualMap: [
    {
      show: false,
      type: "continuous",
      seriesIndex: 0,
      min: 2,
      max: 0,
    },
    {
      show: false,
      type: "continuous",
      seriesIndex: 1,
      min: 2,
      max: 0,
    },
  ],
  // title: {
  //   text: 'Detected Data'
  // },
  title: [
    {
      left: "center",
      text: "Heart rate: 0",
    },
    {
      top: "50%",
      left: "center",
      text: "Breath rate: 0",
    },
  ],
  tooltip: {
    trigger: "axis",
    axisPointer: {
      type: "cross",
      label: {
        backgroundColor: "#283b56",
      },
    },
  },
  // legend: {},
  toolbox: {
    show: true,
    feature: {
      dataView: { readOnly: false },
      restore: {},
      saveAsImage: {},
    },
  },
  dataZoom: {
    show: false,
    start: 0,
    end: 100,
  },
  xAxis: [
    {
      axisLine: {
        show: false,
      },
      type: "category",
      boundaryGap: true,
      data: categories,
      splitLine: {
        show: true,
        lineStyle: {
          type: "dashed",
        },
      },
    },
    {
      axisLine: {
        show: false,
      },
      type: "category",
      boundaryGap: true,
      data: categories,
      gridIndex: 1,
      splitLine: {
        show: true,
        lineStyle: {
          type: "dashed",
        },
      },
    },
  ],
  yAxis: [
    {
      axisLine: {
        show: false,
      },
      type: "value",
      scale: true,
      name: "Heart Waveform",
      // max: 2,
      // min: -2,
      boundaryGap: [0.2, 0.2],
      splitLine: {
        show: true,
        lineStyle: {
          type: "dashed",
        },
      },
    },
    {
      axisLine: {
        show: false,
      },
      type: "value",
      scale: true,
      name: "Breath Waveform",
      // max: 2,
      // min: -2,
      boundaryGap: [0.2, 0.2],
      gridIndex: 1,
      splitLine: {
        show: true,
        lineStyle: {
          type: "dashed",
        },
      },
    },
  ],
  grid: [
    {
      bottom: "60%",
    },
    {
      top: "60%",
    },
  ],
  series: [
    {
      name: "Heart Waveform",
      type: "line",
      smooth: true,
      emphasis: {
        focus: "series",
      },
      data: data2,
    },
    {
      name: "Breath Waveform",
      type: "line",
      smooth: true,
      emphasis: {
        focus: "series",
      },
      data: data3,
      xAxisIndex: 1,
      yAxisIndex: 1,
    },
  ],
};
app.count = 11;
// setInterval(function () {
//     let axisData = new Date().toLocaleTimeString().replace(/^\D*/, '');
//     data2.shift();
//     data2.push(+(Math.random(2)).toFixed(1));
//     data3.shift();
//     data3.push(+(Math.random(2)).toFixed(1));
//     categories.shift();
//     categories.push(axisData);
//     lineChart.setOption({
//       xAxis: [
//         {
//           data: categories
//         },
//         {
//           data: categories,
//           gridIndex: 1
//         }
//       ],
//       series: [
//         {
//           data: data2
//         },
//         {
//           data: data3,
//           xAxisIndex: 1,
//           yAxis: 1
//         }
//       ]
//     });
// }, 2100);

optionLine && lineChart.setOption(optionLine);
