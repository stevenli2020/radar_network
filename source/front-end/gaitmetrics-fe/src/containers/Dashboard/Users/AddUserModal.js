import React, { useState } from 'react';
import { Form, Input, Modal, Row, Col, Select } from 'antd';

const AddDeviceModal = (props) => {
  const [form] = Form.useForm();
  const [userType, setUserType] = useState(null);

  const onFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    props.action(values);
    form.resetFields();
    props.close();
  };

  const handleUserTypeChange = (value) => {
    setUserType(value); // Update the user type when it changes
  };

  return (
    <Modal
      title="Add User"
      visible={props.visible}
      onOk={() => form.submit()}
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        layout="vertical" // Set the form layout
      >
        <Row gutter={16}>
          <Col span={24} lg={12}>
            <Form.Item
              label="Username"
              name="username"
              rules={[{ required: true, message: 'Please enter the username' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Full Name"
              name="fullname"
              rules={[{ required: true, message: 'Please enter the full name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Email"
              name="email"
              rules={[{ required: true, message: 'Please enter the email' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Phone"
              name="phone"
              rules={[{ required: true, message: 'Please enter the phone' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="User Type"
              name="usertype"
              rules={[{ required: true, message: 'Please select the user type' }]}
            >
              <Select placeholder="Please select" onChange={handleUserTypeChange}>
                <Select.Option value={1}>Admin</Select.Option>
                <Select.Option value={0}>User</Select.Option>
              </Select>
            </Form.Item>
          </Col>

          {userType === 0 && (
            <Col span={24}>
              <Form.Item
                label="Assign Room"
                name="assignroom"
                rules={[{ message: 'Please select the assign room' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="Please select"
                  options={props.suggestions}
                />
              </Form.Item>
            </Col>
          )}
        </Row>
      </Form>
    </Modal>
  );
};

export default AddDeviceModal;