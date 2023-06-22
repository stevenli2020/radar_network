var vitalDom = document.getElementById("vitalAnalytic");
var vitalAnalyticChart = echarts.init(vitalDom);
var option;

let base = +new Date(1968, 9, 3);
let oneDay = 24 * 3600 * 1000;
let date = [];
let date2 = [];
let dataVital = [Math.random() * 300];
let dataVital2 = [Math.random() * 300];
for (let i = 1; i < 20000; i++) {
  var now = new Date((base += oneDay));
  date.push([now.getFullYear(), now.getMonth() + 1, now.getDate()].join("/"));
  date2.push([now.getFullYear(), now.getMonth() + 1, now.getDate()].join("/"));
  // dataVital.push(Math.round((Math.random() - 0.5) * 20 + dataVital[i - 1]));
  // dataVital2.push(Math.round((Math.random() - 0.5) * 20 + dataVital[i - 1]));
  dataVital.push(0);
  dataVital2.push(0);
}
window.addEventListener("resize", function () {
  vitalAnalyticChart.resize();
});
option = {
  textStyle: {
    color: "#fff",
  },
  tooltip: {
    trigger: "axis",
    position: function (pt) {
      return [pt[0], "10%"];
    },
  },
  title: [
    {
      left: "center",
      text: "Heart Rate",
    },
    {
      top: "50%",
      left: "center",
      text: "Breath Rate",
    },
  ],
  toolbox: {
    feature: {
      dataZoom: {
        yAxisIndex: "none",
      },
      restore: {},
      saveAsImage: {},
    },
  },
  xAxis: [
    {
      gridIndex: 0,
      axisLine: {
        show: false,
      },
      type: "category",
      boundaryGap: false,
      data: date,
    },
    {
      gridIndex: 1,
      axisLine: {
        show: false,
      },
      type: "category",
      boundaryGap: false,
      data: date2,
    },
  ],
  yAxis: [
    {
      gridIndex: 0,
      type: "value",
      boundaryGap: [0, "100%"],
    },
    {
      gridIndex: 1,
      type: "value",
      boundaryGap: [0, "100%"],
    },
  ],
  grid: [{ bottom: "60%" }, { top: "60%" }],
  dataZoom: [
    {
      top: "5%",
      start: 0,
      end: 10,
      xAxisIndex: [0],
    },
    {
      start: 0,
      end: 10,
      xAxisIndex: [1],
    },
  ],
  series: [
    {
      name: "Heart rate",
      type: "line",
      symbol: "none",
      sampling: "lttb",
      itemStyle: {
        color: "rgb(255, 70, 131)",
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {
            offset: 0,
            color: "rgb(255, 158, 68)",
          },
          {
            offset: 1,
            color: "rgb(255, 70, 131)",
          },
        ]),
      },
      data: dataVital,
      xAxisIndex: 0,
      yAxisIndex: 0,
    },
    {
      name: "Breath rate",
      type: "line",
      symbol: "none",
      sampling: "lttb",
      itemStyle: {
        color: "rgb(255, 70, 131)",
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {
            offset: 0,
            color: "rgb(255, 158, 68)",
          },
          {
            offset: 1,
            color: "rgb(255, 70, 131)",
          },
        ]),
      },
      data: dataVital2,
      xAxisIndex: 1,
      yAxisIndex: 1,
    },
  ],
};

option && vitalAnalyticChart.setOption(option);
