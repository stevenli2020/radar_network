import React, { useEffect, useState } from 'react';
import { Form, Input, Col, Row, Select , Modal} from 'antd';
import _ from 'lodash'

const UpdateUserModal = (props) => {
  const [form] = Form.useForm();

  const [selectedValues, setSelectedValues] = useState([]);

  useEffect(() => {
		if (props.selectedUser){
      setSelectedValues(props.selectedUser.DEVICE_LOC)
      form.setFieldValue(props.selectedUser)
    }
	}, [props.selectedUser])

  const onFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    console.log(selectedValues)
    values.rooms = _.join(selectedValues, ',');
    props.action(values)
  };

  return (
    <Modal
      title="Update User"
      open={true}
      onOk={() => form.submit()}
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedUser}
        layout="vertical" // Set the form layout
      >
        <p>ID: <span style={{fontWeight:'bold'}}>{props.selectedUser?props.selectedUser.ID:''}</span></p>
        <p>Created Time: <span style={{fontWeight:'bold'}}>{props.selectedUser?props.selectedUser.CREATED:''}</span></p>
        <p>Last Modified Time: <span style={{fontWeight:'bold'}}>{props.selectedUser?props.selectedUser.LAST_UPDATE:''}</span></p>
        <Row gutter={16}>
          <Col span={24} lg={12}>
            <Form.Item
              label="Username"
              name="LOGIN_NAME"
              rules={[{ required: true, message: 'Please enter the username' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Full Name"
              name="FULL_NAME"
              rules={[{ required: true, message: 'Please enter the full name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Email"
              name="EMAIL"
              rules={[{ required: true, message: 'Please enter the email' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Phone"
              name="PHONE"
              rules={[{ required: true, message: 'Please enter the phone' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="User Type"
              name="TYPE"
              rules={[{ required: true, message: 'Please select the user type' }]}
            >
              <Select placeholder="Please select">
                <Select.Option value={1}>Admin</Select.Option>
                <Select.Option value={0}>User</Select.Option>
              </Select>
            </Form.Item>
          </Col>

          <Col span={24}>
            <Form.Item
              label="Assign Room"
              // name="DEVICE_LOC"
              rules={[{ required: true, message: 'Please select the assign room' }]}
            >
              <Select 
                mode="multiple"
                placeholder="Please select"
                value={selectedValues}
                onChange={setSelectedValues}
                options={props.suggestions}
              >
                {/* <Select.Option value="Admin">Admin</Select.Option>
                <Select.Option value="User">User</Select.Option> */}
              </Select>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
    
  );
};

export default UpdateUserModal;