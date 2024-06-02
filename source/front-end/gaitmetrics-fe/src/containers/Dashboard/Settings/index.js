import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Button, Card, Divider, InputNumber, Modal, Select, Slider, Space, Table, Typography } from 'antd'
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
import { DeleteTwoTone } from '@ant-design/icons'
import { requestError } from 'utils/requestHandler'

const Settings = props => {

	const { Title } = Typography
  const [form] = Form.useForm();
  const { TextArea } = Input;
  const [roomImg, setRoomImg] = useState('')
  const [files, setFiles] = useState([])
  const [threshold, setThreshold] = useState(2);
  const [alertConfigs,setAlertConfigs] = useState([])
  const [dpRange, setDPRange] = useState([15,60])

  const onChange = (value) => {
    console.log('onChange: ', value);
    setDPRange(value)
  };
  
  const onChangeComplete = (value) => {
    console.log('onChangeComplete: ', value);
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
    }
	}, [])

  useEffect(() => {
		setAlertConfigs(props.alertConfigs)
	}, [props.alertConfigs])

  useEffect((()=>{
    if (files.length > 0){
      console.log(files)
      files.map(fileItem => {
        console.log(fileItem.file)
        props.upload(fileItem.file)
      })
    }
  }),[files])

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
  
  const clearAlertConfigs = () => {
		setAlertConfigs([])
	}

  const updateAlertConfigs = () => {
		props.setAlertConfigurations(alertConfigs)
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

	return (
		<Container>
			<Title>Settings</Title>
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedRoom}
        layout="vertical" // Set the form layout
      >
        <Row gutter={[16,16]}>
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
        </Row>

        <Row className='mt-2' gutter={16}>
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
        </Row>
      </Form>
			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(Settings)