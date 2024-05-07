import { Card, Menu } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import getDomainURL from 'utils/api'

import './index.scss'

const mockX = (roomX=10) => {
  let X = [];
  let i = 0;
  while (i < roomX) {
    // X.push(i.toFixed(1));
    X.push(i.toFixed(1));
    // i += 0.01;
    i += 0.1;
  }
  return X
}

const mockY = (roomY=10) => {
  let Y = [];
  let j = 0;
  while (j < roomY) {
    // Y.push(j.toFixed(1));
    Y.push(j.toFixed(1));
    // j += 0.01;
    j += 0.1;
  }
  return Y
}

const RealtimeLocation = (props) => {
  const [option, setOption] = useState({
    tooltip: {
      show: true,
      trigger: 'item',
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
    },
    grid: {
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
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
        min: 10,
        max: 10,
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
        max: 10,
      },
    ],
    animation: false,
  })
  const chartRef = useRef(null);

  useEffect(() => {
    const chartInstance = chartRef.current.getEchartsInstance();

    const setGraphicImageSize = () => {
      const chartWidth = chartInstance.getWidth();
      const chartHeight = chartInstance.getHeight();
      
      if (chartWidth && props.room) {

        const imageUrl = getDomainURL() + `/static/uploads/` + props.room.IMAGE_NAME;

        const graphicImage = {
          id: 'bg',
          type: 'image',
          style: {
            image: imageUrl,
            x: 0,
            y: 0,
            width: chartWidth,
            height: chartHeight,
          },
        };
        
        let tempOption = {
          graphic: [graphicImage],
          xAxis: [
            {
              min: 0,
              max: props.room.ROOM_X,
            },
          ],
          yAxis: [
            {
              min: 0,
              max: props.room.ROOM_Y,
            },
          ],
        }

        tempOption.series = props.sensors.concat(props.persons)
        
        chartInstance.setOption(tempOption);
      }
    };

    // Call the function initially
    setGraphicImageSize();

    // Attach a listener for window resize to adjust the image size
    window.addEventListener('resize', setGraphicImageSize);

    // Cleanup the listener on component unmount
    return () => {
      window.removeEventListener('resize', setGraphicImageSize);
    };
  }, [props.room,props.data,props.sensors,props.persons]);

  return (
    <Card 
      title="Realtime Location" 
      style={{ height: "100%"}} 
      className='content-card'
    >
      
      <ReactECharts option={option} ref={chartRef}/>
      {
        props.room_empty?
          <div id="empty-lable" style={{
            position: 'absolute',
            top: '40%',
            left: '40%',
            fontSize: '-webkit-xxx-large',
            color: 'coral',
          }}>Empty</div>:
          <div className="legend" id="status-label">
            <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#080808'}}></div>
                <div className="legend-label">None</div>
            </div>
            <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#f8fc03'}}></div>
                <div className="legend-label">Moving</div>
            </div>
            <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#0918e3'}}></div>
                <div className="legend-label">Upright</div>
            </div>
            <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#8d61be'}}></div>
                <div className="legend-label">Laying</div>
            </div>
            <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#fc0303'}}></div>
                <div className="legend-label">Fall</div>
            </div>
            <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#20fc03'}}></div>
                <div className="legend-label">Social</div>
            </div>
        </div>
      }
      
    </Card>
  );
};

export default RealtimeLocation;