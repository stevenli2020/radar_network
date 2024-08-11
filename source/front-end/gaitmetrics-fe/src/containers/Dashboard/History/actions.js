"use client";

import React, { Component } from "react";
import { requestError } from "utils/requestHandler";
import { Get, Post, Put, Delete } from "utils/axios";
import { getItem } from 'utils/tokenStore'
import getDomainURL from 'utils/api'
import alertSound from "../../../assets/alert.wav"

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {

    state = {
      init:false,
      loading: false,
      temp:false,
      room_uuid:null,
      room:null,
      room_name:'-',
      sensors:[],
      persons:[],
      alerts:[],
      macPos:null,
      macVital:null,
      realtimeLocationData:null,
      locationHistoryData:null,
      vitalHistoryData:null,
      occupancyHistoryData:null,
      room_empty:true,
      vital_data:null,
      is_admin:false,
      client_id: null,
      receivedAlert:0
    };

    sound = new Audio(alertSound);

    componentWillUnmount() {
      // Cleanup audio playback and event listener
      this.stopSound();
    }

    playSound = () => {
      // Play audio and set playing state to true
      this.sound.play()
        .then(() => {
          console.log("Sound playing");
          this.setState({ playing: true });
        })
        .catch((error) => {
          console.error("Playback error:", error);
          this.setState({ playing: false });
        });

      // Listen for 'ended' event to restart playback
      this.sound.addEventListener('ended', this.playAndRestart);
    };

    stopSound = () => {
      // Stop audio playback and reset state
      this.sound.pause();
      this.sound.currentTime = 0;
      this.setState({ playing: false });
      this.sound.removeEventListener('ended', this.playAndRestart);
    };

    playAndRestart = () => {
      console.log("ended")
      this.getRoomAlerts(this.state.room_uuid,true,this.temp)
    };

    getRoomDetail = (room_uuid) => {
      let payload = {
        ROOM_UUID:room_uuid
      }
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

    getRoomAlerts = (room_id,unread=true,loader=this.load) => {
      let payload = {
        room_id: room_id,
        unread: unread,
        set: false
      }
      if (unread){
        this.setState({receivedAlert:this.state.receivedAlert+1})
      }
      Post(
        `/api/getRoomAlerts`,
        payload,
        this.getRoomAlertsSuccess,
        error => requestError(error),
        loader
      )
    }
    
    getRoomAlertsSuccess = payload => {
      if (payload.DATA.length > 0){
        this.setState({ alerts: payload.DATA })

        const hasUrgency3 = payload.DATA.some(alert => alert.URGENCY === 3 && alert.NOTIFY === 0);
        if (hasUrgency3) {
          this.playSound()
        }
      }
    }

    readAlert = () => {
      let payload = {
        ROOM_UUID: this.state.room_uuid
      }
      Post(
        `/api/readRoomAlerts`,
        payload,
        this.readAlertSuccess,
        error => requestError(error),
        this.load
      )
    }
    
    readAlertSuccess = payload => {
      
    }

    getRoomSensors = (room_uuid) => {
      let payload = {
        ROOM_UUID:room_uuid
      }
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
        this.setState({macPos:macPos})
      }

      if (macVital){
        this.setState({macVital:macVital})
      }
      this.setState({sensors:radars})
      this.setState({init:true})
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
      // console.log(payload)
      Post(
        `/api/getSummaryPositionData`,
        payload,
        this.getLocationHistorySuccess,
        error => {
          console.log(error)
          this.setState({locationHistoryData:null})
        },
        this.temp
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
      Post(
        `/api/getAnalyticData`,
        payload,
        this.getOccupancyHistorySuccess,
        error => {
          console.log(error)
          this.setState({occupancyHistoryData:null})
        },
        this.temp
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
      Post(
        `/api/getHistOfVital`,
        payload,
        this.getVitalHistorySuccess,
        error => {
          console.log(error)
          this.setState({vitalHistoryData:null})
        },
        this.temp
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
    temp = (param) => this.setState({ temp: param });

    initView = (room_id) =>{
      this.setState({room_uuid:room_id})
      this.getRoomDetail(room_id)
      this.getRoomSensors(room_id)
      this.getOccupancyHistory(room_id)
      this.getVitalHistory(room_id,"1 WEEK")
      this.getRoomAlerts(room_id)
    }

    getMQTTClientID = async() => {
      await Post(
        `/api/getMQTTClientID`,
        {},
        this.getMQTTClientIDSuccess,
        error => requestError(error),
        this.load
      )
    }

    getMQTTClientIDSuccess = payload => {
      this.setState({client_id:payload.DATA.client_id})
    }

    setClientConnection = async(client_id) => {
      let payload = {
        client_id: client_id,
      }
      await Post(
        `/api/setClientConnection`,
        payload,
        this.setClientConnectionSuccess,
        error => requestError(error),
        this.temp
      )
    }

    setClientConnectionSuccess = payload => {
      this.setState({client_id:payload.DATA.client_id})
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
          getRoomAlerts={this.getRoomAlerts}
          readAlert={this.readAlert}
          initView={this.initView}
          getMQTTClientID={this.getMQTTClientID}
          setClientConnection={this.setClientConnection}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
