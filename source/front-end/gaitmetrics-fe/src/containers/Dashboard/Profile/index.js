import React, { useEffect } from 'react'
import WithHOC from './actions'
import { Typography } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import { getItem } from 'utils/tokenStore'


const Profile = props => {

	const { Title } = Typography

	useEffect(() => {
		if (getItem("LOGIN_TOKEN")){

		}
		// props.getGames()
		// console.log(props.games)
	}, [])

	return (
		<Container>
			<Title>Profile Page</Title>
			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(Profile)