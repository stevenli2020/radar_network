import React, { useEffect,useState } from 'react'
import WithHOC from './actions'
import { Typography, Image, Button, Row, Col, Space } from 'antd'
import LoadingOverlay from 'components/LoadingOverlay'
import { Container } from 'react-bootstrap'
import { useSearchParams } from 'react-router-dom';
import { AreaSelector, IArea } from '@bmunozg/react-image-area'
import getDomainURL from 'utils/api'
import { getItem } from 'utils/tokenStore'

const FilterLocation = props => {

	const [searchParams, setSearchParams] = useSearchParams();

	const [areas, setAreas] = useState([]);

	const onChangeHandler = (areas) => {
		setAreas(areas);
	}

	const { Title } = Typography

	useEffect(() => {
		if (getItem("LOGIN_TOKEN")){
    	props.initView(searchParams.get("roomId"))
		}
	}, [])

	useEffect(() => {
		if (props.room && getItem("LOGIN_TOKEN")){
			props.getPreselectArea(props.room.ID)
		}
    
	}, [props.room])

	useEffect(() => {
		if (props.preselect_area && props.room && getItem("LOGIN_TOKEN")){
			const roomWidth = props.room.ROOM_X
			const roomHeight = props.room.ROOM_Y
			const imgWidth = props.width
			const imgHeight = props.height
			const tempArea = props.preselect_area.map(area => {
				const x_start = area.X_START;
				const x_end = area.X_END;
				const y_start = area.Y_START;
				const y_end = area.Y_END;
			
				const x = x_start * (imgWidth / roomWidth);
				const y = (roomHeight - y_end) * (imgHeight / roomHeight);
				const width = (x_end - x_start) * (imgWidth / roomWidth);
				const height = (y_end - y_start) * (imgHeight / roomHeight);

				return {
					isChanging: false,
					isNew: false,
					unit: 'px',
					x: x,
					y: y,
					width: width,
					height: height
				};
			});

			setAreas(tempArea)
		}
    
	}, [props.preselect_area])

	const clearAreas = () => {
		setAreas([])
	}

	const handleUpdate = () => {

		const roomWidth = props.room.ROOM_X
		const roomHeight = props.room.ROOM_Y
		const imgWidth = props.width
		const imgHeight = props.height

		const tempAreas = areas.map(area => {
			const { x, y, width, height } = area;
		
			const X_START = x * (roomWidth / imgWidth);
			const X_END = (x + width) * (roomWidth / imgWidth);
			const Y_END = roomHeight - (y * roomHeight) / imgHeight;
			const Y_START = Y_END - (height * roomHeight) / imgHeight;
		
			return {
				X_START: X_START,
				X_END: X_END,
				Y_START: Y_START,
				Y_END: Y_END,
			};
		});

		props.updateFilterArea(tempAreas)
	}

	return (
		<Container>
			<Title style={{width:'100%'}}>Filter Location History ({props.room_name})</Title>
			{
				props.room?
				<div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
					<Row  gutter={[16, 16]} style={{ alignItems: 'center' }}>
						<Col sm={24}  style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
							<AreaSelector
								areas={areas}
								onChange={onChangeHandler}
							>
								<Image src={getDomainURL() + `/static/uploads/` + props.room.IMAGE_NAME} preview={false} width={props.width} height={props.height}/>
							</AreaSelector>
						</Col>
						<Col sm={24} >
							<Space style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
								<Button
									type="primary"
									size="large"
									onClick={handleUpdate}
								>
									Update Areas
								</Button>

								<Button
									type="default"
									size="large"
									onClick={clearAreas}
								>
									Clear Areas
								</Button>
							</Space>
						</Col>
					</Row>
				</div>
				:null
			}
			{
				props.onLoading && <LoadingOverlay/>
			}
		</Container>
	)
}

export default WithHOC(FilterLocation)