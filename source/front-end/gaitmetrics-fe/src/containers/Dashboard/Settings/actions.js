"use client";

import React, { Component } from "react";
import { Get, Post, Put, Delete } from "utils/axios";
import { requestError, requestSuccess } from "utils/requestHandler";
import { getItem } from 'utils/tokenStore'

const HOC = (WrappedComponent) => {
  class WithHOC extends Component {
    state = {
      loading: false,
      dataTypes: [],
      modes: [
        {value:1,label:'Day'},
        {value:2,label:'Day of Week'}
      ],
      alertConfigs: []
    };

    load = (param) => this.setState({ loading: param });

    getDataTypes = () => {
      let payload = {
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getDataTypes`,
        payload,
        this.getDataTypesSuccess,
        error => requestError(error),
        this.load
      )
    }

    getDataTypesSuccess = payload => {
      this.setState({dataTypes:payload.DATA})
    }

    getAlertConfigurations = () => {
      let payload = {
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/getAlertConfigurations`,
        payload,
        this.getAlertConfigurationsSuccess,
        error => requestError(error),
        this.load
      )
    }

    getAlertConfigurationsSuccess = payload => {
      // console.log(payload)
      this.setState({alertConfigs:payload.DATA})
    }

    setAlertConfigurations = (configs) => {
      let payload = {
        data:configs
      }
      payload = { ...JSON.parse(getItem("LOGIN_TOKEN")), ...payload }
      Post(
        `/api/setAlertConfigurations`,
        payload,
        this.setAlertConfigurationsSuccess,
        error => requestError(error),
        this.load
      )
    }

    setAlertConfigurationsSuccess = payload => {
      requestSuccess('Alert configurations updated successfully!')
    }

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
          setAlertConfigurations={this.setAlertConfigurations}
          getAlertConfigurations={this.getAlertConfigurations}
          getDataTypes={this.getDataTypes}
          upload={this.uploadLogo}
          onLoading={this.state.loading}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
