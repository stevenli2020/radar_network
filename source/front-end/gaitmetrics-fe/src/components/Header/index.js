import React, { useState, useEffect } from 'react'
import "./index.scss"
import Userbox from './Userbox'
import {Menu} from 'antd'
import { useNavigate } from "react-router-dom"
import logoImage from '../../assets/logo.png';
import { router } from 'router'
import _ from 'lodash'

import { getItem } from 'utils/tokenStore'

const Header = () => {
  
  const [ menuItems, updateMenuItems ] = useState([])
  const [ isAdmin, setIsAdmin] = useState(false)

  const navigate = useNavigate()

  useEffect(()=>{
    if (getItem("LOGIN_TOKEN")){
      if (JSON.parse(getItem("LOGIN_TOKEN")).TYPE == "1"){
        console.log("admin")
        updateMenuItems(_.find( router, { label: "Dashboard" } ).children.slice(0, 3))
      }else{
        updateMenuItems(_.find( router, { label: "Dashboard" } ).children.slice(0, 1))
      }
    }else{
      updateMenuItems(_.find( router, { label: "Dashboard" } ).children.slice(0, 1))
    }
  },[])

  const navigateTo = (item) => {
    navigate('/dashboard/' + item.key)
    document.title = "Gaitmetrics - " + (_.find( menuItems, { key: item.key } )).label
  }

  const getSelectedKey = (isOpenKey) => {
    let tmp = window.location.pathname.split("/")
    let tmpIndex = tmp.indexOf("dashboard")
    if( tmpIndex > -1 ){
      tmp.splice( 0, tmpIndex + 1)
    } else {
      return []
    }
    if( isOpenKey ){
      return tmp.slice(0, -1)
    } else {
      return tmp.slice(-1)
    }
  }

  return(
    <div className='header-container'>
      <div style={{ display: 'flex', alignItems: 'center', width:'100%' }}>
        <img src={logoImage} alt="Logo" style={{ marginRight: '16px',height: '100%', width: '10rem' }} />
        <Menu 
          style={{width:'100%'}}
          theme="light" 
          mode="horizontal"
          onClick={navigateTo}
          selectedKeys={getSelectedKey()}
          defaultSelectedKeys={['home']}
          items={menuItems}
        >
        </Menu>
      </div>

      <div>
        <Userbox/>
      </div>
    </div>
  )
}

export default Header