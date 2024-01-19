"use client";

import React, { Component } from "react";
import _ from 'lodash'
import { storeItem } from 'utils/tokenStore'
import { requestError } from "utils/requestHandler";
import { Post } from "utils/axios";
import { SHA256} from 'crypto-js';

const HOC = (WrappedComponent) => {

  class WithHOC extends Component {
    
    state = {
      loading: false,
      loggedIn: false
    };

    onChangeHOC = (key, val) => this.setState({ [key]: val });

    load = (param) => this.setState({ loading: param });

    login = (values) => {
      Post(
        `/api/login`,
        {"LOGIN_NAME":values.username,"PWD":SHA256(values.password).toString()},
        this.loginSuccess,
        error => requestError(error),
        this.load
      )}
    loginSuccess = payload => {
      let combinedPayload = _.merge({}, ...payload.DATA)
      combinedPayload = _.mapValues(combinedPayload, value => _.toString(value));
      storeItem('LOGIN_TOKEN', JSON.stringify(combinedPayload))
      this.onChangeHOC('loggedIn',true)
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}
          login={this.login}
          onChangeHOC={this.onChangeHOC}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
