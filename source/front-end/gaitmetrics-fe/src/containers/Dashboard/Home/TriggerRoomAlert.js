import React, { useEffect, useState } from 'react';
import { Form, Input, Row, Col, Button, Modal, message, Image, Select } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const TriggerAlertModal = (props) => {
  const [form] = Form.useForm();

  const { TextArea } = Input;

  const onFinish = (values) => {
    console.log('Received values:', values);
    props.action(values)
    props.close()
  };

  return (
    <Modal
      title="Trigger Alert"
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
          <Col span={24} lg={12}>
          <Form.Item
              label="Urgency"
              name="urgency"
              rules={[{ required: true, message: 'Please select the urgency' }]}
            >
              <Select>
                <Select.Option value={0}>Information</Select.Option>
                <Select.Option value={1}>Attention</Select.Option>
                <Select.Option value={2}>Escalated</Select.Option>
                <Select.Option value={3}>Urgent</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="Details"
              name="details"
              rules={[{ required: true, message: 'Please enter the alert details' }]}
            >
              <TextArea />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
    
  );
};

export default TriggerAlertModal;