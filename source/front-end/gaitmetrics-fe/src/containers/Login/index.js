import { Card, Form, Button, Checkbox, Input } from 'antd'
import { useNavigate } from "react-router-dom"
import React, { useEffect } from 'react';
import { getItem, storeItem } from 'utils/tokenStore'
import WithHOC from './actions'

import logoImage from '../../assets/logo.png';
import LoadingOverlay from 'components/LoadingOverlay';

const LoginPage = (props) => {
  const navigate = useNavigate()

  useEffect(() => {
    if(getItem("LOGIN_TOKEN")){
      navigate('/dashboard')
    }
  }, [props.loggedIn])

  const onSubmit = (values) => {
    props.login(values)
  }

  return(
    <div className='d-flex justify-content-center align-items-center h-100'>
      <Card>
        <div className='m-5 d-flex justify-content-center align-items-center'>
          <img src={logoImage} alt="Logo" style={{ height: '100%' }} />
        </div>
        <Form
          name="basic"
          labelCol={{
            span: 8,
          }}
          wrapperCol={{
            span: 16,
          }}
          style={{
            maxWidth: 600,
          }}
          initialValues={{
            remember: true,
          }}
          onFinish={onSubmit}
          autoComplete="off"
        >
          <Form.Item
            label="Username"
            name="username"
            rules={[
              {
                required: true,
                message: 'Please input your username!',
              },
            ]}
          >
            <Input value={props.username}/>
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[
              {
                required: true,
                message: 'Please input your password!',
              },
            ]}
          >
            <Input.Password value={props.password}/>
          </Form.Item>

          <Form.Item
            name="remember"
            valuePropName="checked"
            wrapperCol={{
              offset: 8,
              span: 16,
            }}
          >
            <Checkbox>Remember me</Checkbox>
          </Form.Item>

          <Form.Item
            wrapperCol={{
              offset: 8,
              span: 16,
            }}
          >
            <Button type="primary" htmlType="submit">
              Login
            </Button>
          </Form.Item>
        </Form>
      </Card>
      {
				props.onLoading && <LoadingOverlay/>
			}
    </div>
  )
}

export default WithHOC(LoginPage)