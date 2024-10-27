import React from 'react';
import { Form, Input, Row, Col, Select, Modal, AutoComplete } from 'antd';

const AddDeviceModal = (props) => {
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
      title="Add Device"
      open={props.visible}
      onOk={() => form.submit()}
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        layout="vertical"
      >
        <Row gutter={16}>
          <Col span={24} lg={8}>
            <Form.Item
              label="MAC Address"
              name="macAddress"
              rules={[{ required: true, message: 'Please enter the MAC address' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Name"
              name="deviceName"
              rules={[{ required: true, message: 'Please enter the device name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: 'Please enter the device password' }]}
            >
              <Input type='password'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Position(X)"
              name="deviceposX"
              rules={[{ required: true, message: 'Please enter the device position (X)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Position(Y)"
              name="deviceposY"
              rules={[{ required: true, message: 'Please enter the device position (Y)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Position(Z)"
              name="deviceposZ"
              rules={[{ required: true, message: 'Please enter the device position (Z)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Rotation(X)"
              name="devicerotX"
              rules={[{ required: true, message: 'Please enter the device rotation (X)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Rotation(Y)"
              name="devicerotY"
              rules={[{ required: true, message: 'Please enter the device rotation (Y)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={8}>
            <Form.Item
              label="Device Rotation(Z)"
              name="devicerotZ"
              rules={[{ required: true, message: 'Please enter the device rotation (Z)' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Location"
              name="location"
              rules={[{ required: true, message: 'Please select the location' }]}
            >
              <Select
                options={props.suggestions}
                // onSearch={handleSearch}
                placeholder="Select location"
              />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Device Type"
              name="devicetype"
              rules={[{ required: true, message: 'Please select the device type' }]}
            >
              <Select>
                <Select.Option value={1}>Wall</Select.Option>
                <Select.Option value={2}>Ceiling</Select.Option>
                <Select.Option value={3}>Vital</Select.Option>
                <Select.Option value={4}>Alarm</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="Device Description"
              name="devicedescription"
              rules={[{ required: true, message: 'Please enter the device description' }]}
            >
              <TextArea />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
    
  );
};

export default AddDeviceModal;