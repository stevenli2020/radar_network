import { DownOutlined, PoweroffOutlined, SettingOutlined, UserOutlined } from '@ant-design/icons'
import { Dropdown, Avatar, Space } from 'antd'
import React from 'react'
import { useNavigate } from "react-router-dom"
import { storeItem } from 'utils/tokenStore'

const Userbox = () => {
  const navigate = useNavigate()
  const menuItem = {
    items: [
      {
				key: "profile",
				icon: <UserOutlined />,
				label: "Profile"
      },
      {
				key: "settings",
				icon: <SettingOutlined />,
				label: "Settings"
      },
      {
				key: "logout",
				icon: <PoweroffOutlined />,
				label: "Log Out"
      }
    ],
    onClick: (e) => {
      switch(e.key){
        case "profile":
          navigate('/dashboard/profile')
          break
        case "settings":
          navigate('/dashboard/settings')
          break
        case "logout":
          storeItem("LOGIN_TOKEN", "")
          window.location.reload()
          break
        default: 
      }
    }
  }

  return (
    <Dropdown menu={menuItem} trigger={'hover'}>
      <a onClick={(e) => e.preventDefault()}>
        <Space>
          <Avatar size={32} icon={<UserOutlined />} />
          <DownOutlined />
        </Space>
      </a>
    </Dropdown>
  )
}

export default Userbox