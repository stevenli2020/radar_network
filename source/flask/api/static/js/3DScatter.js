var ROOT_PATH = 'https://echarts.apache.org/examples';

var chartDom3d = document.getElementById('Scatter3D');
var scatter3d = echarts.init(chartDom3d);
var option3d;

// fetch('http://143.198.199.16:5000/static/js/data.json')
// .then((response) => response.json())
// .then((json) => {
//     console.log(json)
//     setData(json.data)
// });

window.addEventListener('resize', function(){
  scatter3d.resize()
})

setData([['x', 'y', 'z'], [0, 0, 0]])

function setData(d) {
    var symbolSize = 2.5;
    option3d = {
      grid3D: {},
      xAxis3D: {
        type: 'category',
        min: -6,
        max: 6
      },
      yAxis3D: {
        min: 0,
        max: 6
      },
      zAxis3D: {
        min: 0,
        max: 2
      },
      dataset: {
        // dimensions: [
        //   'Income',
        //   'Life Expectancy',
        //   'Population',
        //   'Country',
        //   { name: 'Year', type: 'ordinal' }
        // ],
        // source: d
        dimensions: [
          'x', 'y', 'z'
        ],
        source: d
      },
      series: [
        {
          type: 'scatter3D',
          symbolSize: 20,
          encode: {
            x: 'x',
            y: 'y',
            z: 'z',
            tooltip: [0, 1, 2, 3, 4]
          }
          // encode: {
          //   x: 'Country',
          //   y: 'Life Expectancy',
          //   z: 'Income',
          //   tooltip: [0, 1, 2, 3, 4]
          // }
        }
      ]
    };
    scatter3d.setOption(option3d);
  }

option3d && scatter3d.setOption(option3d);
