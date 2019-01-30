import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import socketIOClient from 'socket.io-client';
import { Link } from 'react-router-dom'

import Table from '../Table';
import { chartOptions, chartData } from '../chartSettings';


export default class History extends Component {
  state = {
    current: [],
    saved: [],
    showTable: false,
    started: false
  }

  showHistory = () => {
    fetch('/api/rpi/data')
    .then(res => res.json())
    .then(json => {
      const history = json.rows.map(row => ({
        date: '12/10/2018',
        antSize: row.ant_size,
        readings: row.readings
      }))
      this.setState({ saved: history, showTable: !this.state.showTable });
    });
  }

  componentDidMount() {
    const socket = socketIOClient('http://192.168.99.100:7002');
    socket.on('connected', message => console.log(message));
    socket.on('new data', message => {
      this.setState({ current: [...this.state.current, message.data] });
    });
  }

  render() {
    const { current, saved, showTable, started } = this.state;

    chartData.labels = current.map((value, index) => index * 0.25);
    chartData.datasets[0].data = current;

    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        {/* <h3>Incoming data: {this.state.current.join(', ')}</h3> */}
        <div><Line data={chartData} options={chartOptions} height={350}/></div>

        {showTable && <Table tableData={saved}/>}
      </div>
    );
  }
}
