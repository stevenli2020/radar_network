import { AlertFilled } from '@ant-design/icons'
import { Dropdown, Avatar, Space, Modal, Table, Radio } from 'antd'
import React from 'react'

const AlertsModal = (props) => {

  const columns = [ 
    { 
      key: "ID", 
      title: "ID", 
      dataIndex: "ID", 
      sorter: true,
    }, 
    { 
      key: "URGENCY", 
      title: "Urgency", 
      render: (_, alert) => (
				alert.URGENCY==0?(<span style={{color:'green'}}>Information</span>):
				alert.URGENCY==1?(<span style={{color:'yellow'}}>Attention</span>):
				alert.URGENCY==2?(<span style={{color:'orange'}}>Escalated</span>):
				(<span style={{color:'red'}}>Urgent</span>)
			),
    }, 
    { 
      key: "DETAILS", 
      title: "Details", 
      dataIndex: "DETAILS"
    }, 
    { 
      key: "TIMESTAMP", 
      title: "Date", 
      render: (_, alert) => (
				<span>{new Date(alert.TIMESTAMP).toLocaleString()}</span>
			),
    },
    { 
      key: "ACCURACY", 
      title: "Accuracy", 
      render: (_, alert) => (
				<Radio.Group onChange={(val) => {
              props.setAlertAccuracy(alert.ID,val.target.value);
            }} value={alert.ACCURACY}>
          <Radio value={1}>True</Radio>
          <Radio value={0}>False</Radio>
        </Radio.Group>
			),
    }
	]
  
  return (
    <Modal
      title={
        <div style={{textAlign:'center'}}>
          <AlertFilled style={{color:'red'}}></AlertFilled> Alert
        </div>}
      open={true}
      onOk={()=>{
        props.action()
        props.close()
      }}
      onCancel={props.close}
    >
      <Table 
        dataSource={props.alerts} 
        columns={columns} >

      </Table>
    </Modal>
  )
}

export default AlertsModal