"use client";

import React, { Component } from "react";
import { Get, Post, Put, Delete } from "utils/axios";
import { requestError, requestSuccess } from "utils/requestHandler";

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
    };

    load = (param) => this.setState({ loading: param });

    uploadLogo = (values) => {
      const form_data = new FormData();
      form_data.append('logo', values, "logo.png");
      console.log(form_data)
      Post(
        `/api/uploadLogo`,
        form_data,
        this.uploadLogoSuccess,
        error => requestError(error),
        this.load
      )
    }
    uploadLogoSuccess = payload => {
      requestSuccess("Logo updated successfully! Refresh to take effect!")
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          upload={this.uploadLogo}
          onLoading={this.state.loading}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
