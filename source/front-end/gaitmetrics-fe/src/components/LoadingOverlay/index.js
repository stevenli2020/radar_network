import React from "react"
import Loader from "react-loaders"

import "./index.scss"

const LoadingOverlay = () => {
  return (
    <div
      className="loader-container"
      style={{
        position: "fixed",
        backgroundColor: "rgba(0,0,0,0.3)",
        top: 0,
        left: 0,
        zIndex: 999,
      }}
    >
      <div className="loader-container-inner">
        <div className="text-center">
          <Loader type="ball-pulse-rise" />
        </div>
      </div>
    </div>
  )
}

export default LoadingOverlay
