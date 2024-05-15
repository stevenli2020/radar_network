import { Button, Card, Menu, Popover, message } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import getDomainURL from 'utils/api'
import { useNavigate } from 'react-router-dom';

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

const LocationHistory = (props) => {

  const navigate = useNavigate()

  const handleOption = (item) => {
    if (item.key){
      if (props.macPos){
        props.action(props.macPos,item.key)
      }
    }else{
      if (dateRange[0] == null || dateRange[1] == null){
        message.error('Please select date range!!');
      }else{
        const fromDate = new Date(dateRange[0]);
        const fromyear = fromDate.getFullYear();
        const frommonth = String(fromDate.getMonth() + 1).padStart(2, '0');
        const fromday = String(fromDate.getDate()).padStart(2, '0');

        const fromFormattedDate = `${fromyear}-${frommonth}-${fromday}`;

        const toDate = new Date(dateRange[1]);
        const toyear = toDate.getFullYear();
        const tomonth = String(toDate.getMonth() + 1).padStart(2, '0');
        const today = String(toDate.getDate()).padStart(2, '0');

        const toFormattedDate = `${toyear}-${tomonth}-${today}`;
        props.action(props.macPos,"CUSTOM",fromFormattedDate,toFormattedDate)
      }
    }
  }
  
  const chartRef = useRef(null);
  const [option,setOption] = useState({
    grid: {
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
    },
    xAxis: {
      data: mockX(),
    },
    yAxis: {
      data: mockY(),
    },
  })

  const [dateRange, setDateRange] = useState([null, null]);
  const [startDate, endDate] = dateRange;

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

        chartInstance.setOption({
          graphic: [graphicImage],
          xAxis: {
            data: mockX(props.room.ROOM_X),
          },
          yAxis: {
            data: mockY(props.room.ROOM_Y),
          },
        });

        if (props.data){
          chartInstance.setOption({
            visualMap: {
              min: 0,
              max: props.data.MAX,
              inRange : {   
                color: ['rgba(235, 209, 12, 0.5)', 'rgba(235, 12, 12, 0.5)' ] //From smaller to bigger value ->
              }
            },
            series: [
              {
                name: "Person most spend time",
                type: "heatmap",
                data: props.data.DATA[0],
                itemStyle: {
                  color: function (value) {
                    // Set transparent color
                    return 'rgba(255, 0, 0, 0.5)'; // RGBA format with the fourth parameter (alpha) controlling transparency
                  }
                },
              },
            ],
          })
        }
      }
    };

    setGraphicImageSize();
    window.addEventListener('resize', setGraphicImageSize);
    return () => {
      window.removeEventListener('resize', setGraphicImageSize);
    };
  }, [props.room,props.data]);

  const customDatePicker = () =>{
    return (
      <DatePicker
        selectsRange={true}
        startDate={startDate}
        endDate={endDate}
        onChange={(update) => {
          setDateRange(update);
        }}
        isClearable={true}
      />
    )
  }

  const filterAreas = () => {
    if (props.is_admin){
      return (
        <Button
          type="primary"
          size="large"
          onClick={()=>{
            navigate('/dashboard/filterlocation?roomId='+props.room.ROOM_UUID)
          }}
        >
          Update Areas
        </Button>
      )
    }
    return null
  }

  return (
    <Popover content={filterAreas}>
      <Card 
        title="Location History" 
        style={{ height: "100%"}} 
        className='content-card'
        extra={
          <Menu 
            style={{width:'100%'}}
            theme="light" 
            mode="horizontal"
            onClick={handleOption}
            defaultSelectedKeys={['HOUR']}
          >
            <Menu.Item key="HOUR">Hour</Menu.Item>
            <Menu.Item key="DAY">Day</Menu.Item>
            <Menu.Item key="WEEK">Week</Menu.Item>
            <Menu.Item key="MONTH">Month</Menu.Item>
            <Popover title={"Select date range"} content={customDatePicker}>
              <Menu.Item key="CUSTOM">Custom</Menu.Item>
            </Popover>
          </Menu>
        }
      >
        
        <ReactECharts option={option} ref={chartRef} />
        
      </Card>
    </Popover>
  );
};

export default LocationHistory;