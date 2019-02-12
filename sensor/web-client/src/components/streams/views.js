import React, {Component} from 'react';
import {Line} from 'react-chartjs-2';

import {chartOptions, chartData} from '../chartSettings';

class Views extends Component {

  state = {
    view: []

  }

  componentDidMount() {

    const index = this.props.location.pathname.split("/")[2];

    fetch('/api/rpi/data').then(res => res.json()).then(json => {
      const history = JSON.parse(json.rows[index-1].readings);
      this.setState({view: history});
    });
  }

  render() {
    const {view} = this.state;

    chartData.labels = view.map((index) => (index * 0.025).toFixed(3));
    chartData.datasets[0].data = view;

    return (<div style={{
        textAlign: 'center',
        padding: '20px'
      }}>
      <h4>Status</h4>
      <div><Line data={chartData} options={chartOptions} height={350}/></div>

    </div>)
  }

}

export default Views;
