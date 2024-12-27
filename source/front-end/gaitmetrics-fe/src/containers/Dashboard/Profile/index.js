import React, { useEffect } from 'react'
import WithHOC from './actions'
import { Avatar, Card, Descriptions, Typography } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import { getItem } from 'utils/tokenStore'
import { UserOutlined } from '@ant-design/icons'


const Profile = props => {

	const { Title } = Typography

	useEffect(() => {
		if (getItem("LOGIN_TOKEN")){
			props.getProfile()
		}
		// props.getGames()
		// console.log(props.games)
	}, [])

	const getUserType = (type) => {
    switch (type) {
      case 2:
        return "Superadmin";
      case 1:
        return "Admin";
      case 0:
        return "User";
      default:
        return "Unknown";
    }
  };

	return (
		<Container>
			<Title>Profile</Title>
			{
				props.onLoading && <LoadingOverlay/>
			}
			{props.profile && <Card
				style={{ maxWidth: 600, margin: "20px auto" }}
				title={
					<div style={{ display: "flex", alignItems: "center" }}>
						<Avatar size={64} icon={<UserOutlined />} style={{ marginRight: 16 }} />
						<span>{props.profile.FULL_NAME}</span>
					</div>
				}
			>
				<Descriptions column={1} bordered>
					<Descriptions.Item label="Email">{props.profile.EMAIL}</Descriptions.Item>
					<Descriptions.Item label="Login Name">{props.profile.LOGIN_NAME}</Descriptions.Item>
					<Descriptions.Item label="Phone">{props.profile.PHONE}</Descriptions.Item>
					<Descriptions.Item label="User Type">{getUserType(props.profile.TYPE)}</Descriptions.Item>
					<Descriptions.Item label="Created At">{props.profile.CREATED}</Descriptions.Item>
					<Descriptions.Item label="Last Updated">{props.profile.LAST_UPDATE}</Descriptions.Item>
				</Descriptions>
			</Card>}
		</Container>
	)
}

export default WithHOC(Profile)