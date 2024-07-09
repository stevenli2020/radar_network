import React, { useEffect } from 'react'
import { Outlet, useNavigate } from "react-router-dom"
import { getItem } from 'utils/tokenStore'

import Header from 'components/Header'

import './index.scss'

const Dashboard = () => {

  const navigate = useNavigate()

  useEffect(() => {
    if(!getItem("LOGIN_TOKEN") || !getItem("Username") || !getItem("TYPE")){
      navigate('/')
    }else{
      const currPath = window.location.pathname.split("/")
      if (currPath[currPath.length-1] === "dashboard"){
        navigate('/dashboard/home')
      }
    }
  }, [])

  return(
    <div className="dashboard-container">
      <Header/>
      <div className="dashboard-content-container">
        <div className="dashboard-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default Dashboard