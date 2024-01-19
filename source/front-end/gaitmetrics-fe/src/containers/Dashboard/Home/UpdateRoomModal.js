import React, { useEffect, useState } from 'react';
import { Form, Input, Row, Col, Modal, message, Image } from 'antd';
import getDomainURL from 'utils/api'

import { FilePond, registerPlugin } from 'react-filepond'

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

const UpdateRoomModal = (props) => {
  const [form] = Form.useForm();

  const { TextArea } = Input;

  const [roomImg, setRoomImg] = useState('')
  const [files, setFiles] = useState([])

  useEffect(() => {
		if (props.selectedRoom){
      form.setFieldValue(props.selectedRoom)
      if (props.selectedRoom.IMAGE_NAME){
        setRoomImg(getDomainURL() +"/static/uploads/" +props.selectedRoom.IMAGE_NAME)
      }
    }
	}, [props.selectedRoom])

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

  const beforeUpload = (file) => {
    // Add custom validation logic here
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('You can only upload image files!');
    }
    return isImage;
  };

  return (
    <Modal
      title="Update Room"
      open={true}
      onOk={() => form.submit()}
      onCancel={props.close}
    >
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedRoom}
        layout="vertical" // Set the form layout
      >
        <Row gutter={16}>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room Name"
              name="ROOM_NAME"
              rules={[{ required: true, message: 'Please enter the room name' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room Location"
              name="ROOM_LOC"
              rules={[{ required: true, message: 'Please enter the room location' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room X (Length)"
              name="ROOM_X"
              rules={[{ required: true, message: 'Please enter the room length' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24} lg={12}>
            <Form.Item
              label="Room Y (Width)"
              name="ROOM_Y"
              rules={[{ required: true, message: 'Please enter the rooom width' }]}
            >
              <Input type='number'/>
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              label="Description"
              name="INFO"
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

          {
            roomImg && !props.uploadImg?<Col span={24}>
              <Image src={roomImg} />
            </Col>: null
          }
        </Row>
      </Form>
    </Modal>
  );
};

export default UpdateRoomModal;