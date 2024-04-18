import { Card, Form, Button, Checkbox, Input } from 'antd'
import { useNavigate, useLocation, Link } from "react-router-dom"
import React, { useEffect } from 'react';
import { getItem, storeItem } from 'utils/tokenStore'
import WithHOC from './actions'

import logoImage from '../../assets/logo.png';
import LoadingOverlay from 'components/LoadingOverlay';

const ResetPasswordPage = (props) => {
  const navigate = useNavigate()

  useEffect(() => {
    if(getItem("LOGIN_TOKEN")){
      navigate('/dashboard')
    }
  }, [props.loggedIn])

  const location = useLocation();

  // Parsing the search string to get query parameters
  const searchParams = new URLSearchParams(location.search);
  // Accessing individual query parameters
  const user = searchParams.get('user') || ''; // Setting default value to ''
  const mode = searchParams.get('mode') || null;
  const code = searchParams.get('code') || null;

  const onSubmit = (values) => {
    if (mode == 'add'){
      props.addPassword(values,code)
    }else{
      props.resetPassword(values,code)
    }
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
            span: 10,
          }}
          wrapperCol={{
            span: 16,
          }}
          style={{
            maxWidth: 700,
          }}
          initialValues={{
            username: user,
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
            label="Confirm Password"
            name="cpassword"
            rules={[
              {
                required: true,
                message: 'Please retype your password!',
              },
            ]}
          >
            <Input.Password value={props.cpassword}/>
          </Form.Item>

          <Form.Item
            wrapperCol={{
              offset: 8,
              span: 16,
            }}
          >
            <Button type="primary" htmlType="submit">
              {
                mode == 'add'? 'Add New Password' :'Reset Password'
              }
            </Button>
          </Form.Item>

          <Form.Item
            wrapperCol={{
              offset: 8,
              span: 16,
            }}
          >
            <Link to="/">
              <Button type="default">Login</Button>
            </Link>
          </Form.Item>

        </Form>
      </Card>
      {
				props.onLoading && <LoadingOverlay/>
			}
    </div>
  )
}

export default WithHOC(ResetPasswordPage)