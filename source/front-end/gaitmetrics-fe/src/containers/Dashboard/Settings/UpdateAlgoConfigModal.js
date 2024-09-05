import React from 'react';
import { Form, Input, Row, Col, Select, Modal, Button } from 'antd';

const UpdateAlgoConfigModal = (props) => {
  const [form] = Form.useForm();

  const { TextArea } = Input;

  const onFinish = (values) => {
    console.log('Received values:', values);
    let temp = [...props.algoConfigs];
    let algoConfig = temp.find(config => config.CONFIG_KEY === props.selectedKey);

    if (algoConfig) {
      algoConfig.VALUE = values.VALUE;
    } 
    props.setAlgoConfigs(temp)
    props.close()
  };

  return (
    <Modal
      title="Update"
      open={true}
      onOk={() => form.submit()}
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedAlgoConfig}
        layout="vertical" // Set the form layout
      >
        <p>Key: <span style={{fontWeight:'bold'}}>{props.selectedKey}</span></p>
        <Row gutter={16}>
          <Col span={24} lg={8}>
            <Form.Item
              label="Value"
              name="VALUE"
              rules={[{ required: true, message: 'Please enter value' }]}
            >
              <Input />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default UpdateAlgoConfigModal;