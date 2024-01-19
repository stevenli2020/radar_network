import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Typography, Row, Col, Button, Card, Divider, Space } from 'antd'
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

let client = null

const Summary = props => {

	const [alertVisible, setAlertVisible] = useState(false);
	const { Title } = Typography
	const navigate = useNavigate()
	const [searchParams, setSearchParams] = useSearchParams();

	const [selectedDate, setSelectedDate] = useState(new Date());
	const [disableNext, setDisableNext] = useState(true);

	const [maxDate,setMaxDate] = useState(new Date())

	const doFail = (e) => {
    console.error("Connection failed:", e);
  };

  const onMessageArrived = async (message) => {
    try {
      console.log("onMessageArrived:", message.payloadString, message.destinationName.split('/'), message);
      props.getRoomAlerts(props.room_uuid,false)
    } catch (error) {
      console.error("Error processing MQTT message:", error);
    }
  };

  useEffect(() => {
    const connectToBroker = async () => {
      try {
				const clientId = JSON.parse(getItem("LOGIN_TOKEN")).ID;
        const brokerUrl = "wss://aswelfarehome.gaitmetrics.org/mqtt";  // Include the path if required
        client = new Paho.Client(brokerUrl, clientId);
				
        await client.connect({
          timeout: 3,
          onSuccess: () => {
            console.log("Connected");
            client.subscribe("/GMT/DEV/ROOM/"+searchParams.get("roomId")+"/ALERT");
            client.onMessageArrived = onMessageArrived;
          },
          onFailure: doFail,
          userName: JSON.parse(getItem("LOGIN_TOKEN")).Username,
          password: "c764eb2b5fa2d259dc667e2b9e195218",
        });
      } catch (error) {
        console.error("Error connecting to MQTT broker:", error);
      }
    };

		if (getItem("LOGIN_TOKEN")){
    	connectToBroker();
		}
  }, []); // Include dependencies if needed
  

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

	return (
		<Container>
			<Row style={{alignItems: 'center' }}>
        <Col sm={12}>
          <Title>Summary ({props.room_name})</Title> 
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
					<h3>Weekly Report: </h3>
					<Button onClick={previousWeekClick} icon={<BsArrowLeft/>}>
					</Button>
					<DatePicker className='form-control' onKeyDown={()=>{return false}} maxDate={maxDate} selected={selectedDate} onChange={handleDateChange} />
					<Button onClick={nextWeekClick} disabled={disableNext} icon={<BsArrowRight/>}>
					</Button>
				</Space>
				
			</Row>

			<Divider/>
			<Container>
				<Row gutter={[16, 16]} >
					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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

					<Col xl={12} xxl={12} lg={12} md={12} sm={24} xs={24}>
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
				</Row>
			</Container>
			
			<AlertsModal visible={alertVisible} close={closeAlertModal} alerts={props.alerts}></AlertsModal>

			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(Summary)