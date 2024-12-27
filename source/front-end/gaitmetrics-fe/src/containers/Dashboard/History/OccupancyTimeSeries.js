import { Card, Col, Divider, Menu, Popover,Row,Typography,message } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import ChartLoader from 'components/ChartLoader';

const randR = () => {
  let res = [];
  let len = 100;
  while (len--) {
    res.push(0)
  }
  return res;
};

const gen2STime = () => {
  let now = new Date();
  let res = [];
  let len = 100;
  while (len--) {
    res.unshift(now.toLocaleTimeString().replace(/^\D*/, ""));
    now = new Date(+now - 2000);
  }
  return res;
};

const OccupancyTimeSeries = (props) => {

  const { Title } = Typography
  const [chartLoading, setChartLoading] = useState(true)

  const handleOption = (item) => {

    if (mode != item.key){
      setMode(item.key)
    }


    if (item.key){
      if (props.room_uuid){
        if (props.data){
          setChartLoading(true)
        }
        props.action(props.room_uuid,item.key)
      }
    }else{
      if (dateRange[0] == null || dateRange[1] == null){
        message.error('Please select date range!!');
      }else{
        if (props.data){
          setChartLoading(true)
        }
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
        props.action(props.room_uuid,"CUSTOM",fromFormattedDate,toFormattedDate)
      }
    }
  }

  const [dateRange, setDateRange] = useState([null, null]);
  const [mode, setMode] = useState('1 WEEK')
  const [startDate, endDate] = dateRange;
  const chartRef = useRef(null);
  const defaultOptions = {
    textStyle: {
      color: "#000",
    },
    visualMap: [
      {
        show: false,
        type: "continuous",
        seriesIndex: 0,
        min: 80,
        max: 0,
      },
    ],
    title: [
      {
        left: "center",
      },
    ],
    tooltip: {
      trigger: "axis",
      axisPointer: {
      },
    },
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
        data: gen2STime(),
        splitLine: {
          show: false,
        },
      }
    ],
    yAxis: [
      {
        axisLine: {
          show: false,
        },
        type: "value",
        scale: true,
        max: 1,
        min: 0,
        boundaryGap: [0.2, 0.2],
        splitLine: {
          show: false,
        },
      }
    ],
    grid: [
      {
        bottom: "30%",
      },
    ],
    dataZoom: [
      {
        top: "80%",
        start: 0,
        end: 100,
        xAxisIndex: [0, 1],
        textStyle: {
          color: "#000"
        }
      },
    ],
    series: [
      {
        name: "Data Count",
        type: "bar",
        smooth: true,
        emphasis: {
          focus: "series",
        },
        data: randR(),
      }
    ],
  };
  const [option,setOption] = useState(defaultOptions)

  useEffect(() => {
    const chartInstance = chartRef.current.getEchartsInstance();

    const setGraphicImageSize = () => {
      if (props.data) {
        let histVitalData = []
        let histVitalTime = []
        if ("DATA" in props.data) {       
          if (props.data.DATA.length > 0) {
            const localDate = new Date()
            const localGMTVal = Math.abs(localDate.getTimezoneOffset() * 60 * 1000)
            // const localGMTVal = 0
            let idx = 0;
            let _idx = 0;
            let data_str = props.data.DATA[0];
            let time = parseInt(props.data.TIME_START);
            while(idx != -1){
              idx = data_str.indexOf(";", idx+2);
              let d_str = data_str.substr(_idx,idx-_idx);
              _idx = idx+1;
              let d = [0,0,0];
              if (d_str!=""){
                let d_arr = d_str.split(",");
                d[0] = new Date((time*1000)+localGMTVal).toISOString().slice(0,16).replace('T', ' ');					
                time = time + 60;
                d[1] = parseFloat(d_arr[0]);
                let t = "1 WEEK"
                if (t == "1 HOUR" || t == "1 DAY") {
                  histVitalTime.push(d[0].substring(11, 16));
                } else if (t == "1 WEEK" || t == "1 MONTH" || t == "CUSTOM") {
                  histVitalTime.push(d[0].substring(0, 16));
                }			
                
                histVitalData.push({value: d[1]});
              }
            }   
          }
        } else {
          histVitalData = randR()
          histVitalTime = gen2STime()
        }
        chartInstance.setOption({
          xAxis: [
            {
              axisLine: {
                show: false,
              },
              type: "category",
              boundaryGap: true,
              data: histVitalTime,
              splitLine: {
                show: false,
              },
            }
          ],
          series: [
            {
              name: "Data Count",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: histVitalData,
            }  
          ],
        });
      }else{
        let histVitalData = []
        let histVitalTime = []
        histVitalData = randR()
        histVitalTime = gen2STime()
        chartInstance.setOption({
          xAxis: [
            {
              axisLine: {
                show: false,
              },
              type: "category",
              boundaryGap: true,
              data: histVitalTime,
              splitLine: {
                show: false,
              },
            }
          ],
          series: [
            {
              name: "Data Count",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: histVitalData,
            }
          ],
        });
      }

      setChartLoading(false)
    };

    setGraphicImageSize();
    window.addEventListener('resize', setGraphicImageSize);
    return () => {
      window.removeEventListener('resize', setGraphicImageSize);
    };
  }, [props.data]);

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

  return (
    <Card 
      title="Occupancy Time Series History" 
      style={{ height: "100%"}} 
      className='content-card'
      extra={
        <Menu 
          style={{width:'100%'}}
          theme="light" 
          mode="horizontal"
          onClick={handleOption}
          defaultSelectedKeys={['1 WEEK']}
        >
          <Menu.Item key="1 HOUR">Hour</Menu.Item>
          <Menu.Item key="1 DAY">Day</Menu.Item>
          <Menu.Item key="1 WEEK">Week</Menu.Item>
          <Menu.Item key="1 MONTH">Month</Menu.Item>
          <Popover title={"Select date range"} content={customDatePicker}>
            <Menu.Item key="CUSTOM">Custom</Menu.Item>
          </Popover>
        </Menu>
      }
    >
      <Row>
        <Col span={24}>
          <ReactECharts option={option} ref={chartRef} />
        </Col>
      </Row>
      {
        chartLoading && <ChartLoader/>
      }
    </Card>
  );
};

export default OccupancyTimeSeries;