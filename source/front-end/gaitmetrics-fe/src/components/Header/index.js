import React, { useState, useEffect } from 'react'
import "./index.scss"
import Userbox from './Userbox'
import {Menu} from 'antd'
import { useNavigate } from "react-router-dom"
import logoImage from '../../assets/logo.png';
import { router } from 'router'
import _ from 'lodash'
import getDomainURL from 'utils/api'

import { getItem } from 'utils/tokenStore'

const Header = () => {
  
  const [ menuItems, updateMenuItems ] = useState([])
  const [ isAdmin, setIsAdmin] = useState(false)

  const imageUrl = getDomainURL() + "/static/uploads/logo.png"

  const navigate = useNavigate()

  const [imageExists, setImageExists] = React.useState(false);

  useEffect(() => {
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
      setImageExists(true);
    };
    img.onerror = () => {
      setImageExists(false);
    };
  }, [imageUrl]);

  useEffect(()=>{
    if (getItem("LOGIN_TOKEN") && getItem("TYPE")){
      if (getItem("TYPE") == "1" || getItem("TYPE") == "2"){
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
        <div style={{ marginRight: '16px', width: '10rem', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <img
              src={logoImage}
              alt="Logo"
              style={{
                height: '100%',
                width: imageExists ? '5rem' : '10rem',
              }}
            />
            {imageExists && (
              <img
                src={imageUrl}
                alt="Some description"
                style={{ maxHeight: '3rem', height:'auto', width: '3rem',marginLeft: '5px' }}
              />
            )}
          </div>
        </div>
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