import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import socketIOClient from 'socket.io-client';

import 'semantic-ui-css/semantic.min.css';
import './index.css';

class App extends Component {
  state = {
    data: [],
    api: null
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
    const JSONdata = JSON.stringify({ data: this.state.data });

    fetch('/api/rpi/data', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSONdata,
    }).then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ data: [] })
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
      json.rows.forEach(row => {
        let antSize = row['ant_size'];
        let readings = row['readings'];
        console.log(`${antSize}: ${readings}`);
      });
    });
  }

  componentDidMount() {
    const socket = socketIOClient('http://192.168.99.100:7002');
    socket.on('connected', message => console.log(message));
    socket.on('new data', message => {
      this.setState({ data: [...this.state.data, message.data] });
    });
  }

  render() {
    return (
      <div style={{ textAlign: 'center', paddingTop: '100px' }}>
        <h1>Portable Force Rig Dashboard</h1>
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
        <h3>Incoming data: {this.state.data.join(', ')}</h3>
      </div>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));
