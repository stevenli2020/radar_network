import React, { useEffect, useState } from 'react'
import WithHOC from './actions'
import { Table, Switch, Typography, Row, Col, Space, Button, Modal, Tag } from 'antd'
import { PlusOutlined, EditTwoTone, DeleteTwoTone, MailTwoTone } from '@ant-design/icons'
import LoadingOverlay from 'components/LoadingOverlay'
import AddUserModal from './AddUserModal'
import UpdateUserModal from './UpdateUserModal'
import { Container } from 'react-bootstrap'
import { getItem } from 'utils/tokenStore'

const Users = props => {

	const { Title } = Typography
	const [ isAdminTable, setIsAdminTable ] = useState(false)
	const [ addVisible, setAddVisible ] = useState(false);
  const [ updateVisible, setUpdateVisible ] = useState(false);

	const timezoneOffset = new Date().getTimezoneOffset();

	const admin_columns = [ 
		{ 
			key: "ID", 
			title: "ID", 
			dataIndex: "ID", 
			sorter: (a, b) => a.ID - b.ID, 
		}, 
		{ 
			key: "LOGIN_NAME", 
			title: "Login Name", 
			dataIndex: "LOGIN_NAME", 
		}, 
		{ 
			key: "FULL_NAME", 
			title: "Full Name", 
			dataIndex: "FULL_NAME", 
		}, 
		{ 
			key: "EMAIL", 
			title: "Email", 
			dataIndex: "EMAIL", 
		}, 
		{ 
			key: "PHONE", 
			title: "Phone", 
			dataIndex: "PHONE", 
		}, 
		{ 
			key: "STATUS", 
			title: "Status", 
			render: (_, user) => (
        user.STATUS===0?('Register'):
        user.STATUS===1?('Add Password'):
        user.STATUS===2?('Login'):  
				user.STATUS===3?('Logout'): ('')
      ),
		}, 
		{ 
			key: "CREATED", 
			title: "Created", 
			render: (_, user) => (
        <>{new Date(user["CREATED"]).toLocaleString()}</>
      ),
		}, 
		{ 
			key: "LAST_UPDATE", 
			title: "Last Modified", 
			render: (_, user) => (
        <>{user["LAST_UPDATE"]}</>
      ),
		}, 
		{ 
      title: "Action", 
      render: (_, user) => (
        <>
        <Space>
          <EditTwoTone onClick={() => {
						props.onChangeHOC('selectedUser',user)
						showUpdateModal()
					}
            // dispatch(add(game))
          }></EditTwoTone>

          <DeleteTwoTone onClick={() => 
            Modal.confirm({
              title: 'Delete User',
              content: 'Are you sure you want to delete '+user.FULL_NAME+'?',
              okText:'Confirm',
              cancelText:'Cancel',
              onOk:() => {
                props.deleteUser(user)
              },
            })
          }></DeleteTwoTone>

          <MailTwoTone onClick={() => 
            Modal.confirm({
              title: 'Reset User Password',
              content: 'Sent reset password link to user email?',
              okText:'Send',
              cancelText:'Cancel',
              onOk:() => {
                props.resetPassword(user)
              },
            })
          }></MailTwoTone>
        </Space>
          
        </>
        
      ),
    },
	]
	const user_columns = [ 
		{ 
			key: "ID", 
			title: "ID", 
			dataIndex: "ID", 
			sorter: (a, b) => a.ID - b.ID, 
		}, 
		{ 
			key: "LOGIN_NAME", 
			title: "Login Name", 
			dataIndex: "LOGIN_NAME", 
		}, 
		{ 
			key: "FULL_NAME", 
			title: "Full Name", 
			dataIndex: "FULL_NAME", 
		}, 
		{ 
			key: "EMAIL", 
			title: "Email", 
			dataIndex: "EMAIL", 
		}, 
		{ 
			key: "PHONE", 
			title: "Phone", 
			dataIndex: "PHONE", 
		}, 
		{ 
			key: "STATUS", 
			title: "Status", 
			render: (_, user) => (
        user.STATUS===0?('Register'):
        user.STATUS===1?('Add Password'):
        user.STATUS===2?('Login'):  
				user.STATUS===3?('Logout'): ('')
      ),
		}, 
		{ 
			key: "CREATED", 
			title: "Created", 
			render: (_, user) => (
        <>{new Date(user["CREATED"]).toLocaleString()}</>
      ),
		}, 
		{ 
			key: "ROOM_NAME",
			title: "Assign Room", 
			render: (_, user) => (
				<>
					{user["ROOM_NAME"]!==undefined && user["ROOM_NAME"]?user["ROOM_NAME"].split(",").map((data, index) => {
						return (
							<Tag color={"geekblue"}>
								{data}
							</Tag>
						);
					}):''}
				</>
			),
		}, 
		{ 
      title: "Action", 
      render: (_, user) => (
        <>
        <Space>
          <EditTwoTone onClick={() => {
						let selectedUser = user;
						if (typeof selectedUser.ROOM_NAME === 'string'){
							selectedUser.DEVICE_LOC = selectedUser.ROOM_NAME.split(",")
						}else if (selectedUser.ROOM_NAME == null){
							selectedUser.DEVICE_LOC = []
						}
						
						props.onChangeHOC('selectedUser',selectedUser)
            showUpdateModal()
					}
            // dispatch(add(game))
          }></EditTwoTone>

          <DeleteTwoTone onClick={() => 
            Modal.confirm({
              title: 'Delete User',
              content: 'Are you sure you want to delete '+user.FULL_NAME+'?',
              okText:'Confirm',
              cancelText:'Cancel',
              onOk:() => {
                props.deleteUser(user)
              },
            })
          }></DeleteTwoTone>

          <MailTwoTone onClick={() => 
            Modal.confirm({
              title: 'Reset User Password',
              content: 'Sent reset password link to user email?',
              okText:'Send',
              cancelText:'Cancel',
              onOk:() => {
                props.resetPassword(user)
              },
            })
          }></MailTwoTone>
        </Space>
          
        </>
        
      ),
    },
	]

	const showAddModal = () => {
    setAddVisible(true);
  };

	const closeAddModal = () => {
    setAddVisible(false);
  };

  const closeUpdateModal = () => {
    setUpdateVisible(false);
  };

  const showUpdateModal = () => {
    setUpdateVisible(true);
  };

  const handleUpdateCancel = () => {
    setUpdateVisible(false);
  };

  const handleUpdateOk = () => {
    setUpdateVisible(false);
  };

	useEffect(() => {
		if (getItem("LOGIN_TOKEN")){
			props.getUsers()
			props.suggestRoom('')
    }
	}, [])

	return (
		<Container>
			<Row style={{alignItems: 'center' }}>
				<Col span={12}>
					<Space>
						<Title>List of {isAdminTable?'Admins':'Users'}</Title>
						<Switch 
							style={{float:'right'}}
							className='mb-2'
							checkedChildren="Admins" 
							unCheckedChildren="Users" 
							checked={isAdminTable}
							onChange={ val => setIsAdminTable(val)} />
					</Space>
				</Col>
				<Col span={12}>
					<Button
            type="primary"
            size="large"
            icon={<PlusOutlined />}
            style={{ background: '#1890ff', borderColor: '#1890ff', float:'right' }}
            onClick={showAddModal}
          >
            Add {isAdminTable?'Admin':'User'}
          </Button>
				</Col>
				
			</Row>
			
				{
					isAdminTable ? (
						<Table id='adminTable' dataSource={props.admins} columns={admin_columns} rowKey="ID"
						pagination={{
							// Enable pagination
							pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
							showSizeChanger: true, // Show the page size changer
							defaultPageSize: 10, // Default number of items per page
							showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
						}}/>
					) : 
					(<Table id='userTable' dataSource={props.users} columns={user_columns} rowKey="ID"
					pagination={{
						// Enable pagination
						pageSizeOptions: ['10', '20', '50'], // Specify the available page sizes
						showSizeChanger: true, // Show the page size changer
						defaultPageSize: 10, // Default number of items per page
						showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`, // Display total number of items
					}}/>)
				}
			{
				props.onLoading && <LoadingOverlay/>
			}

			<AddUserModal visible={addVisible} action={props.registerUser} close={closeAddModal} rooms={props.rooms} suggestions={props.roomSuggestions} />
			{ updateVisible && <UpdateUserModal visible={updateVisible} action={props.updateUser} close={closeUpdateModal} selectedUser={props.selectedUser} rooms={props.rooms} suggestions={props.roomSuggestions} />}
		</Container>
	)
}

export default WithHOC(Users)