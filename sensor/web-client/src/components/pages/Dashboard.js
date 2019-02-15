import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import socketIOClient from 'socket.io-client';
import { chartOptions, chartData } from '../chartSettings';

export default class Dashboard extends Component {
  state = {
    current: [],
    started: false,
    status: 'Sensor ready!'
  }

  startRecording = () => {
    fetch('/api/sensor-controller/start')
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ started: true, status: 'Reading from sensor..' });
    });
  }

  stopRecording = () => {
    fetch('/api/sensor-controller/stop')
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ started: false, status: 'Sensor ready!' });
    });
  }

  saveData = () => {
    const { current } = this.state;
    if (current && current.length) {
      const JSONdata = JSON.stringify({ data: current });
      fetch('/api/rpi/data', {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSONdata,
      }).then(res => res.text())
      .then(string => {
        console.log(string);
        this.setState({ current: [], status: 'Recording successfully saved' });
      });
    }
  }

  clearData = () => {
    this.setState({ current: [] });
  }

  componentDidMount() {
    const socket = socketIOClient('http://localhost:7002');
    socket.on('connected', message => console.log(message));
    socket.on('new data', message => {
      this.setState({ current: [...this.state.current, message.data] });
    });
  }

  render() {
    const { current, started, status } = this.state;
    chartData.labels = current.map((value, index) => (index * 0.025).toFixed(3));
    chartData.datasets[0].data = current;

    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <h4>{status}</h4>
        <div><Line data={chartData} options={chartOptions} height={350}/></div>
        <div style={{ margin: '20px 0 40px 0'}}>
          {!started &&
            <button className="ui green button" onClick={this.startRecording}>
              <i className="play icon"></i>Start
            </button>
          }
          {started &&
            <button className="ui red button" onClick={this.stopRecording}>
              <i className="stop icon"></i>Stop
            </button>
          }
          <button className="ui yellow button" onClick={this.clearData} disabled={started}>
            <i className="trash icon"></i>Clear
          </button>
          <button className="ui blue button" onClick={this.saveData} disabled={started}>
            <i className="download icon"></i>Save
          </button>
        </div>
        <img src="http://localhost:7007/stream.mjpg" alt="Video stream currently unavailable" width="640" height="480" />
      </div>
    );
  }
}
