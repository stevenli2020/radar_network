import { Card, Col, Divider, Menu, Popover,Row,Typography,message } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const brightGreen = "#32d616"
const brightOrange = "#fa9302"

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

const VitalSign = (props) => {

  const { Title } = Typography
  const [avgHeartRate, setAvgHeartRate] = useState("-")
  const [currHeartRate, setCurrHeartRate] = useState("-")
  const [avgBreathRate, setAvgBreathRate] = useState("-")
  const [currBreathRate, setCurrBreathRate] = useState("-")

  const handleOption = (item) => {

    if (mode != item.key){
      setMode(item.key)
      setCurrBreathRate("-")
      setCurrHeartRate("-")
      setAvgBreathRate("-")
      setAvgHeartRate("-")
      if (item.key == "REALTIME"){
        setRealtimeHeart(randR())
        setRealtimeBreath(randR())
        setRealtimeTime(gen2STime())
        setOption(defaultOptions)
      }
    }


    if (item.key){
      if (props.room_uuid && item.key != "REALTIME"){
        props.action(props.room_uuid,item.key)
      }
    }else{
      if (dateRange[0] == null || dateRange[1] == null){
        message.error('Please select date range!!');
      }else{
        const fromDate = new Date(dateRange[0]);
        const fromyear = fromDate.getFullYear();
        const frommonth = String(fromDate.getMonth() + 1).padStart(2, '0');
        const fromday = String(fromDate.getDate()).padStart(2, '0');

        const fromFormattedDate = `${fromyear}-${frommonth}-${fromday} 0:00`;

        const toDate = new Date(dateRange[1]);
        const toyear = toDate.getFullYear();
        const tomonth = String(toDate.getMonth() + 1).padStart(2, '0');
        const today = String(toDate.getDate()).padStart(2, '0');

        const toFormattedDate = `${toyear}-${tomonth}-${today} 23:59`;
        props.action(props.room_uuid,"CUSTOM",fromFormattedDate,toFormattedDate)
      }
    }
  }

  const [dateRange, setDateRange] = useState([null, null]);
  const [realtimeHeart, setRealtimeHeart] = useState(randR());
  const [realtimeBreath, setRealtimeBreath] = useState(randR());
  const [realtimeTime, setRealtimeTime] = useState(gen2STime());
  const [mode, setMode] = useState('1 WEEK')
  const [startDate, endDate] = dateRange;
  const chartRef = useRef(null);
  const defaultOptions = {
    textStyle: {
      color: "#000",
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
        min: 35,
        max: 0,
      },
    ],
    title: [
      {
        left: "center",
      },
      {
        top: "50%",
        left: "center",
      },
    ],
    tooltip: {
      trigger: "axis",
      axisPointer: {
        // type: "cross",
        // label: {
        //   backgroundColor: "#283b56",
        // },
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
      },
      {
        axisLine: {
          show: false,
        },
        type: "category",
        boundaryGap: true,
        data: gen2STime(),
        gridIndex: 1,
        splitLine: {
          show: false,
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
        max: 100,
        min: 0,
        boundaryGap: [0.2, 0.2],
        splitLine: {
          show: false,
        },
      },
      {
        axisLine: {
          show: false,
        },
        type: "value",
        scale: true,
        max: 35,
        min: 0,
        boundaryGap: [0.2, 0.2],
        gridIndex: 1,
        splitLine: {
          show: false,
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
          color: "#000"
        }
      },
    ],
    series: [
      {
        name: "Heart Waveform",
        type: "bar",
        smooth: true,
        emphasis: {
          focus: "series",
        },
        data: randR(),
      },
      {
        name: "Breath Waveform",
        type: "bar",
        smooth: true,
        emphasis: {
          focus: "series",
        },
        data: randR(),
        xAxisIndex: 1,
        yAxisIndex: 1,
      }    
    ],
  };
  const [option,setOption] = useState(defaultOptions)

  useEffect(()=>{
    if (mode == "REALTIME" && props.vital_data){
      let now = new Date();
      let heartRate = props.vital_data[0]
      let breathRate = props.vital_data[1]
      let hearthRates = [...realtimeHeart, heartRate];
      let breathRates = [...realtimeBreath, breathRate];
      let timeRange = [...realtimeTime, now.toLocaleTimeString().replace(/^\D*/, "")];

      // Filter out 0 values
      let nonZeroHeartRates = hearthRates.filter(rate => rate !== 0);
      let nonZeroBreathRates = breathRates.filter(rate => rate !== 0);

      // Calculate the average
      let averageHeartRate = nonZeroHeartRates.length > 0
        ? (nonZeroHeartRates.reduce((sum, rate) => sum + rate, 0) / nonZeroHeartRates.length)
        : 0;

      let averageBreathRate = nonZeroBreathRates.length > 0
        ? (nonZeroBreathRates.reduce((sum, rate) => sum + rate, 0) / nonZeroBreathRates.length)
        : 0;

      if (averageBreathRate != 0){
        setAvgBreathRate(averageBreathRate.toFixed(1))
      }

      if (averageHeartRate != 0){
        setAvgHeartRate(averageHeartRate.toFixed(1))
      }

      if (heartRate){
        setCurrHeartRate(heartRate.toFixed(1))
      }else{
        setCurrHeartRate("-")
      }

      if (breathRate){
        setCurrBreathRate(breathRate.toFixed(1))
      }else{
        setCurrBreathRate("-")
      }

      const chartInstance = chartRef.current.getEchartsInstance();

      const setGraphicImageSize = () => {
        chartInstance.setOption({
          xAxis: [
            {
              axisLine: {
                show: false,
              },
              type: "category",
              boundaryGap: true,
              data: timeRange,
              splitLine: {
                show: false,
              },
            },
            {
              axisLine: {
                show: false,
              },
              type: "category",
              boundaryGap: true,
              data: timeRange,
              gridIndex: 1,
              splitLine: {
                show: false,
              },
            },
          ],
          series: [
            {
              name: "Heart Waveform",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: hearthRates,
            },
            {
              name: "Breath Waveform",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: breathRates,
              xAxisIndex: 1,
              yAxisIndex: 1,
            }    
          ],
        });
      };

      setRealtimeHeart(hearthRates)
      setRealtimeBreath(breathRates)
      setRealtimeTime(timeRange)

      setGraphicImageSize();
      window.addEventListener('resize', setGraphicImageSize);
      return () => {
        window.removeEventListener('resize', setGraphicImageSize);
      };
    }
  },[props.vital_data])

  useEffect(() => {
    const chartInstance = chartRef.current.getEchartsInstance();

    setCurrBreathRate("-")
    setCurrHeartRate("-")

    const setGraphicImageSize = () => {
      if (props.data) {
        let avgHeart = 60
        let avgBreath = 12

        let heartLowerAvg = avgHeart - (avgHeart*0.2)
        let heartUpperAvg = avgHeart + (avgHeart*0.2)
        let breathLowerAvg = avgBreath - (avgBreath*0.2)
        let breathUpperAvg = avgBreath + (avgBreath*0.2)


        if ("AVG" in props.data){
          avgHeart = props.data.AVG[0][0]
          avgBreath = props.data.AVG[0][1]
          if(avgHeart>200){         
            avgHeart = 60                                      
          } else {
            if(avgHeart<30){
              avgHeart = 60
            } else {
            }     
            setAvgHeartRate(avgHeart)       
          }
          if(avgBreath>25){
            avgBreath = 12
          } else {
            if(avgBreath<0){
              avgBreath = 12
            } else {
            }  
            
            setAvgBreathRate(avgBreath)
          }
          heartLowerAvg = avgHeart - (avgHeart*0.2)
          heartUpperAvg = avgHeart + (avgHeart*0.2)
          breathLowerAvg = avgBreath - (avgBreath*0.2)
          breathUpperAvg = avgBreath + (avgBreath*0.2)
        }
        let histVitalData = []
        let histVitalData2 = []
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
                d[2] = parseFloat(d_arr[1]);
                let t = "1 WEEK"
                if (t == "1 HOUR" || t == "1 DAY") {
                  histVitalTime.push(d[0].substring(11, 16));
                } else if (t == "1 WEEK" || t == "1 MONTH" || t == "CUSTOM") {
                  histVitalTime.push(d[0].substring(0, 16));
                }			
                
                histVitalData.push({value: d[1]});
                histVitalData2.push({value: d[2]});
              }
            }   
          }
        } else {
          histVitalData = randR()
          histVitalData2 = randR()
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
            },
            {
              axisLine: {
                show: false,
              },
              type: "category",
              boundaryGap: true,
              data: histVitalTime,
              gridIndex: 1,
              splitLine: {
                show: false,
              },
            },
          ],
          series: [
            {
              name: "Heart Waveform",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: histVitalData,
            },
            {
              name: "Breath Waveform",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: histVitalData2,
              xAxisIndex: 1,
              yAxisIndex: 1,
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
      title="Vital Signs" 
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
          <Menu.Item key="REALTIME">Realtime</Menu.Item>
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
        <Col span={6} style={{alignItems:'center',display:'flex'}}>
          <div >
            <Title level={4}>Heart Rate</Title>
            <Title level={4}>{currHeartRate}</Title>
            <Title level={5}>Average: {avgHeartRate} BPM</Title>
            <hr/>
            <Title level={4}>Breath Rate</Title>
            <Title level={4}>{currBreathRate}</Title>
            <Title level={5}>Average: {avgBreathRate} BPM</Title>
          </div>
        </Col>
        <Col span={18}>
          <ReactECharts style={{minHeight:400}} option={option} ref={chartRef} />
        </Col>
      </Row>
    </Card>
  );
};

export default VitalSign;