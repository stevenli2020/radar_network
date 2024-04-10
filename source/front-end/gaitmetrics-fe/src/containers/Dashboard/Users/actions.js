"use client";

import React, { Component } from "react";
import { requestError, requestSuccess } from "utils/requestHandler";
import { Post } from "utils/axios";
import _ from 'lodash'
import { getItem } from 'utils/tokenStore'

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
      users: [],
      admins:[],
      selectedUser: null,
      roomSuggestions:[],
      rooms:[]
    };

    onChangeHOC = (key, val) => this.setState({ [key]: val });

    load = (param) => this.setState({ loading: param });

    getUsers = () => Post(
        `/api/getAllUsers`,
        JSON.parse(getItem("LOGIN_TOKEN")),
        this.getUsersSuccess,
        error => requestError(error),
        this.load
      )
    getUsersSuccess = payload => {
      this.setState({ users: _.filter(payload.DATA, { TYPE: 0 }) })
      this.setState({ admins: _.filter(payload.DATA, { TYPE: 1 }) })
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
    
    registerUser = (values) => {
      let payload = {
        LOGIN_NAME: values.username,
        FULL_NAME: values.fullname,
        EMAIL: values.email,
        PHONE: values.phone,
        USER_TYPE: values.usertype,
        ROOM: values.rooms,
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/usersManagement`,
        payload,
        this.registerUserSuccess,
        error => requestError(error),
        this.load  
      )
    }
    registerUserSuccess = payload => {
      this.getUsers()
      requestSuccess("User added successfully!")
    }

    updateUser = (values) => {
      let payload = {
        USER_ID:this.state.selectedUser.ID,
        LOGIN_NAME: values.LOGIN_NAME,
        FULL_NAME: values.FULL_NAME,
        EMAIL: values.EMAIL,
        PHONE: values.PHONE,
        USER_TYPE: values.TYPE,
        ROOM: values.rooms,
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/updateUser`,
        payload,
        this.updateUserSuccess,
        error => requestError(error),
        this.load
      )}
    updateUserSuccess = payload => {
      this.getUsers()
      requestSuccess("User updated successfully!")
    }

    deleteUser = (user) => {
      let payload = {
        USER_ID:user.ID
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/deleteUser`,
        payload,
        this.deleteUserSuccess,
        error => requestError(error),
        this.load
      )}
    deleteUserSuccess = payload => {
      this.getUsers()
      requestSuccess("User deleted successfully!")
    }

    resetPassword = (user) => {
      let payload = {
        USER_ID:user.ID
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/sentEmail`,
        payload,
        this.resetPasswordSuccess,
        error => requestError(error),
        this.load
      )}
    resetPasswordSuccess = payload => {
      requestSuccess("Email sent successfully!")
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}

          getUsers={this.getUsers}
          registerUser={this.registerUser}
          updateUser={this.updateUser}
          deleteUser={this.deleteUser}
          resetPassword={this.resetPassword}
          suggestRoom={this.getRoomSuggestion}
          onChangeHOC={this.onChangeHOC}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
