import React from 'react'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
// import { RadarChartOutlined, BarChartOutlined, RiseOutlined } from '@ant-design/icons'

import Dashboard from './containers/Dashboard';
import Home from './containers/Dashboard/Home';
import Devices from './containers/Dashboard/Devices';
import Users from './containers/Dashboard/Users';
import Summary from './containers/Dashboard/Summary';
import History from './containers/Dashboard/History';
import Profile from './containers/Dashboard/Profile';
import LoginPage from 'containers/Login'
import FilterLocation from 'containers/Dashboard/FilterLocation';

export const router = [
  {
    path: "/",
    element: <LoginPage/>,
  },
  {
    path: "/dashboard/",
		label: "Dashboard",
		element: <Dashboard/>,
		children: [
			{
				key: "home",
        path: "home",
				label: "Home",
        element: <Home/>
      },
			{
				key: "devices",
        path: "devices",
				label: "Devices",
        element: <Devices/>,
      },
			{
				key: "users",
        path: "users",
				label: "Users",
        element: <Users/>,
      },
			{
				key: "summary",
        path: "summary",
				label: "Summary",
        element: <Summary/>
      },
			{
				key: "areafilter",
        path: "areafilter",
				label: "Area Filter",
        element: <>Area Filter</>,
      },
			{
				key: "history",
        path: "history",
				label: "History",
        element: <History/>,
      },
      {
				key: "profile",
        path: "profile",
				label: "Profile",
        element: <Profile/>,
      },
      {
				key: "filterlocation",
        path: "filterlocation",
				label: "FilterLocation",
        element: <FilterLocation/>,
      },
		]
  },
];

const MainRouter = () => {

	return (
		<RouterProvider router={createBrowserRouter(router)}/>
	)
}

export default MainRouter