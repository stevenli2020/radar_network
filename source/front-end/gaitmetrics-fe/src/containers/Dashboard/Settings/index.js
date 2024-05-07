import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Typography } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import { getItem } from 'utils/tokenStore'
import { Form, Input, Row, Col, Image } from 'antd';
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

const Settings = props => {

	const { Title } = Typography
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

	useEffect(() => {
		if (getItem("LOGIN_TOKEN")){

		}
		// props.getGames()
		// console.log(props.games)
	}, [])

	return (
		<Container>
			<Title>Settings</Title>
      <Form
        form={form}
        onFinish={onFinish}
        initialValues={props.selectedRoom}
        layout="vertical" // Set the form layout
      >
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              label="Upload Organization Logo"
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
			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(Settings)