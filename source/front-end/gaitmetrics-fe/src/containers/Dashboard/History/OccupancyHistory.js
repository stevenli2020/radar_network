import { Card, Menu } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';

const OccupancyHistory = (props) => {

  const chartRef = useRef(null);
  const [option,setOption] = useState({
    xAxis: {
        max: 100,
    },
    yAxis: {
        type: "category",
        data: ["Month", "Week", "Day", "Hour"],
    },
    legend: {
        data: ["In Bed", "In Room"],
    },
    series: [
        {
            name: "In Bed",
            type: "bar", // Specify the chart type
            label: {
                show: true,
                position: 'right',
                valueAnimation: true,
                formatter: '{c} %',
            },
            data: [0,0,0,0], // Replace with actual data
        },
        {
            name: "In Room",
            type: "bar", // Specify the chart type
            label: {
                show: true,
                position: 'right',
                valueAnimation: true,
                formatter: '{c} %',
            },
            data: [0,0,0,0], // Replace with actual data
        }
    ],
})

  useEffect(() => {
    const chartInstance = chartRef.current.getEchartsInstance();

    const setGraphicImageSize = () => {
      
      if (props.data) {
        
        let inBedPctHour = parseFloat(props.data.DATA[0]['IN_BED_PCT_HOUR']) >= 100 ? 100 : parseFloat(props.data.DATA[0]['IN_BED_PCT_HOUR'])
        let inRoomPctHour = parseFloat(props.data.DATA[0]['IN_ROOM_PCT_HOUR']) >= 100 ? 100 : parseFloat(props.data.DATA[0]['IN_ROOM_PCT_HOUR'])
        let inBedPctDay = parseFloat(props.data.DATA[0]['IN_BED_PCT_DAY']) >=90 ? 90 : parseFloat(props.data.DATA[0]['IN_BED_PCT_DAY'])
        let inRoomPctDay = parseFloat(props.data.DATA[0]['IN_ROOM_PCT_DAY']) >= 90 ? 90 : parseFloat(props.data.DATA[0]['IN_ROOM_PCT_DAY'])
        let inBedPctWeek = parseFloat(props.data.DATA[0]['IN_BED_PCT_WEEK']) >= 90 ? 90 : parseFloat(props.data.DATA[0]['IN_BED_PCT_WEEK'])
        let inRoomPctWeek = parseFloat(props.data.DATA[0]['IN_ROOM_PCT_WEEK']) >= 90 ? 90 : parseFloat(props.data.DATA[0]['IN_ROOM_PCT_WEEK'])
        let inBedPctMonth = parseFloat(props.data.DATA[0]['IN_BED_PCT_MONTH']) >= 90 ? 90 : parseFloat(props.data.DATA[0]['IN_BED_PCT_MONTH'])
        let inRoomPctMonth = parseFloat(props.data.DATA[0]['IN_ROOM_PCT_MONTH']) >= 90 ? 90 : parseFloat(props.data.DATA[0]['IN_ROOM_PCT_MONTH'])
        
        chartInstance.setOption({
          series: [
            {
              name: "In Bed",
              label: {
                show: true,
                position: 'right',
                valueAnimation: true,
                formatter: `{c} %`,
              },
              data: [inBedPctMonth, inBedPctWeek, inBedPctDay, inBedPctHour],
            },
            {
              name: "In Room",
              label: {
                show: true,
                position: 'right',
                valueAnimation: true,
                formatter: `{c} %`,
              },
              data: [inRoomPctMonth, inRoomPctWeek, inRoomPctDay, inRoomPctHour],
            }
          ],
        });
      }
    };

    setGraphicImageSize();
    window.addEventListener('resize', setGraphicImageSize);
    return () => {
      window.removeEventListener('resize', setGraphicImageSize);
    };
  }, [props.data]);

  return (
    <Card 
      title="Occupancy Status History" 
      style={{ height: "100%"}} 
      className='content-card'
      
    >
      {/* {
        props.option?<ReactECharts option={props.option}/>:<div style={{minHeight:'200px'}}/>
      } */}
      <ReactECharts style={{minHeight:400}} option={option} ref={chartRef} />
    </Card>
  );
};

export default OccupancyHistory;