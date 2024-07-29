import React from 'react';
import { Form, Input, Row, Col, Select, Modal, Button } from 'antd';

const UpdateDeviceModal = (props) => {
  const [form] = Form.useForm();

  const { TextArea } = Input;

  const onFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    props.action(values)
    props.close()
  };

  const setConfig = () =>{
    var flag = props.selectedDevice.CONFIG_SWITCH
    if (flag == 0){
      flag = 1
    }else{
      flag = 0
    }
    props.setDeviceConfig(props.selectedDevice.MAC,flag)
  }

  return (
    <Modal
      title="Update Device"
      open={true}
      onOk={() => form.submit()}
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedDevice}
        layout="vertical" // Set the form layout
      >
        <p>ID: <span style={{fontWeight:'bold'}}>{props.selectedDevice?props.selectedDevice.Id:''}</span></p>
        <p>Last Modified Time: <span style={{fontWeight:'bold'}}>{props.selectedDevice?new Date(props.selectedDevice["LAST DATA"]).toLocaleString():''}</span></p>
        <Row gutter={16}>
          <Col span={24} lg={8}>
            <Form.Item
              label="MAC Address"
              name="MAC"
              rules={[{ required: true, message: 'Please enter the MAC address' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Name"
              name="NAME"
              rules={[{ required: true, message: 'Please enter the device name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            {/* <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: 'Please enter the device password' }]}
            >
              <Input type='password'/>
            </Form.Item> */}
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Position(X)"
              name="DEPLOY_X"
              rules={[{ required: true, message: 'Please enter the device position (X)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Position(Y)"
              name="DEPLOY_Y"
              rules={[{ required: true, message: 'Please enter the device position (Y)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Position(Z)"
              name="DEPLOY_Z"
              rules={[{ required: true, message: 'Please enter the device position (Z)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Rotation(X)"
              name="ROT_X"
              rules={[{ required: true, message: 'Please enter the device rotation (X)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Rotation(Y)"
              name="ROT_Y"
              rules={[{ required: true, message: 'Please enter the device rotation (Y)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Rotation(Z)"
              name="ROT_Z"
              rules={[{ required: true, message: 'Please enter the device rotation (Z)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Location"
              name="ROOM_NAME"
              rules={[{ required: true, message: 'Please select the location' }]}
            >
              <Select
                options={props.suggestions}
                placeholder="Select location"
              />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Device Type"
              name="TYPE"
              rules={[{ required: true, message: 'Please select the device type' }]}
            >
              <Select>
                <Select.Option value="1">Wall</Select.Option>
                <Select.Option value="2">Ceiling</Select.Option>
                <Select.Option value="3">Vital</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="Device Description"
              name="DESCRIPTION"
              rules={[{ required: true, message: 'Please enter the device description' }]}
            >
              <TextArea />
            </Form.Item>
          </Col>

          <Col span={24}>
            <Button
              type="primary"
              size="large"
              onClick={setConfig}
            >
              {props.selectedDevice.CONFIG_SWITCH==0?'Turn On Config':'Turn Off Config'}
            </Button>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default UpdateDeviceModal;