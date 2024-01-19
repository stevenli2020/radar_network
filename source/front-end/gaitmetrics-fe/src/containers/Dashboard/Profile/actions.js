"use client";

import React, { Component } from "react";
import { requestError } from "utils/requestHandler";
import { Get, Post, Put, Delete } from "utils/axios";

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
    };

    load = (param) => this.setState({ loading: param });

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
