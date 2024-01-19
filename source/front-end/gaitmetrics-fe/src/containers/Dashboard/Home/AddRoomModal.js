import React, { useEffect, useState } from 'react';
import { Form, Input, Row, Col, Button, Modal, message, Image } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

// Import React FilePond
import { FilePond, File, registerPlugin } from 'react-filepond'

// Import FilePond styles
import 'filepond/dist/filepond.min.css'

// Import the Image EXIF Orientation and Image Preview plugins
// Note: These need to be installed separately
// `npm i filepond-plugin-image-preview filepond-plugin-image-exif-orientation --save`
import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation'
import FilePondPluginImagePreview from 'filepond-plugin-image-preview'
import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css'

// Register the plugins
registerPlugin(FilePondPluginImageExifOrientation, FilePondPluginImagePreview)

const AddRoomModal = (props) => {
  const [form] = Form.useForm();

  const { TextArea } = Input;

  const [roomImg, setRoomImg] = useState('')

  const [files, setFiles] = useState([])

  const onFinish = (values) => {
    // Handle the form submission logic (e.g., send data to the server)
    console.log('Received values:', values);
    if (props.uploadImg == null){
      message.success(`Please upload room image!`);
      return
    }
    props.action(values)
    props.close()
  };

  useEffect((()=>{
    if (files.length > 0){
      console.log(files)
      files.map(fileItem => {
        console.log(fileItem.file)
        props.upload(fileItem.file)
      })
    }
  }),[files])

  const handleUpload = (info) => {
    // console.log(file)
    // props.upload('add-room-img',file)
    console.log(info)
    if (info.file.status !== 'uploading') {
      console.log(info.file, info.fileList);
    }
    if (info.file.status === 'done') {
      message.success(`${info.file.name} file uploaded successfully`);
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  }

  const beforeUpload = (file) => {
    // Add custom validation logic here
    const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
    if (!isJpgOrPng) {
      message.error('You can only upload JPG/PNG file!');
    }
    return isJpgOrPng;
  };

  return (
    <Modal
      title="Add Room"
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
              label="Room Name"
              name="roomname"
              rules={[{ required: true, message: 'Please enter the room name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room Location"
              name="roomlocation"
              rules={[{ required: true, message: 'Please enter the room location' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room X (Length)"
              name="length"
              rules={[{ required: true, message: 'Please enter the room length' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room Y (Width)"
              name="width"
              rules={[{ required: true, message: 'Please enter the rooom width' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="Description"
              name="description"
              // rules={[{ required: true, message: 'Please enter the description' }]}
            >
              <TextArea />
            </Form.Item>
          </Col>

          <Col span={24}>
            <Form.Item
              label="Upload Room Image"
              name="image"
              // rules={[{ required: true, message: 'Please upload room image' }]}
            >
              <FilePond
                files={files}
                onupdatefiles={setFiles}
                allowMultiple={false}
                maxFiles={1}
                name="files"
                labelIdle='Drag & Drop your files or <span class="filepond--label-action">Browse</span>'
              />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
    
  );
};

export default AddRoomModal;