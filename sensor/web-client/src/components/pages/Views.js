import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import { chartOptions, chartData } from '../chartSettings';

export default class Views extends Component {
  state = {
    view: []
  }

  componentDidMount() {
    const id = this.props.location.pathname.split("/")[2];

    fetch(`/api/rpi/data/${id}`)
    .then(res => res.json())
    .then(json => {
      this.setState({ view: json.row[0] });
    });
  }

  render() {
    const { view } = this.state;
    let maxForce = 0;

    if (view.readings) {
      const readings = JSON.parse(view.readings);
      chartData.labels = readings.map((value, index) => (index * 0.025).toFixed(3));
      chartData.datasets[0].data = readings;
      maxForce = Math.max(...JSON.parse(view.readings));
    }

    return (
      <div>
        <div style={{ textAlign: 'left', padding: '20px' }}>
          <h3>Date: {view.date_time}</h3>
          <h3>Ant size: {view.ant_size}</h3>
          <h3>Max bite force: {maxForce}</h3>
        </div>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <h4>Readings</h4>
          <Line data={chartData} options={chartOptions} height={350}/>
          <video src={`/recordings/${view.file_name}`} type="video/mp4" width="600" height="400" muted controls>
            Recording
          </video>
        </div>
      </div>
    )
  }
}
