"use client";

import React, { Component } from "react";
import { requestError } from "utils/requestHandler";
import { Post } from "utils/axios";
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
      sleep_disruption_options:null,
      disrupt_duration_options:null,
      heart_rate_options:null,
      breath_rate_options:null,
      receivedAlert:0,
      in_bed: false,
      client_id: null
    };

    barColors = ['#35A29F', '#088395', '#071952'];

    onChangeHOC = (key, val) => this.setState({ [key]: val });
    load = (param) => this.setState({ loading: param });
    temp = (param) => this.setState({ temp: param });

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
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
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
                itemStyle: { color: '#088395' } // Set the color for 'Sleeping'
              },
              {
                value: negVal,
                name: negText,
                itemStyle: { color: '#35A29F' } // Set the color for 'Not Sleeping'
              }
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
      console.log(payload)
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
          console.log(disrupt_mins,sleeping_mins)
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
    } 

    getRoomAlerts = (room_id,unread=true) => {
      let payload = {
        room_id: room_id,
        unread: unread,
        set: true
      }
      if (unread){
        this.setState({receivedAlert:this.props.receivedAlert+1})
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getRoomAlerts`,
        payload,
        this.getRoomAlertsSuccess,
        error => requestError(error),
        this.load
      )
    }
    
    getRoomAlertsSuccess = payload => {
      if (payload.DATA.length > 0){
        this.setState({ alerts: payload.DATA })

        const hasUrgency3 = payload.DATA.some(alert => alert.URGENCY === 3 && alert.NOTIFY === 0);
        if (hasUrgency3) {
          try{
            const sound = new Audio(alertSound)
            sound.play().then(() => {
              // If playback is successful, sound permission is likely granted
              console.log("Permission granted")
            }).catch((error) => {
              // If playback fails, sound permission is likely denied
              console.log(error)
            });
          } catch (error) {
            // If an exception occurs, sound permission status is uncertain
          }
        }
      }
      

    }

    getMQTTClientID = async() => {
      await Post(
        `/api/getMQTTClientID`,
        JSON.parse(getItem("LOGIN_TOKEN")),
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
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
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
          getRoomSummary={this.getRoomSummary}
          getRoomAlerts={this.getRoomAlerts}
          onLoading={this.state.loading}
          onChangeHOC={this.onChangeHOC}
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
