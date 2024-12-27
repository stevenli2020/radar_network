import React, { useEffect, useState, useRef } from 'react'
import moment from 'moment';
import WithHOC from './actions'
import { useNavigate } from "react-router-dom"
import { Typography, Card, Row, Col, Divider,Tag, Space, Modal, Button, Popover, Table, Radio } from 'antd'
import { ArrowRightOutlined, EditTwoTone, DeleteTwoTone, PlusOutlined, AlertFilled, EditOutlined, SendOutlined, LoginOutlined } from '@ant-design/icons'

import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import AddRoomModal from './AddRoomModal'
import UpdateRoomModal from './UpdateRoomModal'
import { getItem } from 'utils/tokenStore'
import getDomainURL from 'utils/api'
import getWebsocketServer from 'utils/websocket'
import _ from 'lodash';
import Paho from 'paho-mqtt'

import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { color } from 'echarts';
import EditRoomOnMapModal from './EditRoomOnMapModal';
import TriggerAlertModal from './TriggerRoomAlert';

import heart from '../../../assets/heart.png';
import heartWarning from '../../../assets/heart_orange.png';
import heartNormal from '../../../assets/heart_green.png';

let client = null

const viewportWidthInPixels = window.innerWidth;
const viewportHeightInPixels = window.innerHeight;
const backgroundImageUrl = getDomainURL() + `/static/uploads/prison.jpg`

