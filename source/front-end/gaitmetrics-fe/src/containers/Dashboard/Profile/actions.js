"use client";

import React, { Component } from "react";
import { requestError } from "utils/requestHandler";
import { Get, Post, Put, Delete } from "utils/axios";

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
      profile: null
    };

    load = (param) => this.setState({ loading: param });

    getProfile = () => {
      Get(
        `/api/profile`,
        this.getProfileSuccess,
        error => requestError(error),
        this.load
      )
    }

    getProfileSuccess = payload => {
      this.setState({profile:payload.DATA})
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          getProfile={this.getProfile}
          onLoading={this.state.loading}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
