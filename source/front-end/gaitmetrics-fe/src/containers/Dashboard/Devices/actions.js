"use client";

import React, { Component } from "react";
import { requestError, requestSuccess } from "utils/requestHandler";
import { Get, Post, Put, Delete } from "utils/axios";
import { getItem } from 'utils/tokenStore'
import _ from 'lodash';

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
      devices: [],
      selectedDevice: null,
      roomSuggestions: [],
      rooms: []
    };

    onChangeHOC = (key, val) => this.setState({ [key]: val });

    load = (param) => this.setState({ loading: param });

    getDevices = () => {
      Post(
        `/api/getRegDevices`,
        JSON.parse(getItem("LOGIN_TOKEN")),
        this.getDevicesSuccess,
        error => requestError(error),
        this.load
      )
    }
    
    getDevicesSuccess = payload => {
      this.setState({ devices: payload.DATA })
    } 

    getRoomSuggestion = (value) => {
      if (typeof value === 'string') {
        let payload = {
          VALUE: value
        }
        payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
        Post(
          `/api/getRoomSuggestion`,
          payload,
          this.getRoomSuggestionSuccess,
          error => console.log(error),
          this.load
        )
      }
    }
    
    getRoomSuggestionSuccess = payload => {
      const autoCompleteOptions = payload.DATA.map(room => ({
        value: room.ROOM_NAME,
        label: room.ROOM_NAME,
      }));
      const rooms = payload.DATA.map(room => ({
        value: room.ROOM_UUID,
        label: room.ROOM_NAME,
      }));
      this.setState({ roomSuggestions: autoCompleteOptions })
      this.setState({ rooms: rooms })
    } 

    registerDevice = (values) => {
      let room_uuid = _.find(this.state.rooms, { label: values.location }).value
      let payload = {
        MAC: values.macAddress,
        NAME: values.deviceName,
        DEPLOY_X: values.deviceposX,
        DEPLOY_Y: values.deviceposY,
        DEPLOY_Z: values.deviceposZ,
        ROT_X: values.devicerotX,
        ROT_Y: values.devicerotY,
        ROT_Z: values.devicerotZ,
        DEVICE_TYPE: values.devicetype,
        DEPLOY_LOC: room_uuid,
        DESCRIPTION: values.devicedescription,
        PASSWORD:values.password
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      console.log(payload)
      Post(
        `/api/addNewDevice`,
        payload,
        this.registerDeviceSuccess,
        error => requestError(error),
        this.load
      )
      this.registerDeviceCredential(values)
    }

    registerDeviceSuccess = payload => {
      this.getDevices()
      requestSuccess("Device registered successfully!")
    }

    registerDeviceCredential = (values) => {
      let payload = {
        username: values.macAddress,
        password:values.password
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      console.log(payload)
      Post(
        `/api/addDeviceCredential`,
        payload,
        this.registerDeviceCredentialSuccess,
        error => requestError(error),
        this.load
      )}
    registerDeviceCredentialSuccess = payload => {
      requestSuccess("Device credential inserted successfully!")
    }

    updateDevice = (values) => {
      console.log(values)
      let room_uuid = _.find(this.state.rooms, { label: values.ROOM_NAME }).value
      let o_room_uuid = '';
      const selectedRoom = _.find(this.state.rooms, { label: this.state.selectedDevice.ROOM_NAME });
      if (selectedRoom) {
          o_room_uuid = selectedRoom.value;
      }
      // let o_room_uuid = _.find(this.state.rooms, { label: this.state.selectedDevice.ROOM_NAME }).value
      let payload = {
        Id: this.state.selectedDevice.Id,
        MAC: values.MAC,
        NAME: values.NAME,
        DEPLOY_X: values.DEPLOY_X,
        DEPLOY_Y: values.DEPLOY_Y,
        DEPLOY_Z: values.DEPLOY_Z,
        ROT_X: values.ROT_X,
        ROT_Y: values.ROT_Y,
        ROT_Z: values.ROT_Z,
        DEPLOY_LOC: room_uuid,
        DEPLOY_O_LOC: o_room_uuid,
        DEVICE_TYPE: values.TYPE,
        DESCRIPTION: values.DESCRIPTION,
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      console.log(payload)
      Post(
        `/api/updateDevice`,
        payload,
        this.updateDeviceSuccess,
        error => requestError(error),
        this.load
      )}
    updateDeviceSuccess = payload => {
      this.getDevices()
      requestSuccess("Device updated successfully!")
    }

    deleteDevice = (device) => {
      let payload = {
        Id: device.Id,
        MAC: device.MAC
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/deleteDevice`,
        payload,
        this.deleteDeviceSuccess,
        error => requestError(error),
        this.load
      )}
    deleteDeviceSuccess = payload => {
      this.getDevices()
      requestSuccess("Device deleted successfully!")
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}

          getDevices={this.getDevices}
          registerDevice={this.registerDevice}
          updateDevice={this.updateDevice}
          deleteDevice={this.deleteDevice}
          onChangeHOC={this.onChangeHOC}
          suggestRoom={this.getRoomSuggestion}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
