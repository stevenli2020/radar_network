"use client";

import React, { Component } from "react";
import { requestError } from "utils/requestHandler";
import { Get, Post } from "utils/axios";
import { getItem } from 'utils/tokenStore'
import moment from 'moment';
import alertSound from "../../../assets/alert.wav"

const HOC = (WrappedComponent) => {
  
  class WithHOC extends Component {
    state = {
      init:false,
      loading: false,
      temp:false,
      sensors:[],
      bed_time:{min:"-",max:"-",average:"-",previous_average:"-"},
      wake_up_time:{min:"-",max:"-",average:"-",previous_average:"-"},
      sleeping_hour:{min:"-",max:"-",average:"-",previous_average:"-"},
      time_in_bed:{min:"-",max:"-",average:"-",previous_average:"-"},
      in_room:{min:"-",max:"-",average:"-",previous_average:"-"},
      sleep_disruption:{min:"-",max:"-",average:"-",previous_average:"-"},
      heart_rate:{min:"-",max:"-",average:"-",previous_average:"-"},
      breath_rate:{min:"-",max:"-",average:"-",previous_average:"-"},
      disrupt_duration:{min:"-",max:"-",average:"-",previous_average:"-"},
      alerts:[],
      room_uuid:null,
      room_name:"-",
      bed_time_options:null,
      wake_up_time_options:null,
      sleeping_hour_options:null,
      time_in_bed_options:null,
      in_room_options:null,
      in_room_posture_options:null,
      in_room_series_posture_options:null,
      sleep_disruption_options:null,
      disrupt_duration_options:null,
      heart_rate_options:null,
      breath_rate_options:null,
      receivedAlert:0,
      in_bed: false,
      client_id: null,
      components:{}
    };

    barColors = ['#35A29F', '#088395', '#071952'];

    onChangeHOC = (key, val) => this.setState({ [key]: val });
    load = (param) => this.setState({ loading: param });
    temp = (param) => this.setState({ temp: param });

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

    initView = (room_id) =>{
      const defaultEOW = moment().subtract(1, 'days').format('YYYY-MM-DD');
      this.setState({room_uuid:room_id})
      this.getRoomSummary(room_id,defaultEOW)
      this.getRoomAlerts(room_id)
    }

    getRoomSummary = (room_id,eow) => {
      let payload = {
        room_id: room_id,
        eow:eow
      }
      Post(
        `/api/getRoomLaymanDetail`,
        payload,
        this.getRoomSummarySuccess,
        error => requestError(error),
        this.load
      )
    }

    timeStringToMinutes = (timeString) => {
      // Initialize hours and minutes
      var hours = 0;
      var minutes = 0;
      
      // Check if the time string contains "h" (hours)
      var indexOfHours = timeString.indexOf('h');
      if (indexOfHours !== -1) {
        hours = parseInt(timeString.slice(0, indexOfHours));
        // Extract the part after 'h' to find minutes
        var minutesPart = timeString.slice(indexOfHours + 1).replace('m', '');
        if (minutesPart !== '') {
          minutes = parseInt(minutesPart);
        }
      } else {
        // If no 'h' is found, assume the whole string represents minutes
        minutes = parseInt(timeString.replace('m', ''));
      }
      
      // Convert hours to minutes and add to the minutes
      var totalMinutes = hours * 60 + minutes;
      return totalMinutes;
    }

    generateTimeOptions = (data) => {
      return {
        series: [
          {
            name: 'hour',
            type: 'gauge',
            startAngle: 90,
            endAngle: -270,
            min: 0,
            max: 12,
            splitNumber: 12,
            clockwise: true,
            axisLine: {
              lineStyle: {
                width: 4,
                color: [[1, '#071952']],
              }
            },
            axisLabel: {
              fontSize: 10,
              distance: 5,
              formatter: function (value) {
                if (value === 0) {
                  return '';
                }
                return value + '';
              }
            },
            pointer: {
              icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
              width: 4,
              length: '40%',
              offsetCenter: [0, '2%'],
              itemStyle: {
                color: '#088395',
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                shadowBlur: 8,
                shadowOffsetX: 2,
                shadowOffsetY: 4
              }
            },
            detail: {
              show: false
            },
            data: [
              {
                value: data[0]
              }
            ]
          },
          {
            name: 'minute',
            type: 'gauge',
            startAngle: 90,
            endAngle: -270,
            min: 0,
            max: 60,
            clockwise: true,
            axisLine: {
              show: false
            },
            splitLine: {
              show: false
            },
            axisTick: {
              show: false
            },
            axisLabel: {
              show: false
            },
            pointer: {
              icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
              width: 2,
              length: '60%',
              offsetCenter: [0, '8%'],
              itemStyle: {
                color: '#35A29F',
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                shadowBlur: 8,
                shadowOffsetX: 2,
                shadowOffsetY: 4
              }
            },
            anchor: {
              show: true,
              size: 3,
              showAbove: false,
              itemStyle: {
                borderWidth: 4,
                borderColor: '#35A29F',
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                shadowBlur: 8,
                shadowOffsetX: 2,
                shadowOffsetY: 4
              }
            },
            detail: {
              show: false
            },
            title: {
              offsetCenter: ['0%', '-4%']
            },
            data: [
              {
                value: data[1]
              }
            ]
          }
        ]
      }
    }

    generateBarOptions = (min,max,average) => {
      return {
        xAxis: {                   // Use xAxis for horizontal bars
          type: 'value'
        },
        yAxis: {                   // Use yAxis for categories
          type: 'category',        // Specify the axis type as category
          data: ['Min', 'Avg', 'Max']
        },
        series: [
          {
            data: [
              {
                value: min,
                itemStyle: {
                  color: this.barColors[0] // Set the color for the 'Min' bar
                }
              },
              {
                value: average,
                itemStyle: {
                  color: this.barColors[1] // Set the color for the 'Average' bar
                }
              },
              {
                value: max,
                itemStyle: {
                  color: this.barColors[2] // Set the color for the 'Max' bar
                }
              }
            ],
            type: 'bar',
            showBackground: true,
            backgroundStyle: {
              color: 'rgba(180, 180, 180, 0.2)'
            }
          }
        ]
      }
    }

    generatePieOptions = (posText,negText,posVal,negVal=(60*24)-posVal) => {
      return {
        legend: {
          orient: 'vertical',
          right: '0%',
          bottom: '5%' 
        },
        dataset: [
          {
            source: [
              { value: posVal, name: posText },
              { value: negVal, name: negText }
            ],
            
          }
        ],
        series: [
          {
            type: 'pie',
            radius: '70%',
            center: ['50%', '50%'], // Center the pie chart both horizontally and vertically
            label: {
              position: 'inside',
              formatter: '{d}%',
              color: 'black',
              fontSize: 10
            },
            percentPrecision: 0,
            emphasis: {
              label: { show: true },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            // Set colors for each name (category)
            data: [
              {
                value: posVal,
                name: posText,
                // itemStyle: { color: '#088395' } 
              },
              {
                value: negVal,
                name: negText,
                // itemStyle: { color: '#35A29F' } 
              }
            ]
          }
        ]
      }
    }

    generateSeriesPostureOptions = (data_arr) => {

      let dates = []
      let social_data = []
      let moving_data = []
      let upright_data = []
      let laying_data = []
      let unknown_data = []
      let not_in_room_data = []

      data_arr.forEach(item => {
        dates.push(item.date);
        social_data.push(item.social);
        moving_data.push(item.moving);
        upright_data.push(item.upright);
        laying_data.push(item.laying);
        unknown_data.push(item.unknown);
        not_in_room_data.push(item.not_in_room)
      });

      return {
        // title: {
        //   text: 'In Room Posture Time Series Analysis'
        // },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: function (params) {
            let tooltipText = `<b>${params[0].name}</b><br/>`;
            params.forEach(param => {
              let minutes = param.value
              let day = Math.floor(minutes / (24 * 60));
              let hour = Math.floor((minutes % (24 * 60)) / 60);
              let minute = minutes % 60;
              let textString = ''
              let percentString = ''
        
              if (day > 0){
                textString += day.toString() + "d" 
              }
              if (hour > 0){
                textString += hour.toString() + "h" 
              }
              if (minute > 0){
                textString += minute.toString() + "m" 
              }

              percentString = ((minutes*100)/(24*60)).toFixed(2).toString()
        
              if (textString == ''){
                textString = '0m'
              }
              tooltipText += `<b>${param.seriesName}:</b> ${textString} (${percentString} %)<br/>`;
            });
            return tooltipText;
          },
        },
        legend: {
          data: ['Social', 'Moving', 'Upright', 'Laying', 'Unknown', 'Not In Room'],
          type: 'scroll'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            boundaryGap: true,
            data: dates
          }
        ],
        yAxis: [
          {
            type: 'value'
          }
        ],
        series: [
          {
            name: 'Social',
            type: 'bar',
            stack: 'Total',
            emphasis: {
              focus: 'series'
            },
            data: social_data
          },
          {
            name: 'Moving',
            type: 'bar',
            stack: 'Total',
            emphasis: {
              focus: 'series'
            },
            data: moving_data
          },
          {
            name: 'Upright',
            type: 'bar',
            stack: 'Total',
            emphasis: {
              focus: 'series'
            },
            data: upright_data
          },
          {
            name: 'Laying',
            type: 'bar',
            stack: 'Total',
            emphasis: {
              focus: 'series'
            },
            data: laying_data
          },
          {
            name: 'Unknown',
            type: 'bar',
            stack: 'Total',
            emphasis: {
              focus: 'series'
            },
            data: unknown_data
          },
          {
            name: 'Not In Room',
            type: 'bar',
            stack: 'Total',
            emphasis: {
              focus: 'series'
            },
            data: not_in_room_data
          }
        ]
      }
    }

    generatePostureOptions = (data) => {
      return {
        legend: {
          orient: 'horizontal',
          bottom: '0%',
          left: 'center',
          type: 'scroll'
        },
        dataset: [
          {
            source: [
              { value: data.social, name: 'Social' },
              { value: data.moving, name: 'Moving' },
              { value: data.upright, name: 'Upright' },
              { value: data.laying, name: 'Laying' },
              { value: data.unknown, name: 'Unknown' },
            ],
            
          }
        ],
        series: [
          {
            type: 'pie',
            radius: '70%',
            center: ['50%', '50%'], // Center the pie chart both horizontally and vertically
            label: {
              position: 'inside',
              formatter: '{d}%',
              color: 'black',
              fontSize: 10
            },
            percentPrecision: 0,
            emphasis: {
              label: { show: true },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            // Set colors for each name (category)
            data: [
              { value: data.social, name: 'Social' },
              { value: data.moving, name: 'Moving' },
              { value: data.upright, name: 'Upright' },
              { value: data.laying, name: 'Laying' },
              { value: data.unknown, name: 'Unknown' },
            ]
          }
        ]
      }
    }

    extractHourAndMinute = (timeString) => {
      const timeStr = timeString.split(" ")[0]
      const timeArr = timeStr.split(":")
      const hour = parseFloat(timeArr[0]) + (parseInt(timeArr[1])/60)
      const minute = parseInt(timeArr[1])
      return [hour, minute]
    }
    
    getRoomSummarySuccess = payload => {
      this.setState({ sensors: payload.data.sensors })
      this.setState({ init: true })
      this.setState({ bed_time: payload.data.bed_time })
      this.setState({ wake_up_time: payload.data.wake_up_time })
      this.setState({ sleeping_hour: payload.data.sleeping_hour })
      this.setState({ time_in_bed: payload.data.time_in_bed })
      this.setState({ in_room: payload.data.in_room })
      this.setState({ sleep_disruption: payload.data.sleep_disruption })
      this.setState({ heart_rate: payload.data.heart_rate })
      this.setState({ breath_rate: payload.data.breath_rate })
      this.setState({ disrupt_duration: payload.data.disrupt_duration })
      this.setState({ room_name: payload.data.room_name.split("@")[0] })

      if (payload.data.bed_time.average != "-"){
        let data = this.extractHourAndMinute(payload.data.bed_time.average)
        let options =  this.generateTimeOptions(data)

        this.setState({ bed_time_options: options })
      }else{
        this.setState({ bed_time_options: null })
      }

      if (payload.data.wake_up_time.average != "-"){
        let data = this.extractHourAndMinute(payload.data.wake_up_time.average)
        let options =  this.generateTimeOptions(data)

        this.setState({ wake_up_time_options: options })
      }else{
        this.setState({ wake_up_time_options: null })
      }

      if (payload.data.sleeping_hour.average != "-"){
        let sleeping_mins = 0
        sleeping_mins = this.timeStringToMinutes(payload.data.sleeping_hour.average)
        let options =  this.generatePieOptions("Sleeping","Not Sleeping",sleeping_mins)

        if (payload.data.disrupt_duration.average != "-"){
          let disrupt_mins = 0
          disrupt_mins = this.timeStringToMinutes(payload.data.disrupt_duration.average)
          let disruptOptions =  this.generatePieOptions("Disrupt Disruption","Not Disrupted",disrupt_mins,sleeping_mins)

          this.setState({ disrupt_duration_options: disruptOptions })
        }else{
          this.setState({ disrupt_duration_options: null })
        }

        this.setState({ sleeping_hour_options: options })
      }else{
        this.setState({ sleeping_hour_options: null })
      }

      if (payload.data.time_in_bed.average != "-"){
        let sleeping_mins = 0
        sleeping_mins = this.timeStringToMinutes(payload.data.time_in_bed.average)
        let options =  this.generatePieOptions("On Bed","Not On Bed",sleeping_mins)

        this.setState({ time_in_bed_options: options })
      }else{
        this.setState({ time_in_bed_options: null })
      }

      if (payload.data.in_room.average != "-"){
        let sleeping_mins = 0
        sleeping_mins = this.timeStringToMinutes(payload.data.in_room.average)
        let options =  this.generatePieOptions("In Room","Not In Room",sleeping_mins)

        this.setState({ in_room_options: options })
      }else{
        this.setState({ in_room_options: null })
      }

      if (payload.data.sleep_disruption.average != "-"){
        let options =  this.generateBarOptions(payload.data.sleep_disruption.min,payload.data.sleep_disruption.max,payload.data.sleep_disruption.average)

        this.setState({ sleep_disruption_options: options })
      }else{
        this.setState({ sleep_disruption_options: null })
      }

      if (payload.data.heart_rate.average != "-"){
        let options =  this.generateBarOptions(payload.data.heart_rate.min,payload.data.heart_rate.max,payload.data.heart_rate.average)

        this.setState({ heart_rate_options: options })
      }else{
        this.setState({ heart_rate_options: null })
      }

      if (payload.data.breath_rate.average != "-"){
        let options =  this.generateBarOptions(payload.data.breath_rate.min,payload.data.breath_rate.max,payload.data.breath_rate.average)

        this.setState({ breath_rate_options: options })
      }else{
        this.setState({ breath_rate_options: null })
      }

      if (payload.data.inroom_analysis.length > 0){
        let inroom_analysis = payload.data.inroom_analysis
        const mergedDict = inroom_analysis.reduce((acc, curr) => {
            for (let key in curr) {
                acc[key] = (acc[key] || 0) + curr[key];
            }
            return acc;
        }, {});
        this.setState({in_room_posture_options: this.generatePostureOptions(mergedDict)})
        this.setState({in_room_series_posture_options: this.generateSeriesPostureOptions(inroom_analysis)})
      }
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

    getComponentsEnablement = (page) => {
      Get(
        `/api/componentenablement/${page}`,
        this.getComponentsEnablementSuccess,
        error => requestError(error),
        this.load
      )
    }

    getComponentsEnablementSuccess = payload => {
      this.setState({components:payload})
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          getRoomSummary={this.getRoomSummary}
          getRoomAlerts={this.getRoomAlerts}
          readAlert={this.readAlert}
          onLoading={this.state.loading}
          onChangeHOC={this.onChangeHOC}
          initView={this.initView}
          getMQTTClientID={this.getMQTTClientID}
          setClientConnection={this.setClientConnection}
          getComponentsEnablement={this.getComponentsEnablement}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
