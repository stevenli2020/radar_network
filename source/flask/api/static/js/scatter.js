// import API_Call from "./utils";

var chartDom = document.getElementById('Scatter');
var scatter = echarts.init(chartDom);
var option;
x = [], y = [], input = []


// var timer = window.setInterval(async function() {
//   input = []
//   dataReq = await API_Call('real time', "IWR1642")
//   // console.log(dataReq)
//   if(dataReq["DATA"].length > 0){

//     xStr = dataReq["DATA"][0]["X"]
//     yStr = dataReq["DATA"][0]["Y"]
//     xStr = xStr.replace("[", "")
//     yStr = yStr.replace("[", "")
//     // 
//     xStr = xStr.split(",")
//     yStr = yStr.split(",")
//     // console.log(xStr, yStr)
//     // for(i=0; i < xStr.length && i<yStr.length; i++){
//     //   // console.log(parseFloat(xStr[i]), parseFloat(yStr[i]))
//     //   input[i] = [parseFloat(xStr[i]), parseFloat(yStr[i])]
//     // }
    
//     for ( var i = 0; i < xStr.length; i++ ){
//       // console.log(parseFloat(xStr[i]), parseFloat(yStr[i]))
//       input.push([parseFloat(xStr[i]), parseFloat(yStr[i])])
//     }
//     // console.log(input)
//     scatter.hideLoading()
//     scatter.setOption({
//       series: [
//         {
//           data: input
//         }
//       ]
//     })
//   }
// }, 60)


option = {
  xAxis: {},
  yAxis: {},
  // graphic: [{
  //   elements: [{
  //     id: 'radar',
  //     type: 'arc',
  //     $action: 'merge',
  //     x:-300,
  //     y:100,
  //     rotation: 0,
  //     // scaleX: 10,
  //     // scaleY: 10,
  //     // originX: 190,
  //     // originY: 265,
  //     // transition: ['x', 'y'],
  //     // left: 60,
  //     z: 100,
  //     z: 100,
  //     shape: {
  //       cx: 350,
  //       cy: 200,
  //       r: 200,
  //       // r0: 100,
  //       startAngle: 90,
  //       endAngle: 180,
  //       clockwise: true
  //     },
  //     style: {
  //       // fill: 'rgba(0, 140, 250, 0.5)',
  //       stroke: 'rgba(0, 50, 150, 0.5)',
  //       lineWidth: 2,
  //     }
  //   }]
  // }],
  series: [
    {
      symbolSize: 20,
      data: [
        [10.0, 8.04],
        [8.07, 6.95],
        [13.0, 7.58],
        [9.05, 8.81],
        [11.0, 8.33],
        [14.0, 7.66],
        [13.4, 6.81],
        [10.0, 6.33],
        [14.0, 8.96],
        [12.5, 6.82],
        [9.15, 7.2],
        [11.5, 7.2],
        [3.03, 4.23],
        [12.2, 7.83],
        [2.02, 4.47],
        [1.05, 3.33],
        [4.05, 4.96],
        [6.03, 7.24],
        [12.0, 6.26],
        [12.0, 8.84],
        [7.08, 5.82],
        [-5.02, 5.68],
        [-12.0, 6.26],
        [-12.0, 8.84],
        [-7.08, 5.82],
        [-5.02, 5.68]
      ],
      type: 'scatter'
    }
  ]
};

// scatter.showLoading();
option && scatter.setOption(option);