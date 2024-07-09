"use client";

import React, { Component } from "react";
import { requestError, requestSuccess } from "utils/requestHandler";
import { Get, Post, Put, Delete } from "utils/axios";
import { getItem } from 'utils/tokenStore'

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
      room_uuid:null,
      room:null,
      room_name:'-',
      preselect_area: [],
      width:500,
      height:400
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
      let room_name = payload.DATA[0].ROOM_NAME + "@" + payload.DATA[0].ROOM_LOC
      this.setState({room_name:room_name})
    }

    getPreselectArea = (room_id) => {
      let payload = {
        room_id:room_id
      }
      Post(
        `/api/getFilterLocationHistory`,
        payload,
        this.getPreselectAreaSuccess,
        error => requestError(error),
        this.load
      )
    }

    getPreselectAreaSuccess = payload => {
      // console.log(payload)
      this.setState({preselect_area:payload.DATA})
    }

    updateFilterArea = (areas) => {
      let payload = {
        room_id:this.state.room.ID,
        data:areas
      }
      Post(
        `/api/updateFilterLocationHistory`,
        payload,
        this.updateFilterAreaSuccess,
        error => requestError(error),
        this.load
      )
    }

    updateFilterAreaSuccess = payload => {
      requestSuccess('Area updated successfully!')
    }

    initView = (room_id) =>{
      this.setState({room_uuid:room_id})
      this.getRoomDetail(room_id)
    }

    load = (param) => this.setState({ loading: param });

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          initView={this.initView}
          getPreselectArea={this.getPreselectArea}
          updateFilterArea={this.updateFilterArea}
          onLoading={this.state.loading}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
