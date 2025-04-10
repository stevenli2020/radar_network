import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Typography, Row, Col, Button, Card, Divider, Space, Tag, Collapse } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import { BsArrowLeft, BsArrowRight, BsCloudMoonFill, BsCloudSunFill, BsDoorClosedFill, BsFillLungsFill, BsFillSunsetFill, BsHeartFill, BsSignStopFill, BsTruckFlatbed } from "react-icons/bs";
import { Container } from 'react-bootstrap';
import ReactECharts from 'echarts-for-react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import AlertsModal from './AlertsModal';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import Paho from 'paho-mqtt'
import { getItem } from 'utils/tokenStore'
import getWebsocketServer from 'utils/websocket'

let client = null

const Summary = props => {

	const [alertVisible, setAlertVisible] = useState(false);
	const { Title } = Typography
	const navigate = useNavigate()
	const [searchParams, setSearchParams] = useSearchParams();

	const [selectedDate, setSelectedDate] = useState(new Date());
	const [disableNext, setDisableNext] = useState(true);

	const [maxDate,setMaxDate] = useState(new Date())
	const [isActive, setIsActive] = useState(true);

	const [items, setItems] = useState([]);

  useEffect(() => {

		if (getItem("LOGIN_TOKEN") && props.client_id == null){
			props.getMQTTClientID()
			props.getComponentsEnablement('summary')
		}
		
    const handleVisibilityChange = () => {
      setIsActive(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

	const doFail = (e) => {
    console.error("Connection failed:", e);
  };

  const onMessageArrived = async (message) => {
    try {
			let destination = message.destinationName.split('/')
			if (destination[destination.length-1] == "ALERT"){
				props.getRoomAlerts(props.room_uuid)
			}else if (destination[destination.length-1] == "BED_ANALYSIS"){
				const payloadBuffer = message.payloadString;

				// Convert the Buffer to a UTF-8 encoded string
				const payloadStr = payloadBuffer.toString('utf-8');

				// Parse the JSON string to a JavaScript object
				const payloadJson = JSON.parse(payloadStr);
				
				props.onChangeHOC('in_bed',payloadJson["IN_BED"])
			}
      
    } catch (error) {
      console.error("Error processing MQTT message:", error);
    }
  };

  useEffect(() => {
    const connectToBroker = async () => {
      try {
				const clientId = props.client_id;
        const brokerUrl = getWebsocketServer();  // Include the path if required
        client = new Paho.Client(brokerUrl, clientId);
				
        await client.connect({
          timeout: 3,
          onSuccess: () => {
            console.log("Connected");
						client.subscribe("/GMT/DEV/ROOM/"+searchParams.get("roomId")+"/BED_ANALYSIS");
            client.subscribe("/GMT/DEV/ROOM/"+searchParams.get("roomId")+"/ALERT");
            client.onMessageArrived = onMessageArrived;
          },
          onFailure: doFail,
          userName: getItem("Username"),
          password: "c764eb2b5fa2d259dc667e2b9e195218",
        });
      } catch (error) {
        console.error("Error connecting to MQTT broker:", error);
      }
    };

		if (getItem("LOGIN_TOKEN") && props.client_id != null){
    	connectToBroker();

			let intervalId;

      const startInterval = () => {
        intervalId = setInterval(() => {
          // Your interval function here
          console.log('Interval function running');
          connectToBroker();
        }, 1000 * 60 * 10); // Adjust the interval time as needed
      };

      const stopInterval = () => {
        clearInterval(intervalId);
      };

      if (isActive) {
        startInterval();
      } else {
        stopInterval();
      }

      return () => {
        stopInterval();
      };
		}
  }, [props.room_uuid,isActive, props.client_id]); // Include dependencies if needed
  
	useEffect(() => {
    return () => {
      if (client && client.isConnected()) {
        client.disconnect();
        console.log("Disconnected from MQTT broker");
      }
    };
  }, []);

	useEffect(() => {
		if (props.alerts.length>0){
			setAlertVisible(true)
		}
	}, [props.alerts])

	useEffect(() => {

		if (getItem("LOGIN_TOKEN")){
			props.initView(searchParams.get("roomId"))

			const initialDate = new Date();
			initialDate.setDate(initialDate.getDate() - 1);
			setSelectedDate(initialDate);

			setMaxDate(initialDate)
		}
	}, [])

	const closeAlertModal = () =>{
		setAlertVisible(false)
	}

	const navigateTo = () =>{
		navigate('/dashboard/history?roomId='+props.room_uuid)
	}

	const onChange = (date, dateString) => {
		console.log(date, dateString);
		props.onChangeHOC('eow',date)
	};

	useEffect(() => {
		if (getItem("LOGIN_TOKEN") && props.client_id){
			props.setClientConnection(props.client_id)
			let intervalId;
      const startInterval = () => {
        intervalId = setInterval(() => {
					if (getItem("LOGIN_TOKEN")){
						props.setClientConnection(props.client_id)
					}
        }, 1000 * 60 * 2); // Adjust the interval time as needed
      };
      startInterval();

			return () => {
				clearInterval(intervalId);
			};
		}
  }, [props.client_id]);

	// Function to change the selected week
	const changeWeek = (weekChange) => {
		let curr = new Date(selectedDate)
		curr.setDate(curr.getDate() + (7 * weekChange ));

		setSelectedDate(curr)

		const curr_year = curr.getFullYear();
		const curr_month = String(curr.getMonth() + 1).padStart(2, '0');
		const curr_day = String(curr.getDate()).padStart(2, '0');
		const currformattedDate = `${curr_year}-${curr_month}-${curr_day}`;

		props.getRoomSummary(props.room_uuid,currformattedDate)

		checkWeekLimit(new Date(curr))
	}

	const checkWeekLimit = (date) => {
		let next = new Date(date)
		next.setHours(0, 0, 0, 0);
		const currentDate = new Date();
		currentDate.setHours(0, 0, 0, 0);
		next.setDate(next.getDate() + 7);
		if (next >= currentDate){
			setDisableNext(true)
		}else{
			setDisableNext(false)
		}
	}

	const handleDateChange = (date) => {
    setSelectedDate(date);
		const current_year = date.getFullYear();
		const current_month = String(date.getMonth() + 1).padStart(2, '0');
		const current_day = String(date.getDate()).padStart(2, '0');
		const formattedDate = `${current_year}-${current_month}-${current_day}`;
		props.getRoomSummary(props.room_uuid,formattedDate)
		
		checkWeekLimit(new Date(date))
  };

	const previousWeekClick = () => {
    changeWeek(-1)
  };

	const nextWeekClick = () => {
    changeWeek(1)
  };

	useEffect(() => {
		if (props.receivedAlert == 1 && props.alerts.length > 0 && getItem("LOGIN_TOKEN")){
			setAlertVisible(true)
		}
	},[props.receivedAlert,props.alerts])

	useEffect(() => {
		var temp = []
		if (props.components?.sleep_analysis){
			temp.push(
			{
				key: 'sleep_analysis',
				label: 'Sleep Analysis',
				children: <Row gutter={[16, 16]} >
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsCloudMoonFill size={40} style={{color:"#2f54eb"}}/> Bed Time
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.bed_time.average}</Title>
														{
															props.bed_time_options ? <ReactECharts option={props.bed_time_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Latest</p>
															<Title level={4}>{props.bed_time.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Earliest</p>
															<Title level={4}>{props.bed_time.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.bed_time.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
	
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsCloudSunFill size={40} style={{color:"#2f54eb"}}/> Wake Up Time
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.wake_up_time.average}</Title>
														{
															props.wake_up_time_options ? <ReactECharts option={props.wake_up_time_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Latest</p>
															<Title level={4}>{props.wake_up_time.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Earliest</p>
															<Title level={4}>{props.wake_up_time.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.wake_up_time.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
	
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsFillSunsetFill size={40} style={{color:"#2f54eb"}}/> Sleeping Hour
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.sleeping_hour.average}</Title>
														{
															props.sleeping_hour_options ? <ReactECharts option={props.sleeping_hour_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.sleeping_hour.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.sleeping_hour.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.sleeping_hour.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
	
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsTruckFlatbed size={40} style={{color:"#2f54eb"}}/> Time In Bed
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.time_in_bed.average}</Title>
														{
															props.time_in_bed_options ? <ReactECharts option={props.time_in_bed_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.time_in_bed.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.time_in_bed.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.time_in_bed.previous_average}</span> 
													</div> 
												</div>
												
											</Card>
										</Col>
	
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsSignStopFill size={40} style={{color:"#2f54eb"}}/> Disrupt Duration
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.disrupt_duration.average}</Title>
														{
															props.disrupt_duration_options ? <ReactECharts option={props.disrupt_duration_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.disrupt_duration.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.disrupt_duration.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.disrupt_duration.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
	
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsSignStopFill size={40} style={{color:"#2f54eb"}}/> Sleep Disruption
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.sleep_disruption.average}</Title>
														{
															props.sleep_disruption_options ? <ReactECharts option={props.sleep_disruption_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.sleep_disruption.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.sleep_disruption.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.sleep_disruption.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
									</Row>,
			})
		}
	
		if (props.components?.inroom_analysis){
			temp.push(
			{
				key: 'inroom_analysis',
				label: 'In Room Analysis',
				children: <Row gutter={[16, 16]} >
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsDoorClosedFill size={40} style={{color:"#2f54eb"}}/> In Room
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.in_room.average}</Title>
														{
															props.in_room_options ? <ReactECharts option={props.in_room_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.in_room.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.in_room.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.in_room.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
										{props.in_room_posture_options && 
										<Col xl={16} xxl={16} lg={16} md={16} sm={24} xs={24} style={{}}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														In Room Posture Analysis
													</>  } 
												style={{
													height:'100%'
												}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={24}>
														<ReactECharts option={props.in_room_posture_options}/>
													</Col>
												</Row>
											</Card>
										</Col>
										}
										{props.in_room_series_posture_options && 
										<Col xl={24} xxl={24} lg={24} md={24} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														In Room Posture Time Series Analysis (In Minutes)
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={24}>
														<ReactECharts option={props.in_room_series_posture_options}/>
													</Col>
												</Row>
											</Card>
										</Col>
										}
									</Row>,
			})
		}
	
		if (props.components?.vital_analysis){
			temp.push(
			{
				key: 'vital_analysis',
				label: 'Vital Analysis',
				children: <Row gutter={[16, 16]} >
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsHeartFill size={40} style={{color:"#2f54eb"}}/> Heart Rate
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.heart_rate.average}</Title>
														{
															props.heart_rate_options ? <ReactECharts option={props.heart_rate_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.heart_rate.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.heart_rate.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.heart_rate.previous_average}</span> 
													</div>
												</div>
												
											</Card>
										</Col>
	
										<Col xl={8} xxl={8} lg={8} md={8} sm={24} xs={24}>
											<Card 
												headStyle={{textAlign:'center'}}
												title={ 
													<>
														<BsFillLungsFill size={40} style={{color:"#2f54eb"}}/> Breath Rate
													</>  } 
												style={{}} 
												className='content-card'
											>
												<Row style={{textAlign:'center'}}>
													<Col span={16}>
														<p>Week's Average</p>
														<Title level={2}>{props.breath_rate.average}</Title>
														{
															props.breath_rate_options ? <ReactECharts option={props.breath_rate_options}/>: null
														}
													</Col>
													<Col span={8} className='my-auto'>
														<div className='min-max-container'>
															<p>Maximum</p>
															<Title level={4}>{props.breath_rate.max}</Title>
														</div>
														<div className='min-max-container'>
															<p>Minimum</p>
															<Title level={4}>{props.breath_rate.min}</Title>
														</div>
													</Col>
												</Row>
												<div>
													<Divider/>
													<div style={{textAlign:'center'}}>
														Previous Week's Average: <span style={{fontWeight:'bold'}}>{props.breath_rate.previous_average}</span> 
													</div>
												</div>
											</Card>
										</Col>
									</Row>,
			})
		}

		setItems(temp)
	},[props.components, props.init])

	return (
		<Container>
		{
			!props.init? 
			<h1 style={{textAlign:'center'}}>Retrieving data ...</h1>:
			props.sensors.length===0?
			<h1 style={{textAlign:'center'}}>No sensor for this room!</h1>:
			<div>
				<Row style={{alignItems: 'center' }}>
					<Col sm={12}>
						<Title>Summary ({props.room_name}) {props.in_bed && <Tag>In Bed</Tag>}</Title> 
					</Col>
					<Col sm={12}>
						<Button
							type="default"
							size="large"
							style={{ float:'right' }}
							onClick={navigateTo}
						>
							History
						</Button>
						<Button
							type="primary"
							danger
							size="large"
							className='mx-2'
							style={{ float:'right' }}
							onClick={ ()=>
								{
									props.getRoomAlerts(props.room_uuid,false)
									setAlertVisible(true)
								}
							}
						>
							Alert
						</Button>
					</Col>
				</Row>
				
				<Row style={{alignItems:'center'}}>
					<Space>
						<h3>Report: </h3>
						<Button onClick={previousWeekClick} icon={<BsArrowLeft/>}>
						</Button>
						<DatePicker className='form-control' onKeyDown={()=>{return false}} maxDate={maxDate} selected={selectedDate} onChange={handleDateChange} />
						<Button onClick={nextWeekClick} disabled={disableNext} icon={<BsArrowRight/>}>
						</Button>
					</Space>
					
				</Row>

				<Divider/>
				<Container>
					<Collapse items={items} defaultActiveKey={['sleep_analysis','inroom_analysis','vital_analysis']} />
				</Container>
			</div>
		}
			
			{alertVisible && <AlertsModal visible={alertVisible} action={props.readAlert} close={closeAlertModal} alerts={props.alerts} setAlertAccuracy={props.setAlertAccuracy}></AlertsModal>}

			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(Summary)