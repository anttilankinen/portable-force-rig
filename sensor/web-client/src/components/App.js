import React, { Component } from 'react';
import socketIOClient from 'socket.io-client';
import Table from './Table';

import {Line} from 'react-chartjs-2';

export default class App extends Component {
  state = {
    current: [],
    saved: [],
    showTable: false
  }

  startRecording = () => {
    fetch('/api/sensor-controller/start')
    .then(res => res.text())
    .then(string => console.log(string));
  }

  stopRecording = () => {
    fetch('/api/sensor-controller/stop')
    .then(res => res.text())
    .then(string => console.log(string));
  }

  saveData = () => {
    const JSONdata = JSON.stringify({ data: this.state.current });

    fetch('/api/rpi/data', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSONdata,
    }).then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ current: [] });
    });
  }

  uploadData = () => {
    fetch('/api/data-upload/')
    .then(res => res.text())
    .then(string => console.log(string));
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
    const { response } = this.state;
    const options = {
      options: {
      title: {
        display: true,
        text: 'Graph of'
      }
    }};
    const data = {
      labels:response,
      datasets: [
        {
          label: 'Force',
          fill: false,
          lineTension: 0.1,
          backgroundColor: 'rgba(75,192,192,0.4)',
          borderColor: 'rgba(75,192,192,1)',
          borderCapStyle: 'butt',
          borderDash: [],
          borderDashOffset: 0.0,
          borderJoinStyle: 'miter',
          pointBorderColor: 'rgba(75,192,192,1)',
          pointBackgroundColor: '#fff',
          pointBorderWidth: 1,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: 'rgba(75,192,192,1)',
          pointHoverBorderColor: 'rgba(220,220,220,1)',
          pointHoverBorderWidth: 2,
          pointRadius: 1,
          pointHitRadius: 10,
          data:response,
        }
      ]
    };
    console.log(response);
    return (

      <div style={{ textAlign: 'center', padding: '100px' }}>
        <h1>Portable Force Rig Dashboard</h1>
        <h3>Incoming data: {this.state.current.join(', ')}</h3>
        <div style={{ marginTop: '20px '}}>
          <button className="ui green button" onClick={this.startRecording}>
            <i className="play icon"></i>Start
          </button>
          <button className="ui red button" onClick={this.stopRecording}>
            <i className="stop icon"></i>Stop
          </button>
          <button className="ui yellow button" onClick={this.saveData}>
            <i className="download icon"></i>Save
          </button>
          <button className="ui blue button" onClick={this.uploadData}>
            <i className="upload icon"></i>Upload
          </button>
          <button className="ui black button" onClick={this.showHistory}>
            <i className="list alternate outline icon"></i>History
          </button>


        </div>
        {this.state.showTable && <Table tableData={this.state.saved}/>}

        <div><Line data={data} options ={options}/></div>
      </div>
    );
  }
}
