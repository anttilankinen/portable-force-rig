import React, {Component} from 'react';
import {Line} from 'react-chartjs-2';

import {chartOptions, chartData} from '../chartSettings';

class Views extends Component {

  state = {
    view: []

  }

  componentDidMount() {

    const id = this.props.location.pathname.split("/")[2];
    fetch(`/api/rpi/data/${id}`).then(res => res.json()).then(json => {

      this.setState({view: json.row[0]});
    });

  }

  render() {
    const {view} = this.state;
    console.log(view);
    if (view.readings) {
      const readings = JSON.parse(view.readings);
      chartData.labels = readings.map((value, index) => (index * 0.025).toFixed(3));
      chartData.datasets[0].data = readings;
    }

    return (<div>
      <div style={{
          textAlign: 'left',
          padding: '20px'
        }}>
        <h3 >Date & Time : {view.date_time}</h3>
        <h3>Size of ant : {view.ant_size}</h3>
      </div>

      <div style={{
          textAlign: 'center',
          padding: '20px'
        }}>
        <div>
          <h4>Readings</h4>
          <Line data={chartData} options={chartOptions} height={350}/></div>
        <div style={{
            textAlign: 'right',
            padding: '20px'
          }}></div>
      </div>
    </div>)
  }

}

export default Views;
