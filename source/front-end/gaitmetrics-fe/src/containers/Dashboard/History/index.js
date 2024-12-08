import React, { useEffect, useState, useRef } from 'react'
import WithHOC from './actions'
import { Typography, Row, Col, Button } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import ReactECharts from 'echarts-for-react';
import { Container } from 'react-bootstrap';
import { useSearchParams, useNavigate } from 'react-router-dom';
import LocationHistory from './LocationHistory';
import RealtimeLocation from './RealtimeLocation';
import VitalSign from './VitalSign';
import OccupancyHistory from './OccupancyHistory';

import { getItem } from 'utils/tokenStore'
import getWebsocketServer from 'utils/websocket'
import AlertsModal from '../Summary/AlertsModal';
import Paho from 'paho-mqtt'
import WallSign from './WallSign';


const dashCircleFill = 'path://M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7z'
const arrowUpCircleFill = 'path://M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V11.5z'
const arrowRightCircleFill = 'path://M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V11.5z'
const arrowLeftCircleFill = 'path://M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 7.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z'
const arrowDownCircleFill = 'path://M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v5.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V4.5z'
const arrowDownLeftCircleFill = "path://M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-5.904-2.803a.5.5 0 1 1 .707.707L6.707 10h2.768a.5.5 0 0 1 0 1H5.5a.5.5 0 0 1-.5-.5V6.525a.5.5 0 0 1 1 0v2.768l4.096-4.096z"
const arrowDownRightCircleFill = 'path://M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm5.904-2.803a.5.5 0 1 0-.707.707L9.293 10H6.525a.5.5 0 0 0 0 1H10.5a.5.5 0 0 0 .5-.5V6.525a.5.5 0 0 0-1 0v2.768L5.904 5.197z'
const arrowUpLeftCircleFill = 'path://M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-5.904 2.803a.5.5 0 1 0 .707-.707L6.707 6h2.768a.5.5 0 1 0 0-1H5.5a.5.5 0 0 0-.5.5v3.975a.5.5 0 0 0 1 0V6.707l4.096 4.096z'
const arrowUpRightCircleFill = 'path://M0 8a8 8 0 1 0 16 0A8 8 0 0 0 0 8zm5.904 2.803a.5.5 0 1 1-.707-.707L9.293 6H6.525a.5.5 0 1 1 0-1H10.5a.5.5 0 0 1 .5.5v3.975a.5.5 0 0 1-1 0V6.707l-4.096 4.096z'


let client = null

