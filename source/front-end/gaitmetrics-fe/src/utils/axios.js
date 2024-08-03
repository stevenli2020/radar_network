import Axios from 'axios'
import getDomainURL from 'utils/api'
import { getItem } from 'utils/tokenStore'

export const Get = (url, response, error, load, isPublic ) => {
  load(true)
  let token = getItem("LOGIN_TOKEN")
  Axios.defaults.headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    ...token ? {'Authorization': `Bearer ${token}`} : {}
  }
  return Axios.get(`${getDomainURL()}${url}`).then(res => {
    response(res.data)
    load(false)
  }).catch(err => {
    console.error( err )
    if (err && err.response) {
      if (err.response.status === 502) {

      }
      else if (err.response.status === 401) {

      } else if (err.response.status === 500) {
        error('Server encountered issues. Please contact your system admin for assistance.')
      } else {
        error(err.response.data )
      }
    } else if (err.response) {
      error(err.response.data)
    } else {
      error('You are disconnnected from the internet, please reconnect to use the system. If problem persists, please contact the system admin.')
    }
    load(false)
  })
}

export const Post = (url, data, response, error, load, isPublic) => {
  load(true)
  let token = getItem("LOGIN_TOKEN")
  Axios.defaults.headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    ...token ? {'Authorization': `Bearer ${token}`} : {}
  }
  const requestUrl = url.indexOf( 'http' ) > -1 ? url : `${getDomainURL()}${ url }`
  return Axios.post( requestUrl, data ).then( res => {
    if ((res.data.hasOwnProperty("ERROR") && res.data.ERROR.length === 0) || !res.data.hasOwnProperty("ERROR")){
      response (res.data )
    }else{
      if (Array.isArray(res.data.ERROR)){
        res.data.ERROR.map((errorObject) => {
          // Assuming each errorObject has only one key-value pair
          const key = Object.keys(errorObject)[0]; // Get the key (e.g., "Username")
          const value = errorObject[key]; // Get the corresponding value (e.g., "Username is incorrect!")
        
          error(value)
        })
      }else{
        error(res.data.ERROR)
      }
      
    }
    
    load( false )
  }).catch( err => {
    console.error( err )
    if ( err && err.response ) {
      if (err.response.status === 502) {

      }
      else if( err.response.status === 413 ){
        error('The file is too large. Please try with smaller file')
      } else if (err.response.status === 401) {
        error('User unauthorized!')
      } else {
        error( err.response.data )
      }
    } else {
      error('You are disconnnected from the internet, please reconnect to use the system. If problem persists, please contact the system admin.')
    }
    load( false )
  })
}

export const PostForm = (url, data, response, error, load, isPublic) => {
  load(true)
  let token = getItem("LOGIN_TOKEN")
  Axios.defaults.headers = {
    'Content-Type': 'multipart/form-data',
    'Access-Control-Allow-Origin': '*',
    ...token ? {'Authorization': `Bearer ${token}`} : {}
  }
  const requestUrl = url.indexOf( 'http' ) > -1 ? url : `${getDomainURL()}${ url }`
  return Axios.post( requestUrl, data ).then( res => {
    if ((res.data.hasOwnProperty("ERROR") && res.data.ERROR.length === 0) || !res.data.hasOwnProperty("ERROR")){
      response (res.data )
    }else{
      if (Array.isArray(res.data.ERROR)){
        res.data.ERROR.map((errorObject) => {
          // Assuming each errorObject has only one key-value pair
          const key = Object.keys(errorObject)[0]; // Get the key (e.g., "Username")
          const value = errorObject[key]; // Get the corresponding value (e.g., "Username is incorrect!")
        
          error(value)
        })
      }else{
        error(res.data.ERROR)
      }
      
    }
    
    load( false )
  }).catch( err => {
    console.error( err )
    if ( err && err.response ) {
      if (err.response.status === 502) {

      }
      else if( err.response.status === 413 ){
        error('The file is too large. Please try with smaller file')
      } else if (err.response.status === 401) {
        error('User unauthorized!')
      } else {
        error( err.response.data )
      }
    } else {
      error('You are disconnnected from the internet, please reconnect to use the system. If problem persists, please contact the system admin.')
    }
    load( false )
  })
}

export const Put = (url, data, response, error, load, isPublic, customToken ) => {
  load(true)
  let token = getItem("LOGIN_TOKEN")
  Axios.defaults.headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    ...token ? {'Authorization': `Bearer ${token}`} : {}
  }
  return Axios.put(`${getDomainURL()}${url}`, data).then(res => {
    response(res.data)
    load(false)
  }).catch(err => {
    console.error( err )
    if (err && err.response && err.response.status) {
      if (err.response.status === 502) {

      }
      else if (err.response.status === 500) {
        error('Server encountered issues. Please contact your system admin for assistance.')
      } else if(err.response.status === 422){
        error( err.response.data )
      } else if( err.response.status === 413 ){
        error('The file is too large. Please try with smaller file')
      } else if (err.response.status === 401) {
        
      } else {
        error( err.response.data )
      }
    } else if (err) {
      error(err.response.data)
    } else {
      error('You are disconnnected from the internet, please reconnect to use the system. If problem persists, please contact the system admin.')
    }
    load(false)
  })
}

export const Delete = (url, response, error, load, isPublic) => {
  load(true)
  let token = getItem("LOGIN_TOKEN")
  Axios.defaults.headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    ...token ? {'Authorization': `Bearer ${token}`} : {}
  }
  return Axios.delete(`${getDomainURL()}${url}`).then(res => {
    response(res.data)
    load(false)
  }).catch(err => {
    console.error( err )
    if (err && err.response && err.response.status) {
      if (err.response.status === 502) {

      }
      else if (err.response.status === 500) {
        error('Server encountered issues. Please contact your system admin for assistance.')
      } else if(err.response.status === 422){
        error( err.response.data )
      } else if (err.response.status === 401) {

      } else {
        error(err.response.data)
      }
    } else if (err) {
      error(err.response.data[0])
    } else {
      error('You are disconnnected from the internet, please reconnect to use the system. If problem persists, please contact the system admin.')
    }
    load(false)
  })
}