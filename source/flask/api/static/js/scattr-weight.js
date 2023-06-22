var chartDomWeight = document.getElementById("Scatter");
var scatterWeight = echarts.init(chartDomWeight);
var dashCircleFill = 'path://M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7z'
var arrowUpCircleFill = 'path://M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V11.5z'
var arrowRightCircleFill = 'path://M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V11.5z'
var arrowLeftCircleFill = 'path://M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 7.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z'
var arrowDownCircleFill = 'path://M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v5.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V4.5z'
var arrowDownLeftCircleFill = "path://M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-5.904-2.803a.5.5 0 1 1 .707.707L6.707 10h2.768a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5V6.525a.5.5 0 0 1 1 0v2.768l4.096-4.096z"
var arrowDownRightCircleFill = 'path://M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm5.904-2.803a.5.5 0 1 0-.707.707L9.293 10H6.525a.5.5 0 0 0 0 1H10.5a.5.5 0 0 0 .5-.5V6.525a.5.5 0 0 0-1 0v2.768L5.904 5.197z'
var arrowUpLeftCircleFill = 'path://M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-5.904 2.803a.5.5 0 1 0 .707-.707L6.707 6h2.768a.5.5 0 1 0 0-1H5.5a.5.5 0 0 0-.5.5v3.975a.5.5 0 0 0 1 0V6.707l4.096 4.096z'
var arrowUpRightCircleFill = 'path://M0 8a8 8 0 1 0 16 0A8 8 0 0 0 0 8zm5.904 2.803a.5.5 0 1 1-.707-.707L9.293 6H6.525a.5.5 0 1 1 0-1H10.5a.5.5 0 0 1 .5.5v3.975a.5.5 0 0 1-1 0V6.707l-4.096 4.096z'
var defaultSymbol = "pin"
var option;

let radarX = 0;
let radarY = 0;
let radarZ = 0;
let roomX = 5;
let roomY = 5;

window.addEventListener('resize', function(){
  scatterWeight.resize()
})

option = {
  // graphic:[{
  //   type: 'image',
  //   style: {
  //     image: '/static/images/Room1.png',
  //     x: rect.x,
  //     y: rect.y
  //   }
  // }],
  textStyle: {
    color: "#fff",
  },
  title: {
    text: "Real-time location",
    // subtext: 'Data from: Heinz 2003'
  },
  grid: {
    left: "3%",
    right: "7%",
    bottom: "7%",
    containLabel: true,
  },
  tooltip: {
    // trigger: 'axis',
    showDelay: 0,
    formatter: function (params) {
      if (params.value.length > 1) {
        return (
          params.seriesName +
          " :<br/>" +
          params.value[0] +
          "m " +
          params.value[1] +
          "m "
        );
      } else {
        return (
          params.seriesName +
          " :<br/>" +
          params.name +
          " : " +
          params.value +
          "m "
        );
      }
    },
    axisPointer: {
      show: true,
      type: "cross",
      lineStyle: {
        type: "dashed",
        width: 1,
      },
    },
  },
  toolbox: {
    feature: {
      dataZoom: {},
      brush: {
        type: ["rect", "polygon", "clear"],
      },
    },
  },
  brush: {},
  legend: {
    data: ["Radar", "Person 1"],
    left: "left",
    // bottom: 10
    top: 30,
    left: 50,
  },
  xAxis: [
    {
      type: "value",
      axisLine: {
        show: false,
      },
      scale: true,
      axisLabel: {
        formatter: "{value} m",
      },
      min: -roomX,
      max: roomX,
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
      type: "value",
      axisLine: {
        show: false,
      },
      scale: true,
      axisLabel: {
        formatter: "{value} m",
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: "dashed",
        },
      },
      min: 0,
      max: roomY,
    },
  ],
  animation: false,
  series: [
    {
      name: "Radar",
      type: "scatter",
      emphasis: {
        focus: "series",
      },
      data: [[radarX, radarY]],
      symbol: "diamond",
      symbolSize: 30,
      // markArea: {
      //   silent: true,
      //   data: [
      //     [
      //       {
      //         name: "Radar",
      //         xAxis: "min",
      //         yAxis: "min",
      //       },
      //       {
      //         xAxis: "max",
      //         yAxis: "max",
      //       },
      //     ],
      //   ],
      // },
      // markPoint: {
      //   data: [
      //     { type: "max", name: "" },
      //     { type: "min", name: "" },
      //   ],
      //   symbol: "diamond",
      //   symbolSize: 30,
      // },
    },
    {
      name: "Person 1",
      type: "scatter",
      emphasis: {
        focus: "series",
      },
      // prettier-ignore
      // data: [[3.2, 1.6], [1.5, 2.0], [2.5, 2.2], [1.0, 1.3], [1.8, 2.6]],
      data: [],
      // markArea: {
      //   silent: true,
      //   itemStyle: {
      //     color: "transparent",
      //     borderWidth: 1,
      //     borderType: "dashed",
      //   },
      //   data: [
      //     [
      //       {
      //         name: "Person 1",
      //         xAxis: "min",
      //         yAxis: "min",
      //       },
      //       {
      //         xAxis: "max",
      //         yAxis: "max",
      //       },
      //     ],
      //   ],
      // },
      // markPoint: {
      //   // data: [
      //   //   { type: "max", name: "Max" },
      //   //   { type: "min", name: "Min" },
      //   // ],
      //   symbol: defaultSymbol,
      //   symbolSize: 50,
      // },
      // markLine: {
      //   lineStyle: {
      //     type: "solid",
      //   },
      //   // data: [{ type: 'average', name: 'AVG' }, { xAxis: 160 }]
      // },
    },
    // {
    //   name: 'Person 2',
    //   type: 'scatter',
    //   emphasis: {
    //     focus: 'series'
    //   },
    //   // prettier-ignore
    //   data: [[-1.0, 2.6], [-1.3, 1.8], [-1.5, 0.7], [-1.5, 2.6], [-1.2, -0.8]],
    //   markArea: {
    //     silent: true,
    //     itemStyle: {
    //       color: 'transparent',
    //       borderWidth: 1,
    //       borderType: 'dashed'
    //     },
    //     data: [
    //       [
    //         {
    //           name: 'Person 2 Data Range',
    //           xAxis: 'min',
    //           yAxis: 'min'
    //         },
    //         {
    //           xAxis: 'max',
    //           yAxis: 'max'
    //         }
    //       ]
    //     ]
    //   },
    //   markPoint: {
    //     data: [
    //       { type: 'max', name: 'Max' },
    //       { type: 'min', name: 'Min' }
    //     ]
    //   },
    //   markLine: {
    //     lineStyle: {
    //       type: 'solid'
    //     },
    //     // data: [{ type: 'average', name: 'Average' }, { xAxis: 170 }]
    //   }
    // }
  ],
};

option && scatterWeight.setOption(option);


