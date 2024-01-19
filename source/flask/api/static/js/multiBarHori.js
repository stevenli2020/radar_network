var multiBarHoriDom = document.getElementById("multiBarHori");
var multiBarHoriChart = echarts.init(multiBarHoriDom);
var option;

window.addEventListener('resize', function(){
    multiBarHoriChart.resize()
  })

option = {
  textStyle: {
    color: "#000",
  },
  // title: {
  //   text: "History",
  // },
  tooltip: {
    trigger: "axis",
    axisPointer: {
      type: "shadow",
    },
    formatter: function (params) {
        // console.log(params)
        // return (
        //   params[0].name +
        //   " <br/>" +
        //   params[0].value +" %"          
        // )
        if(params.length > 1){
          return (
            params[0].name +
            " <br/>" +
            params[0].marker +" "+ params[0].seriesName + ": "+ params[0].value +
            " %<br/>" +
            params[1].marker +" "+ params[1].seriesName + ": "+ params[1].value +
            " %<br/>"
        )
          // return (
          //     params[0].name +
          //     " <br/>" +
          //     params[0].marker +" "+ params[0].seriesName + ": "+ params[0].value +
          //     " %<br/>" +
          //     params[1].marker +" "+ params[1].seriesName + ": "+ params[1].value +
          //     " %<br/>" +
          //     params[2].marker +" "+ params[2].seriesName + ": "+ params[2].value +
          //     "%"
          // )           
        }
    },
  },
  legend: {
    bottom: 5,
    textStyle: {
      color: "#000",
    }
  },
  // grid: {
  //   left: "3%",
  //   right: "4%",
  //   bottom: "3%",
  //   containLabel: true,
  // },
  xAxis: [{
    type: "value",
    boundaryGap: [0, 0.01],
    axisLine: {
      lineStyle: {
        color: "#000",
      }
    },
    splitLine: {
      show: false,
      lineStyle: {
        
        // color:["#fff"],
        // type: "dashed"
      }
    }
  }],
  yAxis: {
    type: "category",
    // data: ["Brazil", "Indonesia", "USA", "India", "China", "World"],
    data: ["Month", "Week", "Day", "Hour"],
    axisLine: {
      lineStyle: {
        color: "#000",
      }
    },
  },
  series: [
    {
      name: "In Bed",
      type: "bar",
      data: [0, 0, 0, 0],
      // data: [18203, 23489, 29034, 104970, 131744, 630230],
    },
    {
      name: "In Room",
      type: "bar",
      data: [0, 0, 0, 0],
    },
    // {
    //   name: "2012",
    //   type: "bar",
    //   data: [19325, 23438, 31000, 121594, 134141, 681807],
    // },
  ],
};

option && multiBarHoriChart.setOption(option);