const Home = (props) => {

	const [isActive, setIsActive] = useState(true);

  useEffect(() => {

		if (getItem("LOGIN_TOKEN") && props.client_id == null){
			props.getMQTTClientID()
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
				setConnected(false)
				await props.getRoomDetails()
			}else if (destination[destination.length-1] == "BED_ANALYSIS"){
				// console.log("onMessageArrived:", message.payloadString, message.destinationName.split('/'), message);
				const payloadBuffer = message.payloadString;

				// Convert the Buffer to a UTF-8 encoded string
				const payloadStr = payloadBuffer.toString('utf-8');

				// Parse the JSON string to a JavaScript object
				const payloadJson = JSON.parse(payloadStr);
				// console.log(destination[3],payloadJson)
				
				const updatedRooms = [...props.rooms]; // Create a shallow copy of rooms
				const roomToUpdate = _.find(updatedRooms, { ROOM_UUID: destination[4] });

				if (roomToUpdate) {
					roomToUpdate.IN_BED = payloadJson["IN_BED"];
				}
				
				// props.onChangeHOC('rooms',updatedRooms)
			} else if (destination[destination.length-1] == "HEART_RATE"){

				const payloadBuffer = message.payloadString;

				// Convert the Buffer to a UTF-8 encoded string
				const payloadStr = payloadBuffer.toString('utf-8');

				const payloadJson = JSON.parse(payloadStr);

				// Parse the JSON string to a JavaScript object
				// console.log(destination[3],payloadJson)
				
				const updatedRooms = [...props.rooms]; // Create a shallow copy of rooms
				const roomToUpdate = _.find(updatedRooms, { ROOM_UUID: destination[4] });
				console.log(destination[4])
				if (roomToUpdate) {
					const now = new Date();
					// Get the user's timezone offset in minutes
					const userTimezoneOffset = now.getTimezoneOffset();
					// Calculate the timezone offset in milliseconds
					const timezoneOffsetMilliseconds = userTimezoneOffset * 60 * 1000;
					// Get the current time in UTC
					const nowUTC = now.getTime() - timezoneOffsetMilliseconds;
					// Create a new Date object with the adjusted time
					const timeInUserTimezone = new Date(nowUTC);
					roomToUpdate.LAST_DATA_RECEIVED = Date.now();
					roomToUpdate.HEART_RATE = parseFloat(payloadJson["HEART_RATE"]).toFixed(1);
					roomToUpdate.LAST_HEART_TS = Date.now()
					roomToUpdate.IN_BED = true;
					roomToUpdate.LAST_IN_BED_TS = Date.now()
					if (payloadJson["STATUS"] != 0){
						roomToUpdate.STATUS = payloadJson["STATUS"]
					}else{
						roomToUpdate.STATUS = 1	
					}
					
					props.onChangeHOC('rooms',updatedRooms)
				}
			}
    } catch (error) {
      console.error("Error processing MQTT message:", error);
    }
  };

	useEffect(() => {
		if (props.rooms.length >0) {
			props.rooms
				.forEach((room) => {

					const heartItem = document.getElementById(`heart-item-${room.ID}`);
					
					if (heartItem) {
						if (room.HEART_RATE) {
							heartItem.style.display = 'block';
							if (room.HEART_RATE >= 40 && room.HEART_RATE <= 110) {
								heartItem.src = heartNormal // Set image for normal heart rate
							} else {
								heartItem.src = heartWarning; // Set image for abnormal heart rate
							}
						} else {
							heartItem.style.display = 'none';
						}
					}
				});
		}
	}, [props.rooms]);

	const intervalRef = useRef(null); // Track interval ID
  const roomsRef = useRef(props.rooms); // Track latest rooms reference

  // Update roomsRef whenever props.rooms changes
  useEffect(() => {
    roomsRef.current = props.rooms;
  }, [props.rooms]);

  // Clear heart rate logic
  const clearHeartRate = () => {
    const currentTimestamp = Date.now();
    const updatedRooms = [...roomsRef.current];
    let change = false;

    updatedRooms.forEach((room) => {
      if (room.LAST_HEART_TS && currentTimestamp - room.LAST_HEART_TS > 30000) {
        room.HEART_RATE = null;
        room.LAST_HEART_TS = null;
        room.IN_BED = false;
        room.LAST_IN_BED_TS = null;
        change = true;
      }

      if (room.LAST_IN_BED_TS && currentTimestamp - room.LAST_IN_BED_TS > 30000) {
        room.IN_BED = false;
        room.LAST_IN_BED_TS = null;
        change = true;
      }
    });

    if (change) {
      props.onChangeHOC('rooms', updatedRooms);
    }
  };

	const [connected, setConnected] = useState(false);

  useEffect(() => {

		if (getItem("LOGIN_TOKEN") && getItem("TYPE")){
      if (getItem("TYPE") == "1" || getItem("TYPE") == "2"){
        props.onChangeHOC('isAdmin',true)
      }
    }

    const connectToBroker = async () => {
      try {
				const clientId = props.client_id
        const brokerUrl = getWebsocketServer();  // Include the path if required
        client = new Paho.Client(brokerUrl, clientId);
				
        await client.connect({
          timeout: 3,
          onSuccess: () => {
            console.log("Connected");
						setConnected(true)
            client.subscribe("/GMT/DEV/ROOM/+/ALERT");
						client.subscribe("/GMT/DEV/ROOM/+/BED_ANALYSIS");
						client.subscribe("/GMT/DEV/ROOM/+/HEART_RATE");
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

		if (getItem("LOGIN_TOKEN") && props.rooms.length > 0 && props.client_id != null){
			console.log("refresh connection")
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

			if (intervalRef.current) {
        clearInterval(intervalRef.current); // Clear existing interval
      }

      intervalRef.current = setInterval(() => {
        console.log('Clearing heart rate...');
        clearHeartRate();
      }, 1000); // Adjust as needed

      return () => {
        stopInterval();
				if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
		}
  }, [props.rooms,connected, isActive, props.client_id, props.playing]); // Include dependencies if needed

	useEffect(() => {
    return () => {
      if (client && client.isConnected()) {
        client.disconnect();
        console.log("Disconnected from MQTT broker");
        setConnected(false);
      }
    };
  }, []);

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
  

	const [addVisible, setAddVisible] = useState(false);
	const [updateVisible, setUpdateVisible] = useState(false);
	const [triggerAlertVisible, setTriggerAlertVisible] = useState(false);
	const [editMapVisible, setEditMapVisible] = useState(false);

	const { Title } = Typography
	const navigate = useNavigate()
	const timezoneOffset = new Date().getTimezoneOffset();

	useEffect(() => {
		if (getItem("LOGIN_TOKEN")){
      props.getRoomDetails()
    }
		
	}, [])

	const toSummary = (roomId) =>{
		navigate('/dashboard/summary?roomId=' + roomId)
	}

	const showAddModal = () => {
    setAddVisible(true);
  };

	const showEditMapModal = () => {
    setEditMapVisible(true);
  };

  const closeAddModal = () => {
    setAddVisible(false);
  };

  const closeUpdateModal = () => {
    setUpdateVisible(false);
  };

	const closeTriggerAlertModal = () => {
    setTriggerAlertVisible(false);
  };

	const closeEditMapModal = () => {
    setEditMapVisible(false);
  };

  const showUpdateModal = () => {
    setUpdateVisible(true);
  };

	const showTriggerAlertModal = () => {
    setTriggerAlertVisible(true);
  };

	const popoverContent = (room) =>{
		return (
		<div>
			<Table 
				dataSource={room.ALERTS} 
        columns={columns} >
			</Table>
			<span>
				<Button
					type="primary"
					onClick={()=>{
						props.readAlerts(room.ROOM_UUID)
					}}
				>
					OK
				</Button>
			</span>
			
		</div>)
	}

	const roomContent = (room) =>{
		return (
			<Card 
				title={ room.ROOM_NAME } 
				style={{ height: "100%"}} 
				className='content-card'
				extra={
					<Space>
						{
							room.ALERTS.length>0?(
								<Popover title="Alert(s)" content={popoverContent(room)}>
									<AlertFilled style={{color:'red'}}></AlertFilled>
								</Popover>):(<></>)
						}
						{room.IN_BED && room.ROOM_NAME!='Wall Sensor'?<Tag>In Bed</Tag>:''}
						<EditTwoTone onClick={ ()=>{
							props.onChangeHOC('updateUploadImg',null)
							props.onChangeHOC('selectedRoom',room)
							console.log(room)
							showUpdateModal()
						}
						}></EditTwoTone>

						<DeleteTwoTone onClick={() => 
							Modal.confirm({
								title: 'Delete Room',
								content: 'Are you sure you want to delete '+room.ROOM_NAME+'?',
								okText:'Confirm',
								cancelText:'Cancel',
								onOk:() => {
									props.deleteRoom(room)
								},
							})
						}></DeleteTwoTone>

						{/* <ArrowRightOutlined onClick={
							() => {
								toSummary(room.ROOM_UUID)
							}
						}></ArrowRightOutlined> */}
					</Space>
				}
			>
				<div
					onClick={
						() => {
							toSummary(room.ROOM_UUID)
						}
					} 
				>
					<p>{room.INFO?room.INFO:'-'}</p>
					<p>Status: <Tag>{
						room.STATUS === 0? 'Room is empty':
						room.STATUS === 1? 'Room is occupied':
						room.STATUS === 2? 'Sleeping':
						room.STATUS === 255? 'Alert':
						'Room is empty'
					}</Tag></p>
					<p>Location: <Tag>{room.ROOM_LOC}</Tag></p>
					<p>Last data: <Tag>{
						moment(room.LAST_DATA_RECEIVED).fromNow()
						}</Tag></p>
				</div>
				
			</Card>
		// <div>
		// 	<p>{room.INFO?room.INFO:'-'}</p>
		// 	<p>Status: <Tag>{
		// 		room.STATUS === 0? 'Room is empty':
		// 		room.STATUS === 1? 'Room is occupied':
		// 		room.STATUS === 2? 'Sleeping':
		// 		room.STATUS === 255? 'Alert':
		// 		'Room is empty'
		// 	}</Tag></p>
		// 	<p>Location: <Tag>{room.ROOM_LOC}</Tag></p>
		// 	<p>Last data: <Tag>{
		// 		moment(room.LAST_DATA_TS).add(timezoneOffset, 'minutes').fromNow()
		// 		}</Tag></p>
		// </div>
		)
	}

	const columns = [ 
    { 
      key: "ID", 
      title: "ID", 
      dataIndex: "ID", 
      sorter: true,
    }, 
    { 
      key: "URGENCY", 
      title: "Urgency", 
      render: (_, alert) => (
				alert.URGENCY==0?(<span style={{color:'green'}}>Information</span>):
				alert.URGENCY==1?(<span style={{color:'yellow'}}>Attention</span>):
				alert.URGENCY==2?(<span style={{color:'orange'}}>Escalated</span>):
				(<span style={{color:'red'}}>Urgent</span>)
			),
    }, 
    { 
      key: "DETAILS", 
      title: "Details", 
      dataIndex: "DETAILS"
    }, 
    { 
      key: "TIMESTAMP", 
      title: "Date", 
			render: (_, alert) => (
				<span>{new Date(alert.TIMESTAMP).toLocaleString()}</span>
			),
    },
		{ 
      key: "ACCURACY", 
      title: "Accuracy", 
      render: (_, alert) => (
				<Radio.Group onChange={(val) => {
              props.setAlertAccuracy(alert.ID,val.target.value);
            }} value={alert.ACCURACY}>
          <Radio value={1}>True</Radio>
          <Radio value={0}>False</Radio>
        </Radio.Group>
			),
    }
	]

	const initialLayout = props.rooms
  .filter((room) => room.x !== null && room.y !== null && room.w !== null && room.h !== null)
  .map((room, index) => ({
    i: `${room.ID.toString()}`,
    x: room.x, // Adjust based on your grid structure
    y: room.y, // Adjust based on your grid structure
    w: room.w,
    h: room.h,
  }));

  // Callback function to handle layout changes
  const onLayoutChange = (layout) => {
    // Handle layout changes if needed
    console.log(layout);
  };

	return (
		<Container>
			{/* <Title>Home Page</Title> */}

			<Row gutter={[16, 16]} >
				<Col xl={5} xxl={5} lg={6} md={6} sm={24} xs={24}>
					<Card 
						title="Room Count" 
					>
						<Title>
							{props.rooms.length}
						</Title>
					</Card>
				</Col>
				<Col xl={5} xxl={5} lg={6} md={6} sm={24} xs={24}>
					<Card 
						title="Unread Alert" 
					>
						<Title
							style={
								props.alertLength>0?{
									color:"red"
								}:{}
							}
						>
							{props.alertLength}
						</Title>
					</Card>
					
				</Col>
			</Row>
			<Divider/>

			{
				props.isAdmin?
				<Row style={{alignItems: 'center' }}>
					<Col sm={24}>
						<Button
							type="primary"
							size="large"
							icon={<PlusOutlined />}
							style={{ background: '#1890ff', borderColor: '#1890ff', float:'right' }}
							onClick={showAddModal}
						>
							Add Room
						</Button>
						{
							props.mapView?
							<Button
								type="primary"
								size="large"
								icon={<EditOutlined />}
								className='mx-2'
								style={{ background: '#1890ff', borderColor: '#1890ff', float:'right' }}
								onClick={showEditMapModal}
							>
								Edit Map
							</Button>:null
						}
					</Col>
				</Row>:null
			}
			

			{props.mapView?
			<div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
				<div className='mt-5' style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',width:'700px',height:'500px' }}>
					{/* <Image src={getDomainURL() + `/static/uploads/white.png`} preview={false} style={{width:'60vw',height:'50vh'}}/> */}
					<GridLayout
						className="grid-layout"
						style={{backgroundImage:`url(${backgroundImageUrl})`,backgroundRepeat:'no-repeat', backgroundSize:'700px 500px'}}
						layout={initialLayout}
						cols={100}
						autoSize={false}
						rowHeight={2} // 50vh / 4 rows
						width={700} // 60vw * 12 cols
						onLayoutChange={onLayoutChange}
						verticalCompact={false}
						isDraggable={false}
						isResizable={false}
						preventCollision={true}
						// isBounded={true} 
					>
						{
						props.rooms.filter((room) => room.x !== null && room.y !== null && room.w !== null && room.h !== null).map( room => (
							<div key={room.ID.toString()} className={`grid-item ${room.ALERTS.length > 0 ? 'red-background' : ''}`} >
								<Popover content={roomContent(room)}>
									<div style={{display:'flex',alignItems:'center',justifyContent: 'center',height:'100%',cursor:'pointer'}}>
										{room.ROOM_NAME} 
									</div>
								</Popover>
							</div>)) 
						}
					</GridLayout>
				</div>
			</div>
			:
			<Row gutter={[16, 16]} className='mt-2' >
				{
					props.rooms.map( room => (
						<Col xl={6} xxl={6} lg={6} md={12} sm={24} xs={24}	key={"room - " + room.ID}>
							{
								room.ALERTS.length>0?(
									<Popover 
										title="Alert(s)" 
										content={popoverContent(room)} 
										trigger="hover">
											<Card 
								title={ room.ROOM_NAME } 
								style={{ height: "100%"}} 
								className='content-card'
								extra={
									<Space>
										{
											room.ALERTS.length>0?(
												<AlertFilled style={{color:'red'}}></AlertFilled>):(<></>)
										}
										{
											props.isAdmin?<SendOutlined onClick={ ()=>{
												props.onChangeHOC('selectedRoom',room)
												showTriggerAlertModal()
											}
											}></SendOutlined>:(<></>)
										}
										{
											props.isAdmin?<LoginOutlined onClick={ ()=>{
												Modal.confirm({
													title: room.ACTIVE?'Deactivate Room':'Activate Room',
													content: room.ACTIVE?'Are you sure you want to deactivate '+room.ROOM_NAME+'?':'Are you sure you want to activate '+room.ROOM_NAME+'?',
													okText:'Confirm',
													cancelText:'Cancel',
													onOk:() => {
														if (room.ACTIVE){
															props.updateRoomActive(room.ROOM_UUID,0)
														}else{
															props.updateRoomActive(room.ROOM_UUID,1)
														}
														
													},
												})
											}
											}></LoginOutlined>:(<></>)
										}
										<EditTwoTone onClick={ ()=>{
											props.onChangeHOC('updateUploadImg',null)
											props.onChangeHOC('selectedRoom',room)
											console.log(room)
											showUpdateModal()
										}
										}></EditTwoTone>

										<DeleteTwoTone onClick={() => 
											Modal.confirm({
												title: 'Delete Room',
												content: 'Are you sure you want to delete '+room.ROOM_NAME+'?',
												okText:'Confirm',
												cancelText:'Cancel',
												onOk:() => {
													props.deleteRoom(room)
												},
											})
										}></DeleteTwoTone>

										{/* <ArrowRightOutlined onClick={
											() => {
												toSummary(room.ROOM_UUID)
											}
										}></ArrowRightOutlined> */}
									</Space>
								}
							>
								<div
									onClick={
										() => {
											toSummary(room.ROOM_UUID)
										}
									} 
								>
									<p>{room.INFO?room.INFO:'-'} <img id={`heart-item-${room.ID}`} src={heart} alt="Heart" style={{ display:'none', position:'absolute', right: 0, top:50,  margin: '16px',height: '30px', width: 'auto' }} /></p>
									<p>Status: <Tag>{
										room.MAC.length === 0? 'No sensor':
										room.STATUS === 0? 'Room is empty':
										room.STATUS === 1? 'Room is occupied':
										room.STATUS === 2? 'Sleeping':
										room.STATUS === 255? 'Alert':
										'Room is empty'
									}</Tag></p>
									<p>Location: <Tag>{room.ROOM_LOC}</Tag></p>
									<p>Last data: <Tag>{
										room.MAC.length === 0? '-':
										moment(room.LAST_DATA_RECEIVED).fromNow()
										}</Tag></p>
								</div>
								
							</Card>
									</Popover>):
								(<>
<Card 
								title={ room.ROOM_NAME } 
								style={{ height: "100%"}} 
								className='content-card'
								extra={
									<Space>
										{
											room.ALERTS.length>0?(
												<AlertFilled style={{color:'red'}}></AlertFilled>):(<></>)
										}
										{
											props.isAdmin?<SendOutlined onClick={ ()=>{
												props.onChangeHOC('selectedRoom',room)
												showTriggerAlertModal()
											}
											}></SendOutlined>:(<></>)
										}
										{
											props.isAdmin?<LoginOutlined onClick={ ()=>{
												Modal.confirm({
													title: room.ACTIVE?'Deactivate Room':'Activate Room',
													content: room.ACTIVE?'Are you sure you want to deactivate '+room.ROOM_NAME+'?':'Are you sure you want to activate '+room.ROOM_NAME+'?',
													okText:'Confirm',
													cancelText:'Cancel',
													onOk:() => {
														if (room.ACTIVE){
															props.updateRoomActive(room.ROOM_UUID,0)
														}else{
															props.updateRoomActive(room.ROOM_UUID,1)
														}
														
													},
												})
											}
											}></LoginOutlined>:(<></>)
										}
										<EditTwoTone onClick={ ()=>{
											props.onChangeHOC('updateUploadImg',null)
											props.onChangeHOC('selectedRoom',room)
											console.log(room)
											showUpdateModal()
										}
										}></EditTwoTone>

										<DeleteTwoTone onClick={() => 
											Modal.confirm({
												title: 'Delete Room',
												content: 'Are you sure you want to delete '+room.ROOM_NAME+'?',
												okText:'Confirm',
												cancelText:'Cancel',
												onOk:() => {
													props.deleteRoom(room)
												},
											})
										}></DeleteTwoTone>

										{/* <ArrowRightOutlined onClick={
											() => {
												toSummary(room.ROOM_UUID)
											}
										}></ArrowRightOutlined> */}
									</Space>
								}
							>
								<div
									onClick={
										() => {
											toSummary(room.ROOM_UUID)
										}
									} 
								>
									<p>{room.INFO?room.INFO:'-'} <img id={`heart-item-${room.ID}`} src={heart} alt="Heart" style={{ display:'none', position:'absolute', right: 0, top:50,  margin: '16px',height: '30px', width: 'auto' }} /></p>
									<p>Status: <Tag>{
										room.MAC.length === 0? 'No sensor':
										room.STATUS === 0? 'Room is empty':
										room.STATUS === 1? 'Room is occupied':
										room.STATUS === 2? 'Sleeping':
										room.STATUS === 255? 'Alert':
										'Room is empty'
									}</Tag></p>
									<p>Location: <Tag>{room.ROOM_LOC}</Tag></p>
									<p>Last data: <Tag>{
										room.MAC.length === 0? '-':
										moment(room.LAST_DATA_RECEIVED).fromNow()
										}</Tag></p>
								</div>
								
							</Card>
								</>)
							}
							
						</Col>
					))
				}
			</Row>
			}
			{
				props.onLoading && <LoadingOverlay/>
			}

			{props.isAdmin && props.mapView && editMapVisible && <EditRoomOnMapModal close={closeEditMapModal} rooms={props.rooms} action={props.updateRoomLocationOnMap}/>}
			<AddRoomModal visible={addVisible} uploadImg={props.newUploadImg} close={closeAddModal} action={props.addRoom} upload={props.uploadNewImg}/>
			{ updateVisible && <UpdateRoomModal uploadImg={props.updateUploadImg} visible={updateVisible} close={closeUpdateModal} action={props.updateRoom} selectedRoom={props.selectedRoom} upload={props.uploadUpdateImg}/>}
			{ triggerAlertVisible && <TriggerAlertModal visible={triggerAlertVisible} close={closeTriggerAlertModal} action={props.triggerAlert} selectedRoom={props.selectedRoom}/>}
		</Container>
	)
}

export default WithHOC(Home)