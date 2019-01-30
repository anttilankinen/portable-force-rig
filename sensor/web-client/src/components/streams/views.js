import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import socketIOClient from 'socket.io-client';
import { chartOptions, chartData } from '../chartSettings';

{/*

export default class Dashboard extends Component {
  state = {
    current: [],
    started: false
  }

  componentDidMount() {
    const socket = socketIOClient('http://localhost:7002');
    socket.on('connected', message => console.log(message));
    socket.on('new data', message => {
      this.setState({ current: [...this.state.current, message.data] });
    });
  }

  render() {
    const { current, started } = this.state;
    chartData.labels = current.map((value, index) => (index * 0.025).toFixed(3));
    chartData.datasets[0].data = current;

    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <h4>Status</h4>
        <div><Line data={chartData} options={chartOptions} height={350}/></div>

      </div>
    );
  }
}
  */}
