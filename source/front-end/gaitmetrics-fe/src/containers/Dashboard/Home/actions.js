"use client";

import React, { Component } from "react";
import { requestError, requestSuccess } from "utils/requestHandler";
import { Get, Post, Put, Delete, PostForm } from "utils/axios";
import { getItem } from 'utils/tokenStore'

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
      alertLength:0,
      rooms:[],
      selectedRoom:null,
      newUploadImg:null,
      updateUploadImg:null,
      mapView:false,
      isAdmin:false
    };

    onChangeHOC = (key, val) => this.setState({ [key]: val });

    load = (param) => this.setState({ loading: param });

    getRoomDetails = () => Post(
        `/api/getRoomDetails`,
        JSON.parse(getItem("LOGIN_TOKEN")),
        this.getRoomDetailsSuccess,
        error => requestError(error),
        this.load
      )

    getRoomDetailsSuccess = payload => {
      this.setState({rooms:payload.DATA})
      let c = 0
      payload.DATA.map(room => {
        c += room.ALERTS.length
      });
      console.log(payload,c)
      this.setState({alertLength:c})
    }

    addRoom = (values) => {
      console.log(values)
      let info = values.description==undefined?'':values.description
      let payload = {
        ROOM_NAME: values.roomname,
        ROOM_X: values.length,
        ROOM_Y: values.width,
        ROOM_LOC: values.roomlocation,
        INFO: info,
        IMAGE_NAME: this.state.newUploadImg,
      }
      console.log(payload)
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/addNewRoom`,
        payload,
        this.addRoomSuccess,
        error => requestError(error),
        this.load
      )}
    addRoomSuccess = payload => {
      requestSuccess("Room added successfully!")
      this.getRoomDetails()
    }

    updateRoom = (values) => {
      console.log(values)
      console.log(this.state.selectedRoom)
      let info = values.INFO==undefined || values.INFO==null?'':values.INFO
      let payload = {
        ROOM_NAME: values.ROOM_NAME,
        ROOM_X: values.ROOM_X,
        ROOM_Y: values.ROOM_Y,
        ROOM_LOC: values.ROOM_LOC,
        INFO: info,
        IMAGE_NAME: this.state.updateUploadImg,
        O_IMAGE_NAME: this.state.selectedRoom.IMAGE_NAME,
        ROOM_UUID: this.state.selectedRoom.ROOM_UUID,
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      console.log(payload)
      Post(
        `/api/updateRoom`,
        payload,
        this.updateRoomSuccess,
        error => requestError(error),
        this.load
      )}
    updateRoomSuccess = payload => {
      requestSuccess("Room updated successfully!")
      this.getRoomDetails()
    }

    deleteRoom = (room) => {
      let payload = {
        ROOM_UUID: room.ROOM_UUID,
        IMAGE_NAME: room.IMAGE_NAME,
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/deleteRoom`,
        payload,
        this.deleteRoomSuccess,
        error => requestError(error),
        this.load
      )
    }
    deleteRoomSuccess = payload => {
      requestSuccess("Room deleted successfully!")
      this.getRoomDetails()
    }

    uploadNewImg = (values) => {
      console.log(values)
      const form_data = new FormData();
      form_data.append('add-room-img', values, values.name);
      console.log(form_data)
      // let payload = {
      //   body:
      // }
      // console.log(payload)
      // payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/uploadImg`,
        form_data,
        this.uploadNewImgSuccess,
        error => requestError(error),
        this.load
      )
    }
    uploadNewImgSuccess = payload => {
      console.log(payload)
      this.setState({newUploadImg:payload.image_source})
      requestSuccess("Image uploaded successfully!")
    }

    uploadUpdateImg = (values) => {
      console.log(values)
      const form_data = new FormData();
      form_data.append('update-room-img', values, values.name);
      console.log(form_data)
      Post(
        `/api/uploadImg`,
        form_data,
        this.uploadUpdateImgSuccess,
        error => requestError(error),
        this.load
      )
    }
    uploadUpdateImgSuccess = payload => {
      console.log(payload)
      this.setState({updateUploadImg:payload.image_source})
      requestSuccess("Image uploaded successfully!")
    }

    updateRoomLocationOnMap = (areas) => {
      let payload = {
        data:areas
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/updateRoomLocationOnMap`,
        payload,
        this.updateRoomLocationOnMapSuccess,
        error => requestError(error),
        this.load
      )
    }

    updateRoomLocationOnMapSuccess = payload => {
      requestSuccess('Map updated successfully!')
      this.getRoomDetails()
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}
          getRoomDetails={this.getRoomDetails}
          addRoom={this.addRoom}
          updateRoom={this.updateRoom}
          deleteRoom={this.deleteRoom}
          uploadNewImg={this.uploadNewImg}
          uploadUpdateImg={this.uploadUpdateImg}
          updateRoomLocationOnMap={this.updateRoomLocationOnMap}
          onChangeHOC={this.onChangeHOC}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;