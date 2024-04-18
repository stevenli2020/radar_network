"use client";

import React, { Component } from "react";
import _ from 'lodash'
import { Post } from "utils/axios";
import { SHA256} from 'crypto-js';
import { requestError, requestSuccess } from "utils/requestHandler";

const HOC = (WrappedComponent) => {

  class WithHOC extends Component {
    
    state = {
      loading: false,
      loggedIn: false
    };

    onChangeHOC = (key, val) => this.setState({ [key]: val });

    load = (param) => this.setState({ loading: param });

    addPassword = (values,code) => {
      Post(
        `/api/updatePassword`,
        {"LOGIN_NAME":values.username,"PWD":SHA256(values.password).toString(),"CPWD":SHA256(values.cpassword).toString(),"CODE":code},
        this.addPasswordSuccess,
        error => requestError(error),
        this.load
      )}
    addPasswordSuccess = payload => {
      requestSuccess("Password added successfully!")
    }

    resetPassword = (values,code) => {
      Post(
        `/api/updatePassword`,
        {"LOGIN_NAME":values.username,"PWD":SHA256(values.password).toString(),"CPWD":SHA256(values.cpassword).toString(),"CODE":code},
        this.resetPasswordSuccess,
        error => requestError(error),
        this.load
      )}
    resetPasswordSuccess = payload => {
      requestSuccess("Password reset successfully!")
    }

    render = () => {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          onLoading={this.state.loading}
          addPassword={this.addPassword}
          resetPassword={this.resetPassword}
          onChangeHOC={this.onChangeHOC}
        />
      );
    };
  }
  return WithHOC;
};

export default HOC;
