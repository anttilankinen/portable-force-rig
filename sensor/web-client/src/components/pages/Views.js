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

    if (view.readings) {
      const readings = JSON.parse(view.readings);
      chartData.labels = readings.map((value, index) => (index * 0.025).toFixed(3));
      chartData.datasets[0].data = readings;
    }

    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <h4>{view.date_time}</h4>
        <div>
          <Line data={chartData} options={chartOptions} height={350}/>
        </div>
      </div>
    )
  }
}
