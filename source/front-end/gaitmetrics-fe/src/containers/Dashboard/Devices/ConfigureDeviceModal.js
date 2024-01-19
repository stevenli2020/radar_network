import React from 'react';
import { Form, Input, Row, Col, Select, Modal, AutoComplete } from 'antd';

const ConfigureDeviceModal = (props) => {
  const [form] = Form.useForm();

  const { TextArea } = Input;

  const onFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    props.action(values)
    props.close()
  };

  return (
    <Modal
      title="Send Device Configuration"
      open={props.visible}
      onOk={() => form.submit()}
      okText="Send"
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedDevice}
        layout="vertical"
      >
        <p>ID: <span style={{fontWeight:'bold'}}>{props.selectedDevice?props.selectedDevice.Id:''}</span></p>
        <p>Last Modified Time: <span style={{fontWeight:'bold'}}>{props.selectedDevice?props.selectedDevice["LAST DATA"]:''}</span></p>
        <Row gutter={16}>
          <Col span={24} lg={12}>
            <Form.Item
              label="MAC Address"
              name="MAC"
              rules={[{ required: true, message: 'Please enter the MAC address' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Device Name"
              name="NAME"
              rules={[{ required: true, message: 'Please enter the device name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="Device Configuration(Put ; in end of line)"
              name="CONFIGURATION"
              rules={[{ required: true, message: 'Please enter the device configuration' }]}
            >
              <TextArea />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
    
  );
};

export default ConfigureDeviceModal;