import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Button, Card, Divider, InputNumber, Modal, Select, Slider, Space, Switch, Table, Typography } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import { getItem } from 'utils/tokenStore'
import { Form, Input, Row, Col, Image } from 'antd';
import getDomainURL from 'utils/api'
import _ from 'lodash'

import { FilePond, registerPlugin } from 'react-filepond'

// Import FilePond styles
import 'filepond/dist/filepond.min.css'

// Import the Image EXIF Orientation and Image Preview plugins
// Note: These need to be installed separately
// `npm i filepond-plugin-image-preview filepond-plugin-image-exif-orientation --save`
import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation'
import FilePondPluginImagePreview from 'filepond-plugin-image-preview'
import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css'
import { DeleteTwoTone, EditTwoTone } from '@ant-design/icons'
import Paho from 'paho-mqtt'
import getWebsocketServer from 'utils/websocket'
import { requestSuccess,requestError } from 'utils/requestHandler'
import UpdateAlgoConfigModal from './UpdateAlgoConfigModal'

let client = null

const Settings = props => {

	const { Title } = Typography
  const [form] = Form.useForm();
  const [enableForm] = Form.useForm();
  const [algoForm] = Form.useForm();
  const [notifierForm] = Form.useForm();
  const { TextArea } = Input;
  const [roomImg, setRoomImg] = useState('')
  const [files, setFiles] = useState([])
  const [threshold, setThreshold] = useState(2);
  const [alertConfigs,setAlertConfigs] = useState([])
  const [algoConfigs,setAlgoConfigs] = useState([])
  const [componentsEnablement,setComponentsEnablement] = useState([])
  const [dpRange, setDPRange] = useState([15,60])
  const [isActive, setIsActive] = useState(true);
  const [selectedAlgoConfig, setSelectedAlgoConfig] = useState(null)
  const [updateVisible, setUpdateVisible] = useState(false);

  const onChange = (value) => {
    console.log('onChange: ', value);
    setDPRange(value)
  };
  
  const onChangeComplete = (value) => {
    console.log('onChangeComplete: ', value);
  };

  const closeUpdateModal = () => {
    setUpdateVisible(false);
  };

  const showUpdateModal = () => {
    setUpdateVisible(true);
  };

  const onChangeThreshold = (value) => {
    if (isNaN(value)) {
      return;
    }
    setThreshold(value);
  };

  const columns = [ 
    { 
      key: "ID", 
      title: "ID", 
      render: (_, __, index) => index + 1, // Render the index as the ID, starting from 1
    },
    { 
      key: "DATA_TYPE", 
      title: "Data Type", 
      render: (temp, config) => {
        const foundObject = _.find(props.dataTypes, { value: config.DATA_TYPE });
        return foundObject ? foundObject.label : 'Value not found';
      },
    }, 
    { 
      key: "MODE", 
      title: "Mode", 
      render: (_, config) => (
        config.MODE==2?"Day of Week":"Day"
      ),
    },
    { 
      key: "MIN_DATA_POINT", 
      title: "Min Data Point", 
      dataIndex: "MIN_DATA_POINT", 
    },
    { 
      key: "MAX_DATA_POINT", 
      title: "Max Data Point", 
      dataIndex: "MAX_DATA_POINT", 
    },
    { 
      key: "THRESHOLD", 
      title: "Threshold", 
      dataIndex: "THRESHOLD", 
    },
    { 
      key: "ACT", 
      title: "Action", 
      render: (_, config) => (
        <>
        <Space>
          <DeleteTwoTone onClick={() => 
            Modal.confirm({
              title: 'Delete Device',
              content: 'Are you sure you want to delete this configuration?',
              okText:'Confirm',
              cancelText:'Cancel',
              onOk:() => {
                const newAlertConfigs = alertConfigs.filter(configs => configs !== config);
                setAlertConfigs(newAlertConfigs);
              },
            })
          }></DeleteTwoTone>
        </Space>
        </>
      ),
    },
  ] 

  const algoColumns = [ 
    { 
      key: "ID", 
      title: "ID", 
      render: (_, __, index) => index + 1, // Render the index as the ID, starting from 1
    },
    { 
      key: "CONFIG_KEY", 
      title: "Config Key", 
      dataIndex: "CONFIG_KEY", 
    },
    { 
      key: "VALUE", 
      title: "Value", 
      dataIndex: "VALUE", 
    },
    { 
      key: "ACT", 
      title: "Action", 
      render: (_, config) => (
        <>
        <Space>
          <EditTwoTone onClick={ ()=>{
            setSelectedAlgoConfig(config)
            showUpdateModal()
          }
          }></EditTwoTone>
          <DeleteTwoTone onClick={() => 
            Modal.confirm({
              title: 'Delete Device',
              content: 'Are you sure you want to delete this configuration?',
              okText:'Confirm',
              cancelText:'Cancel',
              onOk:() => {
                const newAlgoConfigs = algoConfigs.filter(configs => configs !== config);
                setAlgoConfigs(newAlgoConfigs);
              },
            })
          }></DeleteTwoTone>
        </Space>
        </>
      ),
    },
  ] 

  const componentsEnablementColumns = [ 
    { 
      key: "ID", 
      title: "ID", 
      render: (_, __, index) => index + 1, // Render the index as the ID, starting from 1
    },
    { 
      key: "PAGE", 
      title: "Page", 
      dataIndex: "PAGE", 
    },
    { 
      key: "COMPONENT", 
      title: "Component", 
      dataIndex: "COMPONENT", 
    },
    { 
      key: "USER", 
      title: "User", 
      render: (_, component) => (
        <>
        <Switch 
							style={{float:'right'}}
							className='mb-2'
							checkedChildren="Enable" 
							unCheckedChildren="Disable" 
							checked={component.USER}
							onChange={ val => {
                const temp = [...componentsEnablement]; // If it's an array
          
                // Find the target component by its ID and update the ADMIN field
                const index = temp.findIndex((item) => item.ID === component.ID);
                if (index !== -1) {
                  temp[index] = {
                    ...temp[index],
                    USER: val ? 1 : 0,
                  };
                }

                // Update state with the modified array/object
                setComponentsEnablement(temp);
              }} />
        </>
      ),
    },
    { 
      key: "ADMIN", 
      title: "Admin", 
      render: (_, component) => (
        <>
        <Switch 
							style={{float:'right'}}
							className='mb-2'
							checkedChildren="Enable" 
							unCheckedChildren="Disable" 
							checked={component.ADMIN}
							onChange={ val => {
                const temp = [...componentsEnablement]; // If it's an array
          
                // Find the target component by its ID and update the ADMIN field
                const index = temp.findIndex((item) => item.ID === component.ID);
                if (index !== -1) {
                  temp[index] = {
                    ...temp[index],
                    ADMIN: val ? 1 : 0,
                  };
                }

                // Update state with the modified array/object
                setComponentsEnablement(temp);
              }} />
        </>
      ),
    },
  ] 

  const notifierColumns = [ 
    { 
      key: "ID", 
      title: "ID", 
      render: (_, __, index) => index + 1, // Render the index as the ID, starting from 1
    },
    { 
      key: "EMAIL", 
      title: "Email", 
      dataIndex: "EMAIL", 
    },
    { 
      key: "ACT", 
      title: "Action", 
      render: (_, notifier) => (
        <>
        <Space>
          <DeleteTwoTone onClick={() => 
            Modal.confirm({
              title: 'Delete email',
              content: 'Are you sure you want to delete this email?',
              okText:'Confirm',
              cancelText:'Cancel',
              onOk:() => {
                props.deleteNotifier(notifier.EMAIL)
              },
            })
          }></DeleteTwoTone>
        </Space>
        </>
      ),
    },
  ] 

  useEffect(() => {
		if (props.selectedRoom){
      form.setFieldValue(props.selectedRoom)
      if (props.selectedRoom.IMAGE_NAME){
        setRoomImg(getDomainURL() +"/static/uploads/" +props.selectedRoom.IMAGE_NAME)
      }
    }
	}, [props.selectedRoom])

  useEffect(() => {
		if (getItem("LOGIN_TOKEN")){
			props.getDataTypes()
			props.getAlertConfigurations()
      props.getAlgoConfigurations()
      props.getNotifier()
      props.getAllComponentsEnablement()
      props.getComponentsEnablement('settings')
    }
	}, [])

  useEffect(() => {
		setAlertConfigs(props.alertConfigs)
	}, [props.alertConfigs])

  useEffect(() => {
		setComponentsEnablement(props.componentsEnablement)
	}, [props.componentsEnablement])

  useEffect(() => {
    const arrayOfDicts = Object.keys(props.algoConfigs).map(key => {
        return {
            CONFIG_KEY: key,
            VALUE: props.algoConfigs[key]
        };
    });
		setAlgoConfigs(arrayOfDicts)
	}, [props.algoConfigs])

  useEffect((()=>{
    if (files.length > 0){
      console.log(files)
      files.map(fileItem => {
        console.log(fileItem.file)
        props.upload(fileItem.file)
      })
    }
  }),[files])

  useEffect(() => {

    if (getItem("LOGIN_TOKEN") && props.client_id == null){
			props.getMQTTClientID()
		}
    
    const handleVisibilityChange = () => {
      setIsActive(!document.hidden);
    };
  }, []);

  const doFail = (e) => {
    console.error("Connection failed:", e);
  };

  useEffect(() => {
    if (getItem("LOGIN_TOKEN") && props.client_id != null && props.updateConfigFlag > 0){
			configureDevice()
		}
  }, [props.updateConfigFlag]);

  const configureDevice = () => {
    console.log("Configure... MQTT")
    publishToMQTT("UPDATED","/GMT/DEV/ALGO_CONFIG")
  }

  const publishToMQTT = (msg, topic) => {
    let message = new Paho.Message(msg);
    message.destinationName = topic;
    client.send(message);
    console.log("Publish",message,"to",topic)
  }

  const onMessageArrived = async (message) => {
    try {
      if(message.destinationName.includes("ALGO_CONFIG/R")){
        if(message.payloadString.includes("UPDATED")){
          requestSuccess(message.destinationName + ": "+ message.payloadString)
        }    
      }
      if (message.destinationName.includes("REQ/UPDATE_CONFIG")){
        requestSuccess( message.destinationName + ": "+ message.payloadString)
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
            client.subscribe("/GMT/DEV/+/DATA/+/JSON");
            client.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF");
            client.subscribe("/GMT/#");
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
  }, [isActive, props.client_id]); // Include dependencies if needed

  useEffect(() => {
    return () => {
      if (client && client.isConnected()) {
        client.disconnect();
        console.log("Disconnected from MQTT broker");
      }
    };
  }, []);

  const onFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    if (props.uploadImg == null){
      // message.success(`Please upload room image!`);
      // return
    }
    props.action(values)
    props.close()
  };

  const onAlgoFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    // props.action(values)
    // props.close()
  };

  const onEnableFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    // props.action(values)
    // props.close()
  };
  
  const clearAlertConfigs = () => {
		setAlertConfigs([])
	}

  const updateAlertConfigs = () => {
		props.setAlertConfigurations(alertConfigs)
	}

  const updateAlgoConfigs = () => {
		props.setAlgoConfigurations(algoConfigs)
	}

  const updateComponentsEnablement = () => {
		props.updateComponentsEnablement(componentsEnablement)
	}

  const addNotifier = () => {
    if (notifierForm.getFieldValue('email')!=undefined){
      const foundObject = _.find(props.notifier, { EMAIL: notifierForm.getFieldValue('email')});
      if (foundObject == undefined){
        props.addNotifier(notifierForm.getFieldValue('email'))
      }else{
        requestError("Duplicate email!")
      }
      
    }else{
      requestError("Please fill in required fields!")
    }
	}

  const addAlertConfig = () => {
    if (form.getFieldValue('mode')!=undefined && form.getFieldValue('dataType') != undefined){
      const foundObject = _.find(alertConfigs, { MODE: form.getFieldValue('mode'), DATA_TYPE: form.getFieldValue('dataType') });
      if (foundObject == undefined){
        let temp = [...alertConfigs]
        temp.push({
          "MODE":form.getFieldValue('mode'),
          "DATA_TYPE":form.getFieldValue('dataType'),
          "MIN_DATA_POINT":dpRange[0],
          "MAX_DATA_POINT":dpRange[1],
          "THRESHOLD":threshold
        }) 
        setAlertConfigs(temp)
      }else{
        requestError("Duplicate alert configuration!")
      }
      
    }else{
      requestError("Please fill in required fields!")
    }
	}

  const addAlgoConfig = () => {
    if (algoForm.getFieldValue('configKey')!=undefined && algoForm.getFieldValue('value') != undefined){
      const foundObject = _.find(algoConfigs, { CONFIG_KEY: algoForm.getFieldValue('configKey')});
      if (foundObject == undefined){
        let temp = [...algoConfigs]
        temp.push({
          "CONFIG_KEY":algoForm.getFieldValue('configKey'),
          "VALUE":algoForm.getFieldValue('value')
        }) 
        setAlgoConfigs(temp)
      }else{
        requestError("Duplicate configuration!")
      }
      
    }else{
      requestError("Please fill in required fields!")
    }
	}

	return (
		<Container>
			<Title>Settings</Title>
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedRoom}
        layout="vertical" // Set the form layout
      >
        {props.components?.organization_logo && <Row gutter={[16,16]}>
          <Col span={24}>
            <Card 
              title={ 
                <>
                  Upload Organization Logo
                </>  } 
              style={{}} 
              className='content-card'
            >
              <Col span={24}>
                <FilePond
                  files={files}
                  onupdatefiles={setFiles}
                  allowMultiple={false}
                  maxFiles={1}
                  name="files"
                  labelIdle='Drag & Drop your files or <span class="filepond--label-action">Browse</span>'
                />
              </Col>
              {
                roomImg && !props.uploadImg?<Col span={24}>
                  <Image src={roomImg} />
                </Col>: null
              }
						</Card>
          </Col>
        </Row>}

        {props.components?.alert_configurations && <Row className='mt-2' gutter={16}>
          <Col span={24}>
            <Card 
              title={ 
                <>
                  Alert Configurations
                </>  } 
              style={{}} 
              className='content-card'
            >
              <Row gutter={16}>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Data Type"
                    name="dataType"
                    rules={[{ required: true, message: 'Please select data type' }]}
                  >
                    <Select
                      options={props.dataTypes}
                      placeholder="Select data type"
                    />
                  </Form.Item>
                </Col>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Mode"
                    name="mode"
                    rules={[{ required: true, message: 'Please select mode' }]}
                  >
                    <Select
                      options={props.modes}
                      placeholder="Select mode"
                    />
                  </Form.Item>
                </Col>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Data Point (Min - Max)"
                    name="dataPoints"
                    rules={[{ required: true }]}
                  >
                    <Slider
                      range
                      step={1}
                      min={1}
                      max={80}
                      defaultValue={[15, 60]}
                      onChange={onChange}
                      onChangeComplete={onChangeComplete}
                    />
                  </Form.Item>
                </Col>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Threshold"
                    name="threshold"
                    rules={[{ required: true, message: 'Please select threshold' }]}
                  >
                    <Row>
                      <Col span={16}>
                        <Slider
                          step={0.1}
                          min={1}
                          max={4}
                          defaultValue={2}
                          onChange={onChangeThreshold}
                          value={typeof threshold === 'number' ? threshold : 2}
                        />
                      </Col>
                      <Col span={8}>
                        <InputNumber
                          step={0.1}
                          min={1}
                          max={4}
                          defaultValue={2}
                          style={{ margin: '0 0 0 16px' }}
                          value={threshold}
                          onChange={onChangeThreshold}
                        />
                      </Col>
                    </Row>
                  </Form.Item>
                </Col>

                <Col span={24} lg={8} style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    onClick={addAlertConfig}
                  >
                    Add
                  </Button>
                </Col>

              </Row>
              
              {alertConfigs.length > 0 && (
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <Table 
                    dataSource={alertConfigs} 
                    columns={columns} 
                    rowKey={"ID"}
                    pagination={{
                      // Enable pagination
                      pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
                      showSizeChanger: true, // Show the page size changer
                      defaultPageSize: 10, // Default number of items per page
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
                    }}
                  />
                </div>
              )}
              
              <div>
                <Divider/>
                <div style={{textAlign:'center'}}>
                <Space style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    onClick={updateAlertConfigs}
                  >
                    Update Configs
                  </Button>

                  <Button
                    type="default"
                    size="large"
                    onClick={clearAlertConfigs}
                  >
                    Clear
                  </Button>
                </Space>
                </div>
              </div>
						</Card>
          </Col>
        </Row>}
      </Form>

      {props.components?.algorithm_configurations && <Form
        form={algoForm}
        onFinish={onAlgoFinish}
        layout="vertical" // Set the form layout
      >
        <Row className='mt-2' gutter={16}>
          <Col span={24}>
            <Card 
              title={ 
                <>
                  Algorithm Configurations
                </>  } 
              style={{}} 
              className='content-card'
            >
              <Row gutter={16}>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Config Key"
                    name="configKey"
                    rules={[{ required: true, message: 'Please enter config key' }]}
                  >
                    <Input/>
                  </Form.Item>
                </Col>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Value"
                    name="value"
                    rules={[{ required: true, message: 'Please enter value' }]}
                  >
                    <Input type='number'/>
                  </Form.Item>
                </Col>
                
                <Col span={24} lg={8} style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    onClick={addAlgoConfig}
                  >
                    Add
                  </Button>
                </Col>

              </Row>
              
              {algoConfigs.length > 0 && (
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <Table 
                    dataSource={algoConfigs} 
                    columns={algoColumns} 
                    rowKey={"ID"}
                    pagination={{
                      // Enable pagination
                      pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
                      showSizeChanger: true, // Show the page size changer
                      defaultPageSize: 10, // Default number of items per page
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
                    }}
                  />
                </div>
              )}
              
              <div>
                <Divider/>
                <div style={{textAlign:'center'}}>
                <Space style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    onClick={updateAlgoConfigs}
                  >
                    Update Configs
                  </Button>
                </Space>
                </div>
              </div>
						</Card>
          </Col>
        </Row>
      </Form>}
      { props.components?.notifier && <Form
        form={notifierForm}
        layout="vertical" // Set the form layout
      >
        <Row className='mt-2' gutter={16}>
          <Col span={24}>
            <Card 
              title={ 
                <>
                  Notifier
                </>  } 
              style={{}} 
              className='content-card'
            >
              <Row gutter={16}>
                <Col span={24} lg={8}>
                  <Form.Item
                    label="Email"
                    name="email"
                    rules={[{ required: true, message: 'Please enter email' }]}
                  >
                    <Input/>
                  </Form.Item>
                </Col>
                
                <Col span={24} lg={8} style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    onClick={addNotifier}
                  >
                    Add
                  </Button>
                </Col>

              </Row>
              
              {props.notifier.length > 0 && (
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <Table 
                    dataSource={props.notifier} 
                    columns={notifierColumns} 
                    rowKey={"ID"}
                    pagination={{
                      // Enable pagination
                      pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
                      showSizeChanger: true, // Show the page size changer
                      defaultPageSize: 10, // Default number of items per page
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
                    }}
                  />
                </div>
              )}
            </Card>
          </Col>
        </Row>
      </Form>}
      {getItem("TYPE") == "2" && <Form
        form={enableForm}
        onFinish={onEnableFinish}
        layout="vertical" // Set the form layout
      >
        <Row className='mt-2' gutter={16}>
          <Col span={24}>
            <Card 
              title={ 
                <>
                  Component Enablement
                </>  } 
              style={{}} 
              className='content-card'
            >
              {componentsEnablement.length > 0 && (
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <Table 
                    dataSource={componentsEnablement} 
                    columns={componentsEnablementColumns} 
                    rowKey={"ID"}
                    pagination={{
                      // Enable pagination
                      pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
                      showSizeChanger: true, // Show the page size changer
                      defaultPageSize: 10, // Default number of items per page
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
                    }}
                  />
                </div>
              )}
              
              <div>
                <Divider/>
                <div style={{textAlign:'center'}}>
                <Space style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    onClick={updateComponentsEnablement}
                  >
                    Update
                  </Button>
                </Space>
                </div>
              </div>
						</Card>
          </Col>
        </Row>
      </Form>}
      { updateVisible && <UpdateAlgoConfigModal visible={updateVisible} close={closeUpdateModal} selectedKey={selectedAlgoConfig.CONFIG_KEY} selectedAlgoConfig={selectedAlgoConfig} algoConfigs={algoConfigs} setAlgoConfigs={setAlgoConfigs}/>}
			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(Settings)