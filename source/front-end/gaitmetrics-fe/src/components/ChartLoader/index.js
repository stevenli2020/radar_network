import React from "react"
import Loader from "react-loaders"

import "./index.scss"

const ChartLoader = () => {
  return (
    <div
      className="loader-container"
      style={{
        position: "absolute",
        backgroundColor: "rgba(0,0,0,0.3)",
        top: 50,
        left: 0,
        zIndex: 99,
      }}
    >
      <div className="loader-container-inner">
        <div className="text-center">
          <Loader type="ball-scale-ripple-multiple" />
        </div>
      </div>
    </div>
  )
}

export default ChartLoader
