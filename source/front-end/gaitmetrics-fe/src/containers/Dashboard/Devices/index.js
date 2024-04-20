import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Table, Typography, Button, Row, Col, Modal, Space } from 'antd'
import { PlusOutlined, CheckCircleFilled,CloseCircleFilled, EditTwoTone, DeleteTwoTone, SettingTwoTone } from '@ant-design/icons'
import LoadingOverlay from 'components/LoadingOverlay'

import AddDeviceModal from './AddDeviceModal'
import UpdateDeviceModal from './UpdateDeviceModal'
import { Container } from 'react-bootstrap'
import ConfigureDeviceModal from './ConfigureDeviceModal'

import { getItem } from 'utils/tokenStore'

import Paho from 'paho-mqtt'
import { requestSuccess } from 'utils/requestHandler'

let client = null

const Devices = props => {

  const [deviceConfMac,setDeviceMac] = useState(null)
  const [isActive, setIsActive] = useState(true);

  useEffect(() => {

    if (props.client_id == null){
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

  const configureDevice = (device) => {
    setDeviceMac(device.MAC)
    console.log("Configure... MQTT")
    setConfigureVisible(false)
    publishToMQTT(device.CONFIGURATION,"/GMT/DEV/"+device.MAC+"/C/SAVECFG")
  }

  const publishToMQTT = (msg, topic) => {
    let message = new Paho.Message(msg);
    message.destinationName = topic;
    client.send(message);
  }

  const onMessageArrived = async (message) => {
    try {
      if(message.destinationName.includes("DECODE_PUBLISH/R")){
        if(!message.payloadString.includes("CONNECTED")){
          requestSuccess("Process Status: "+ message.payloadString)
        }    
      }
      if(deviceConfMac){
        if(message.destinationName.includes(`GMT/DEV/${deviceConfMac}/R`)){
          requestSuccess("Process Status: "+ message.payloadString)
        }
      }

    } catch (error) {
      console.error("Error processing MQTT message:", error);
    }
  };

  useEffect(() => {
    const connectToBroker = async () => {
      try {
        const clientId = props.client_id;
        const brokerUrl = "wss://aswelfarehome.gaitmetrics.org/mqtt";  // Include the path if required
        client = new Paho.Client(brokerUrl, clientId);
        
        await client.connect({
          timeout: 3,
          onSuccess: () => {
            console.log("Connected");
            client.subscribe("/GMT/DEV/+/DATA/+/JSON");
            client.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF");
            client.subscribe("/GMT/#");
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
  }, [deviceConfMac,isActive, props.client_id]); // Include dependencies if needed

  const [addVisible, setAddVisible] = useState(false);
  const [updateVisible, setUpdateVisible] = useState(false);
  const [configureVisible, setConfigureVisible] = useState(false);

  const timezoneOffset = new Date().getTimezoneOffset();

  const columns = [ 
    { 
      key: "Id", 
      title: "ID", 
      dataIndex: "Id",
      sorter: (a, b) => a.Id - b.Id, 
    }, 
    { 
      key: "MAC", 
      title: "MAC", 
      dataIndex: "MAC", 
    }, 
    { 
      key: "NAME", 
      title: "Name", 
      dataIndex: "NAME", 
    },
    { 
      key: "ROOM_NAME", 
      title: "Location", 
      dataIndex: "ROOM_NAME", 
    },
    { 
      key: "TYPE", 
      title: "Type", 
      render: (_, device) => (
        device.TYPE==="1"?('Wall'):
        device.TYPE==="2"?('Ceil'):
        device.TYPE==="3"?('Vital'):  ('None')
      ),
    },
    { 
      key: "STATUS", 
      title: "Status", 
      render: (_, device) => (
          device.STATUS!=="DISCONNECTED"?(
            <CheckCircleFilled style={{color:'green'}} />):(
              <CloseCircleFilled style={{color:'red'}} />)
      ),
    },
    { 
      key: "POS", 
      title: "Position (X, Y, Z)", 
      render: (_, device) => (
        <>{device.DEPLOY_X}, {device.DEPLOY_Y}, {device.DEPLOY_Z}</>
      ),
    },
    { 
      key: "ROT", 
      title: "Rotation", 
      render: (_, device) => (
        <>{device.ROT_X}, {device.ROT_Y}, {device.ROT_Z}</>
      ),
    },
    { 
      key: "MOD", 
      title: "Last Modified", 
      render: (_, device) => (
        <>{device["LAST DATA"]}</>
      ),
    },
    { 
      key: "DESCRIPTION", 
      title: "Description", 
      dataIndex: "DESCRIPTION", 
    },
    { 
      key: "ACT", 
      title: "Action", 
      render: (_, device) => (
        <>
        <Space>
          <EditTwoTone onClick={() => {
            console.log(device)
              props.onChangeHOC('selectedDevice',device)
              showUpdateModal()
            }
          }></EditTwoTone>

          <DeleteTwoTone onClick={() => 
            Modal.confirm({
              title: 'Delete Device',
              content: 'Are you sure you want to delete '+device.NAME+'?',
              okText:'Confirm',
              cancelText:'Cancel',
              onOk:() => {
                props.deleteDevice(device)
              },
            })
          }></DeleteTwoTone>

          <SettingTwoTone onClick={() => {
              props.onChangeHOC('selectedDevice',device)
              showConfigureModal()
            }
          }></SettingTwoTone>
        </Space>
          
        </>
        
      ),
    },
  ] 

  const { Title } = Typography

  const showAddModal = () => {
    setAddVisible(true);
  };

  const closeAddModal = () => {
    setAddVisible(false);
  };

  const showConfigureModal = () => {
    setConfigureVisible(true);
  };

  const closeConfigureModal = () => {
    setConfigureVisible(false);
  };

  const closeUpdateModal = () => {
    setUpdateVisible(false);
  };

  const showUpdateModal = () => {
    setUpdateVisible(true);
  };

	useEffect(() => {
    if (getItem("LOGIN_TOKEN")){
      props.getDevices()
      props.suggestRoom('')
    }
    
	}, [])

  useEffect(() => {
		if (props.client_id){
			props.setClientConnection(props.client_id)
			let intervalId;
      const startInterval = () => {
        intervalId = setInterval(() => {
          props.setClientConnection(props.client_id)
        }, 1000 * 60 * 2); // Adjust the interval time as needed
      };
      startInterval();
		}
  }, [props.client_id]);

	return (
		<Container>
      <Row style={{alignItems: 'center' }}>
        <Col sm={12}>
          <Title>List of Devices</Title> 
        </Col>
        <Col sm={12}>
          <Button
            type="primary"
            size="large"
            icon={<PlusOutlined />}
            style={{ background: '#1890ff', borderColor: '#1890ff', float:'right' }}
            onClick={showAddModal}
          >
            Add Device
          </Button>
        </Col>
      </Row>
      
			<Table 
        dataSource={props.devices} 
        columns={columns} 
        rowKey={"Id"}
        pagination={{
          // Enable pagination
          pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
          showSizeChanger: true, // Show the page size changer
          defaultPageSize: 10, // Default number of items per page
          showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
        }}
      />
			{
				props.onLoading && <LoadingOverlay/>
			}

      <AddDeviceModal visible={addVisible} action={props.registerDevice} close={closeAddModal} suggestions={props.roomSuggestions} />
      { updateVisible && <UpdateDeviceModal visible={updateVisible} action={props.updateDevice} close={closeUpdateModal} selectedDevice={props.selectedDevice} suggestions={props.roomSuggestions}/>}
      { configureVisible && <ConfigureDeviceModal visible={configureVisible} action={configureDevice} close={closeConfigureModal} selectedDevice={props.selectedDevice}/>}
    </Container>
	)
}

export default WithHOC(Devices)