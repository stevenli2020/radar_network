import React, { useEffect, useState } from 'react';
import { Form, Input, Row, Col, Modal, message, Image, Button, Space, Select } from 'antd';
import getDomainURL from 'utils/api'

import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

import _ from 'lodash';

const backgroundImageUrl = getDomainURL() + `/static/uploads/prison.jpg`
const viewportWidthInPixels = window.innerWidth;

const EditRoomOnMapModal = (props) => {

  const [layout,setLayout] = useState([])
  const [rooms, setRooms] = useState(props.rooms)
  const [dragable, setDragable] = useState(true)
  const [selectedRoomId, setSelectedRoomId] = useState(null);

  const handleUpdate = () =>{
    props.action(layout)
  }

  const addToMap = () => {
    if (selectedRoomId){
      const updatedRooms = _.map(rooms, (room) => {
        if (room.ID === selectedRoomId && room.x == null) {
          // Update x, y, w, and h to null
          return { ...room, x: 1, y: 1, w: 20, h: 8 };
        }
        return room; // If the ID doesn't match, return the original room object
      })

      setRooms(updatedRooms)
      const selectedRoom = _.find(rooms, { ID: selectedRoomId });
      if (selectedRoom) {
        const newLayoutItem = {
          x: 0,
          y: 0,
          w: 10,
          h: 5,
          i: selectedRoomId.toString(), // Assuming 'i' is the property for item ID in layout
        };

        // Assuming you have a function setLayout to update the layout state
        setLayout((prevLayout) => [...prevLayout, newLayoutItem]);
      }
    }
  }

  useEffect(()=>{
    console.log(layout)
  },[layout])

  const initialLayout = props.rooms
  .filter((room) => room.x !== null && room.y !== null && room.w !== null && room.h !== null)
  .map((room, index) => ({
    i: `${room.ID.toString()}`,
    x: room.x, // Adjust based on your grid structure
    y: room.y, // Adjust based on your grid structure
    w: room.w,
    h: room.h,
  }));

  const removeStyle = {
    position: "absolute",
    right: "2px",
    top: 0,
    zIndex:999,
    cursor: "pointer"
  };

  // Callback function to handle layout changes
  const onLayoutChange = (currlayout) => {
    // Handle layout changes if needed
    const newLayout = currlayout.map(room => ({
      ID: room.i, // Use 'ID' instead of 'i'
      x: room.x,
      y: room.y,
      w: room.w,
      h: room.h,
    }));
    
    setLayout(newLayout)
  };

  const onRemoveItem = (id) => {
    console.log("removing", id);
    const updatedRooms = _.map(rooms, (room) => {
      if (room.ID === id) {
        // Update x, y, w, and h to null
        return { ...room, x: null, y: null, w: null, h: null };
      }
      return room; // If the ID doesn't match, return the original room object
    })
    console.log(updatedRooms)
    setRooms(updatedRooms)
    setDragable(true)
  }

  return (
    <Modal
      title="Edit Map"
      open={true}
      onOk={handleUpdate}
      onCancel={props.close}
      width="fit-content"
    >
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        <Row  gutter={[16, 16]} style={{ alignItems: 'center' }}>
          <Col sm={24}  style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <GridLayout
              className="grid-layout"
              style={{backgroundImage:`url(${backgroundImageUrl})`,backgroundRepeat:'no-repeat', backgroundSize:'700px 500px'}}
              layout={initialLayout}
              cols={100}
              autoSize={false}
              rowHeight={2} // 50vh / 4 rows
              width={700} // 60vw * 12 cols
              onLayoutChange={onLayoutChange}
              verticalCompact={false}
              isDraggable={dragable}
              // isResizable={false}
              preventCollision={true}
              // isBounded={true} 
            >
              {
              rooms.filter((room) => room.x !== null && room.y !== null && room.w !== null && room.h !== null).map( room => (
                <div key={room.ID.toString()} className={`grid-item`} >
                  <div style={{display:'flex',alignItems:'center',justifyContent: 'center',height:'100%',}}>
                    <span className="text">{room.ROOM_NAME}</span>
                    <span
                      className="remove"
                      style={removeStyle}
                      onClick={(event) => {
                        onRemoveItem(room.ID)}}
                      onMouseEnter={()=>setDragable(false)}
                      onMouseLeave={()=>setDragable(true)}
                    >
                      x
                    </span>
                  </div>
                </div>))
              }
            </GridLayout>
          </Col>
          <Col sm={24} >
            <Space style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              
              {rooms.length != layout.length && 
              <>
                <Select
                  value={selectedRoomId}
                  onChange={(value) => setSelectedRoomId(value)}
                  style={{ width: 200, marginBottom: 16 }}
                  placeholder="Select a room"
                >
                  {rooms
                    .filter((room) => room.x === null && room.y === null && room.w === null && room.h === null)
                    .map((room) => (
                      <Select.Option key={room.ID.toString()} value={room.ID}>
                        {room.ROOM_NAME}
                      </Select.Option>
                    ))}
                </Select>
                <Button
                  type="primary"
                  size="large"
                  onClick={addToMap}
                >
                  Add
                </Button>
              </>}
            </Space>
          </Col>
        </Row>
      </div>
    </Modal>
  );
};

export default EditRoomOnMapModal;