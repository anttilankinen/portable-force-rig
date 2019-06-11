import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import socketIOClient from 'socket.io-client';
import { chartOptions, chartData } from '../chartSettings';
import AntSizeInput from '../AntSizeInput';
import uuidv4 from 'uuid/v4';

export default class Dashboard extends Component {
  state = {
    antSize: 'Large',
    current: [],
    currentId: null,
    started: false,
    status: 'Sensor ready!'
  }

  updateAntSize = (antSize) => {
    this.setState({ antSize: antSize });
  }

  startRecording = () => {
    const id = uuidv4();
    this.setState({ currentId: id });
    fetch('http://localhost:7007/record/begin', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id }),
    }).then(res => res.text())
    .then(string => {
      console.log(string);
    });

    fetch('/api/sensor/start', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ size: this.state.antSize.toLowerCase() }),
    })
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ started: true, status: 'Reading from sensor..' });
    });
  }

  stopRecording = () => {
    fetch('http://localhost:7007/record/end')
      .then(res => res.text())
      .then(string => console.log(string));

    fetch('/api/sensor/stop')
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ started: false, status: 'Sensor ready!' });
    });
  }

  saveData = () => {
    const { antSize, current, currentId } = this.state;
    if (current && current.length) {
      const JSONdata = JSON.stringify({ id: currentId, antSize: antSize, data: current });
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
    this.socket = socketIOClient('http://localhost:7002');
    this.socket.on('connected', message => console.log(message));
    this.socket.on('new data', message => {
      this.setState({ current: [...this.state.current, message.data] });
    });
  }

  componentWillUnmount() {
    const { antSize, current, currentId, started } = this.state;
    if (started) {
      fetch('/api/sensor/stop')
      .then(res => res.text())
      .then(string => {
        console.log(string);
      });
    }
    if (current && current.length) {
      const JSONdata = JSON.stringify({ id: currentId, antSize: antSize, data: current });
      fetch('/api/rpi/data', {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSONdata,
      }).then(res => res.text())
      .then(string => {
        console.log(string);
      });
    }
    this.socket.close();
  }

  render() {
    const { antSize, current, started, status } = this.state;
    const display = current.slice(-500);
    chartData.datasets[0].data = display;
    chartData.labels = current.map((value, index) => (index * 0.025).toFixed(3)).slice(-500);

    return (
      <div style={{ textAlign: 'center', padding: '10px', height: '400px', width: 'auto' }}>
        <h4>{status}</h4>
        <Line data={chartData} options={chartOptions} height={350}/>
        <div style={{ margin: '10px 0 40px 0'}}>
          <AntSizeInput antSize={antSize} handleChange={this.updateAntSize}/>
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
