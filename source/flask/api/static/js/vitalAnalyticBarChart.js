var vitalchartDom = document.getElementById("vitalChart");
var vitalChart = echarts.init(vitalchartDom);
var optionLine;
var today = new Date();
var dd = String(today.getDate()).padStart(2, "0");
var mm = String(today.getMonth() + 1).padStart(2, "0"); //January is 0!
var yyyy = today.getFullYear();

var app = {};

window.addEventListener('resize', function(){
  vitalChart.resize()
})

function gen2STime() {
  let now = new Date();
  let res = [];
  let len = 100;
  while (len--) {
    res.unshift(now.toLocaleTimeString().replace(/^\D*/, ""));
    now = new Date(+now - 2000);
  }
  return res;
}
const categories2 = (function () {
  let res = [];
  let len = 100;
  while (len--) {
    res.push(100 - len - 1);
  }
  return res;
})();
var vitalData = randR()
var vitalData2 = randR()
var categories = gen2STime()
function randR() {
  let res = [];
  let len = 0;
  while (len < 100) {
    // res.push(+(Math.random() * 2).toFixed(1));
    res.push({value: 0, itemStyle: { color: brightOrange}});
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
      min: 100,
      max: 0,
    },
    {
      show: false,
      type: "continuous",
      seriesIndex: 1,
      min: 25,
      max: 0,
    },
  ],
  // title: {
  //   text: 'Detected Data'
  // },
  title: [
    {
      left: "center",
    //   text: "Heart rate: 0",
    },
    {
      top: "50%",
      left: "center",
    //   text: "Breath rate: 0",
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
    show: false,
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
        show: false,
        // lineStyle: {
        //   type: "dashed",
        // },
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
        show: false,
        // lineStyle: {
        //   type: "dashed",
        // },
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
    //   name: "Heart Waveform",
      max: 100,
      min: 0,
      boundaryGap: [0.2, 0.2],
      splitLine: {
        show: false,
        // lineStyle: {
        //   type: "dashed",
        // },
      },
    },
    {
      axisLine: {
        show: false,
      },
      type: "value",
      scale: true,
    //   name: "Breath Waveform",
      max: 25,
      min: 0,
      boundaryGap: [0.2, 0.2],
      gridIndex: 1,
      splitLine: {
        show: false,
        // lineStyle: {
        //   type: "dashed",
        // },
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
  dataZoom: [
    {
      top: "50%",
      start: 0,
      end: 100,
      xAxisIndex: [0, 1],
      textStyle: {
        color: "#fff"
      }
    },
    // {
    //   start: 90,
    //   end: 100,
    //   xAxisIndex: [1],
    //   textStyle: {
    //     color: "#fff"
    //   }
    // },
  ],
  series: [
    {
      name: "Heart Waveform",
      type: "bar",
      smooth: true,
      emphasis: {
        focus: "series",
      },
      data: vitalData,
      // markLine: {
      //   silent: true,
      //   lineStyle: {
      //     color: '#fff'
      //   },
      //   data: [
      //     {
      //       yAxis: 60
      //     },
      //     {
      //       yAxis: 100
      //     }
      //   ]
      // }
    },
    {
      name: "Breath Waveform",
      type: "bar",
      smooth: true,
      emphasis: {
        focus: "series",
      },
      data: vitalData2,
      xAxisIndex: 1,
      yAxisIndex: 1,
      // markLine: {
      //   silent: true,
      //   lineStyle: {
      //     color: '#fff'
      //   },
      //   data: [
      //     {
      //       yAxis: 12
      //     },
      //     {
      //       yAxis: 20
      //     }
      //   ]
      // }
    }    
  ],
};

optionLine && vitalChart.setOption(optionLine);
