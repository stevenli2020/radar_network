"use client";

import React, { Component } from "react";
import { requestError } from "utils/requestHandler";
import { Get, Post, Put, Delete } from "utils/axios";
import { getItem } from 'utils/tokenStore'
import getDomainURL from 'utils/api'

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {

    state = {
      loading: false,
      room_uuid:null,
      room:null,
      room_name:'-',
      sensors:[],
      persons:[],
      macPos:null,
      macVital:null,
      realtimeLocationData:null,
      locationHistoryData:null,
      vitalHistoryData:null,
      occupancyHistoryData:null,
      room_empty:true,
      vital_data:null,
      is_admin:false
    };

    getRoomDetail = (room_uuid) => {
      let payload = {
        ROOM_UUID:room_uuid
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getRoomDetail`,
        payload,
        this.getRoomDetailSuccess,
        error => requestError(error),
        this.load
      )
    }

    getRoomDetailSuccess = payload => {
      this.setState({room:payload.DATA[0]})
      let room_name = payload.DATA[0].ROOM_NAME
      this.setState({room_name:room_name})
      const imageUrl = getDomainURL() + `/static/uploads/` + payload.DATA[0].IMAGE_NAME;
      this.setState({realtimeLocationOptions:{
        graphic: [
          {
            id: 'bg',
            type: 'image',
            style: {
              image: imageUrl,
              position: 'absolute',
              width: 200,
              height: 200
            },
            position: [0,0]
          },
        ]
      }})
    }

    getRoomSensors = (room_uuid) => {
      let payload = {
        ROOM_UUID:room_uuid
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getRLMacRoom`,
        payload,
        this.getRoomSensorsSuccess,
        error => requestError(error),
        this.load
      )
    }

    getRoomSensorsSuccess = payload => {
      let radars = []
      let macPos = null
      let macVital = null

      payload.DATA.forEach(d => {
        if (d.TYPE == "1" || d.TYPE == "2") {
          macPos = d.MAC
          const radarType = d.TYPE == "1" ? "Wall" : "Ceil";
          const radarName = `${radarType} Radar`;
      
          radars.push({
            name: radarName,
            type: "scatter",
            emphasis: {
              focus: "series",
            },
            symbol: 'rect',
            symbolSize: 10,
            data: [[d.DEPLOY_X, d.DEPLOY_Y]],
          });
        }
      
        if (d.TYPE == "3") {
          macVital = d.MAC
          radars.push({
            name: "Vital Radar",
            type: "scatter",
            emphasis: {
              focus: "series",
            },
            symbol: 'rect',
            symbolSize: 10,
            data: [[d.DEPLOY_X, d.DEPLOY_Y]],
          });
        }
      });

      if (macPos){
        this.getLocationHistory(macPos,"HOUR")
        console.log("macpos",macPos)
        this.setState({macPos:macPos})
      }

      if (macVital){
        this.setState({macVital:macVital})
        console.log("macvital",macVital)
      }
      this.setState({sensors:radars})
    }

    getLocationHistory = (macPos, type, start=null, end=null) => {
      let payload = {
        DEVICEMAC:macPos,
        TIME:type
      }
      if (type == "CUSTOM"){
        payload.TIMESTART = start
        payload.TIMEEND = end
      }else{
        payload.CUSTOM = 0
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      console.log(payload)
      Post(
        `/api/getSummaryPositionData`,
        payload,
        this.getLocationHistorySuccess,
        error => console.log(error),
        this.load
      )
    }

    getLocationHistorySuccess = payload => {
      this.setState({locationHistoryData:payload})
    }

    getOccupancyHistory = (room_uuid) => {
      let payload = {
        ROOM_UUID: room_uuid,
        CUSTOM: 0
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getAnalyticData`,
        payload,
        this.getOccupancyHistorySuccess,
        error => console.log(error),
        this.load
      )
    }

    getOccupancyHistorySuccess = payload => {
      this.setState({occupancyHistoryData:payload})
    }

    getVitalHistory = (room_uuid,type, start=null,end=null) => {
      let payload = {
        ROOM_UUID: room_uuid
      }
      if (type == "CUSTOM"){
        payload.CUSTOM = 1
        payload.TIMESTART = start
        payload.TIMEEND = end
      }else{
        payload.CUSTOM = 0
        payload.TIME = type
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getHistOfVital`,
        payload,
        this.getVitalHistorySuccess,
        error => console.log(error),
        this.load
      )
    }

    getVitalHistorySuccess = payload => {
      this.setState({vitalHistoryData:payload})
    }

    updatePersonsLocation = (data) => {
      if (data.length > 0){
        this.setState({room_empty:false})
      }else{
        this.setState({room_empty:true})
      }
      this.setState({persons:data})
    }

    addVitalData = (heartRate,breathRate) => {
      this.setState({vital_data:[heartRate,breathRate]})
    }

    onChangeHOC = (key, val) => this.setState({ [key]: val });
    load = (param) => this.setState({ loading: param });

    initView = (room_id) =>{
      this.setState({room_uuid:room_id})
      this.getRoomDetail(room_id)
      this.getRoomSensors(room_id)
      this.getOccupancyHistory(room_id)
      this.getVitalHistory(room_id,"1 WEEK")
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}
          onChangeHOC={this.onChangeHOC}
          getLocationHistory={this.getLocationHistory}
          getVitalHistory={this.getVitalHistory}
          updatePersonsLocation={this.updatePersonsLocation}
          addVitalData={this.addVitalData}
          initView={this.initView}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
