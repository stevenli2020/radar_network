import React, { useEffect, useState } from 'react'
import moment from 'moment';
import WithHOC from './actions'
import { useNavigate } from "react-router-dom"
import { Typography, Card, Row, Col, Divider,Tag, Space, Modal, Button, Popover, Table, Image } from 'antd'
import { ArrowRightOutlined, EditTwoTone, DeleteTwoTone, PlusOutlined, AlertFilled, EditOutlined } from '@ant-design/icons'

import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import AddRoomModal from './AddRoomModal'
import UpdateRoomModal from './UpdateRoomModal'
import { getItem } from 'utils/tokenStore'
import getDomainURL from 'utils/api'

import Paho from 'paho-mqtt'

import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { color } from 'echarts';
import EditRoomOnMapModal from './EditRoomOnMapModal';

let client = null

const viewportWidthInPixels = window.innerWidth;
const viewportHeightInPixels = window.innerHeight;
const backgroundImageUrl = getDomainURL() + `/static/uploads/prison.jpg`

const Home = (props) => {
  const doFail = (e) => {
    console.error("Connection failed:", e);
  };

  const onMessageArrived = async (message) => {
    try {
      console.log("onMessageArrived:", message.payloadString, message.destinationName.split('/'), message);
      props.getRoomDetails()
    } catch (error) {
      console.error("Error processing MQTT message:", error);
    }
  };

  useEffect(() => {

		if (getItem("LOGIN_TOKEN")){
      if (JSON.parse(getItem("LOGIN_TOKEN")).TYPE == "1"){
        props.onChangeHOC('isAdmin',true)
      }
    }

    const connectToBroker = async () => {
      try {
				const clientId = JSON.parse(getItem("LOGIN_TOKEN")).ID;
        const brokerUrl = "wss://aswelfarehome.gaitmetrics.org/mqtt";  // Include the path if required
        client = new Paho.Client(brokerUrl, clientId);
				
        await client.connect({
          timeout: 3,
          onSuccess: () => {
            console.log("Connected");
            client.subscribe("/GMT/DEV/ROOM/+/ALERT");
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
  

	const [addVisible, setAddVisible] = useState(false);
	const [updateVisible, setUpdateVisible] = useState(false);
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

	const closeEditMapModal = () => {
    setEditMapVisible(false);
  };

  const showUpdateModal = () => {
    setUpdateVisible(true);
  };

	const popoverContent = (room) =>{
		return (
		<div>
			<Table 
				dataSource={room.ALERTS} 
        columns={columns} >

			</Table>
		</div>)
	}

	const roomContent = (room) =>{
		return (
		<div>
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
				moment(room.LAST_DATA_TS).add(timezoneOffset, 'minutes').fromNow()
				}</Tag></p>
		</div>)
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
      dataIndex: "TIMESTAMP"
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
						width={(60 * viewportWidthInPixels) / 100} // 60vw * 12 cols
						onLayoutChange={onLayoutChange}
						verticalCompact={false}
						isDraggable={false}
						isResizable={false}
						preventCollision={true}
						// isBounded={true} 
					>
						{
						props.rooms.filter((room) => room.x !== null && room.y !== null && room.w !== null && room.h !== null).map( room => (
							<div key={room.ID.toString()} className={`grid-item ${room.ALERTS.length > 0 ? 'red-background' : ''}`} onClick={
								() => {
									toSummary(room.ROOM_UUID)
								}
							}>
								<Popover title="Detail" content={roomContent(room)}>
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
										moment(room.LAST_DATA_TS).add(timezoneOffset, 'minutes').fromNow()
										}</Tag></p>
								</div>
								
							</Card>
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
			
		</Container>
	)
}

export default WithHOC(Home)