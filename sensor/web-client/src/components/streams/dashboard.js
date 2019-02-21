import React, {Component} from 'react';
import {Line} from 'react-chartjs-2';
import socketIOClient from 'socket.io-client';

import {chartOptions, chartData} from '../chartSettings';
import AntSizeInput from '../AntSizeInput.js';
export default class Dashboard extends Component {
  state = {
    current: [],
    started: false
  }

  startRecording = () => {
    this.setState({started: true});
    fetch('/api/sensor-controller/start').then(res => res.text()).then(string => console.log(string));
  }

  stopRecording = () => {
    this.setState({started: false});
    fetch('/api/sensor-controller/stop').then(res => res.text()).then(string => console.log(string));
  }

  saveData = () => {
    const {current} = this.state;
    if (current && current.length) {
      const JSONdata = JSON.stringify({data: current});

      fetch('/api/rpi/data', {
        method: 'post',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSONdata
      }).then(res => res.text()).then(string => {
        console.log(string);
        this.setState({current: []});
      });
    }
  }

  clearData = () => {
    this.setState({current: []});
  }

  uploadData = () => {
    fetch('/api/data-upload/').then(res => res.text()).then(string => console.log(string));
  }

  componentDidMount() {
    const socket = socketIOClient('http://localhost:7002');
    socket.on('connected', message => console.log(message));
    socket.on('new data', message => {
      this.setState({
        current: [
          ...this.state.current,
          message.data
        ]
      });
    });
  }

  render() {
    const {current, started} = this.state;
    console.log(current);
    chartData.labels = current.map((index) => (index * 0.025).toFixed(3));
    chartData.datasets[0].data = current;

    return (<div style={{
        textAlign: 'center',
        padding: '20px'
      }}>
      <h4>Status</h4>
      <div><Line data={chartData} options={chartOptions} height={350}/></div>
      <div style={{
          marginTop: '20px '
        }}>
        <AntSizeInput/>
        <br/> {
          !started && <button style={{
                margin: '0.25em'
              }} className="ui green button" onClick={this.startRecording}>
              <i className="play icon"></i>Start
            </button>
        }
        {
          started && <button style={{
                margin: '0.25em'
              }} className="ui red button" onClick={this.stopRecording}>
              <i className="stop icon"></i>Stop
            </button>
        }
        <button className="ui yellow button" style={{
            margin: '0.25em'
          }} onClick={this.clearData} disabled={started}>
          <i className="trash icon"></i>Clear
        </button>

        <button style={{
            margin: '0.25em'
          }} className="ui blue button" onClick={this.saveData} disabled={started}>
          <i className="download icon"></i>Save
        </button>
        <button style={{
            margin: '0.25em'
          }} className="ui brown button" onClick={this.uploadData}>
          <i className="upload icon"></i>Upload
        </button>
      </div>

    </div>);
  }
}
