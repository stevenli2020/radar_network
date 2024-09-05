"use client";

import React, { Component } from "react";
import { Get, Post, Put, Delete, PostForm } from "utils/axios";
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
      alertConfigs: [],
      algoConfigs: {},
      notifier:[],
      updateConfigFlag: 0
    };

    load = (param) => this.setState({ loading: param });

    getDataTypes = () => {
      let payload = {
      }
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
      Post(
        `/api/setAlertConfigurations`,
        payload,
        this.setAlertConfigurationsSuccess,
        error => requestError(error),
        this.load
      )
    }

    setAlertConfigurationsSuccess = payload => {
      requestSuccess('Algorithm configurations updated successfully!')
    }

    getAlgoConfigurations = () => {
      Get(
        `/api/algo-config`,
        this.getAlgoConfigurationsSuccess,
        error => requestError(error),
        this.load
      )
    }

    getAlgoConfigurationsSuccess = payload => {
      this.setState({algoConfigs:payload.DATA})
    }

    setAlgoConfigurations = (configs) => {
      let payload = {
        data:configs
      }
      Put(
        `/api/algo-config`,
        payload,
        this.setAlgoConfigurationsSuccess,
        error => requestError(error),
        this.load
      )
    }

    setAlgoConfigurationsSuccess = payload => {
      requestSuccess('Algorithm configurations updated successfully!')
      this.setState({updateConfigFlag:this.state.updateConfigFlag+1})
    }

    getNotifier = () => {
      Get(
        `/api/notifier`,
        this.getNotifierSuccess,
        error => requestError(error),
        this.load
      )
    }

    getNotifierSuccess = payload => {
      this.setState({notifier:payload.DATA})
    }

    addNotifier = (configs) => {
      let payload = {
        EMAIL:configs
      }
      Post(
        `/api/notifier`,
        payload,
        this.addNotifierSuccess,
        error => requestError(error),
        this.load
      )
    }

    addNotifierSuccess = payload => {
      requestSuccess('New notifier added successfully!')
      this.getNotifier()
    }

    deleteNotifier = (email) => {
      Delete(
        `/api/notifier/${email}`,
        this.deleteNotifierSuccess,
        error => requestError(error),
        this.load
      )
    }

    deleteNotifierSuccess = payload => {
      requestSuccess('Notifier deleted successfully!')
      this.getNotifier()
    }

    uploadLogo = (values) => {
      const form_data = new FormData();
      form_data.append('logo', values, "logo.png");
      console.log(form_data)
      PostForm(
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

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          setAlertConfigurations={this.setAlertConfigurations}
          getAlertConfigurations={this.getAlertConfigurations}
          setAlgoConfigurations={this.setAlgoConfigurations}
          getAlgoConfigurations={this.getAlgoConfigurations}
          getMQTTClientID={this.getMQTTClientID}
          setClientConnection={this.setClientConnection}
          getNotifier={this.getNotifier}
          addNotifier={this.addNotifier}
          deleteNotifier={this.deleteNotifier}
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