const History = props => {

  const [alertVisible, setAlertVisible] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const [isActive, setIsActive] = useState(true);
  const navigate = useNavigate()

  const hasFetchedData = useRef(false);

  useEffect(() => {

    if (getItem("LOGIN_TOKEN") && props.client_id == null){
			props.getMQTTClientID()
      props.getComponentsEnablement('history')
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
      let mac = message.destinationName.split("/");
      let destination = message.destinationName.split('/')

      if (destination[destination.length-1] == "ALERT"){
				props.getRoomAlerts(props.room_uuid)
			}else{
        let data
        if ("DATA" in JSON.parse(message.payloadString)) {
          data = JSON.parse(message.payloadString).DATA;
        } else {
          data = JSON.parse(message.payloadString);
        }

        var num = 0;

        if (data.length > 0 && (props.macPos == mac[3] || props.macVital == mac[3])) {
          let timer = 1000;
          timer = parseInt(3000 / data.length);
          
          if("heartRate" in data[num]){
            data.forEach(d => {
              if("heartRate" in d)
                if(d.heartRate != "-" && d.heartRate != null){
                  props.addVitalData(d.heartRate, d.breathRate)   
                }
            })
          }
          
          if("numSubjects" in data[num]){
            let index = 0;
            let interval = setInterval(
              function () {        
                if (parseInt(data[index]["numSubjects"]) > 0) { 
                  let persons = []
                  let object_list = []
  
                  for (let i = 0 ; i < data.length ; i++){
                    if (object_list.includes(data[i].trackIndex) || (data[i].trackIndex == null )){
                      continue
                    }
  
                    let defaultSymbol = dashCircleFill
  
                    object_list.push(data[i].trackIndex)
  
                    if(data[i].velX == 0 && data[i].velY == 0)
                      defaultSymbol = dashCircleFill
                    else if(data[i].velX == 0 && data[i].velY > 0)
                      defaultSymbol = arrowUpCircleFill
                    else if(data[i].velX == 0 && data[i].velY < 0)
                      defaultSymbol = arrowDownCircleFill
                    else if(data[i].velX > 0 && data[i].velY == 0)
                      defaultSymbol = arrowRightCircleFill
                    else if(data[i].velX > 0 && data[i].velY > 0)
                      defaultSymbol = arrowUpRightCircleFill
                    else if(data[i].velX > 0 && data[i].velY < 0)
                      defaultSymbol = arrowDownRightCircleFill
                    else if(data[i].velX < 0 && data[i].velY == 0)
                      defaultSymbol = arrowLeftCircleFill
                    else if(data[i].velX < 0 && data[i].velY > 0)
                      defaultSymbol = arrowUpLeftCircleFill
                    else if(data[i].velX < 0 && data[i].velY < 0)
                      defaultSymbol = arrowDownLeftCircleFill
                    
                    persons.push({
                      tooltip: {
                        showDelay: 0,
                        formatter: function (params) {
                          if (params.value.length > 1) {
                            return (
                              params.seriesName +" :<br/>" +params.value[0] +"m " +params.value[1] +"m "
                            );
                          } else {
                            return (
                              params.seriesName +" :<br/>" +params.name +" : " +params.value +"m "
                            );
                          }
                        },
                        axisPointer: {
                          show: true,
                          type: "cross",
                          lineStyle: {
                            type: "dashed",
                            width: 1,
                          },
                        },
                      },
                      name: "Person ID:" + String(data[i].trackIndex),
                      type: "scatter",
                      symbol: defaultSymbol,
                      symbolSize: 30,
                      data: [
                        [
                          Math.abs((data[i].posX??0).toFixed(2)),
                          Math.abs((data[i].posY??0).toFixed(2)),
                        ],
                      ],
                      itemStyle: {
                        color: function () {
                          if (!("state" in data[i]) || data[i].state == null || data[i].state == "None") {
                            return '#080808';
                          } else if (data[i].state == "Moving") {
                            return '#f8fc03'; 
                          } else if (data[i].state == "Upright") {
                            return '#0918e3'; 
                          } else if (data[i].state == "Laying") {
                            return '#8d61be'; 
                          } else if (data[i].state == "Fall") {
                            return '#fc0303'; 
                          } else if (data[i].state == "Social") {
                            return '#20fc03'; 
                          } 
                        },
                      },        
                    });
                  }
                  
                  props.updatePersonsLocation(persons)
                }
              index++;
              if (index == data.length) {
                clearInterval(interval);
              }
            }, timer);
          }
        }
      }
      
      
    } catch (error) {
      console.error("Error processing MQTT message:", error);
    }
  };

  const closeAlertModal = () =>{
		setAlertVisible(false)
	}

  useEffect(() => {
		if (props.receivedAlert > 0 && props.alerts.length > 0 && getItem("LOGIN_TOKEN")){
			setAlertVisible(true)
		}
	},[props.receivedAlert,props.alerts])

  useEffect(() => {
    const connectToBroker = async () => {
      try {
        const userId = props.client_id;
        const clientId = `${userId}`;
        const brokerUrl = getWebsocketServer();  // Include the path if required
        client = new Paho.Client(brokerUrl, clientId);
        
        await client.connect({
          timeout: 3,
          onSuccess: () => {
            console.log("Connected");
            client.subscribe("/GMT/DEV/+/DATA/+/JSON");
            client.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF");
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

    
  }, [props.sensors,isActive, props.client_id]); // Include dependencies if needed

  useEffect(() => {
    return () => {
      if (client && client.isConnected()) {
        client.disconnect();
        console.log("Disconnected from MQTT broker");
      }
    };
  }, []);

  const navigateTo = () =>{
		navigate('/dashboard/summary?roomId='+props.room_uuid)
	}

	useEffect(() => {
    if (getItem("LOGIN_TOKEN") && getItem("TYPE")){
      if (getItem("TYPE") == "1" || getItem("TYPE") == "2"){
        props.onChangeHOC("is_admin",true)
      }

      if (hasFetchedData.current) return;
      hasFetchedData.current = true;

      props.initView(searchParams.get("roomId"))
    }
	}, [])

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

	const { Title } = Typography

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
						<Title>History ({props.room_name})</Title> 
					</Col>
					<Col sm={12}>
						<Button
							type="default"
							size="large"
							style={{ float:'right' }}
							onClick={navigateTo}
						>
							Summary
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
        <Row gutter={[16, 16]} style={{justifyContent:'center'}}>
          {
            props.components?.realtime_location && <Col span={24} lg={12}>
              <RealtimeLocation is_admin={props.is_admin} room={props.room} room_empty={props.room_empty} sensors={props.sensors} persons={props.persons} data={props.realtimeLocationData}/>
            </Col>
          }
          {
            props.components?.location_history && <Col span={24} lg={12}>
              <LocationHistory is_admin={props.is_admin} action={props.getLocationHistory} macPos={props.macPos} macVital={props.macVital} room={props.room} data={props.locationHistoryData}/>
            </Col>
          }
        </Row>
        <Row gutter={[16, 16]} className='mt-2'>
          {
            props.components?.vital_sign && <Col span={24} lg={12}>
              <VitalSign action={props.getVitalHistory} macPos={props.macPos} macVital={props.macVital} vital_data={props.vital_data} room_uuid={props.room_uuid} data={props.vitalHistoryData}/>
            </Col>
          }
          {
            props.components?.occupancy_history && <Col span={24} lg={12}>
              <OccupancyHistory data={props.occupancyHistoryData}/>
            </Col>
          }
        </Row>
        <Row gutter={[16, 16]} className='mt-2'>
          {
            props.components?.wall_data && <Col span={24} lg={12}>
              <WallSign action={props.getWallHistory} room_uuid={props.room_uuid} data={props.wallHistoryData}/>
            </Col>
          }
        </Row>
      </div>
    }
			{alertVisible && <AlertsModal visible={alertVisible} action={props.readAlert} close={closeAlertModal} alerts={props.alerts} setAlertAccuracy={props.setAlertAccuracy}></AlertsModal>}
			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(History)