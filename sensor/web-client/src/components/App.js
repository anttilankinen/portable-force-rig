import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import socketIOClient from 'socket.io-client';
import Table from './Table';
import { chartOptions, chartData } from './chartSettings';

export default class App extends Component {
  state = {
    current: [],
    saved: [],
    showTable: false,
    started: false
  }

  startRecording = () => {
    this.setState({ started: true });
    fetch('/api/sensor-controller/start')
    .then(res => res.text())
    .then(string => console.log(string));
  }

  stopRecording = () => {
    this.setState({ started: false });
    fetch('/api/sensor-controller/stop')
    .then(res => res.text())
    .then(string => console.log(string));
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
        this.setState({ current: [] });
      });
    }
  }

  clearData = () => {
    this.setState({ current: [] });
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
        date: row.date_time,
        antSize: row.ant_size,
        readings: row.readings
      }))
      this.setState({ saved: history, showTable: !this.state.showTable });
    });
  }

  componentDidMount() {
    const socket = socketIOClient('http://localhost:7002');
    socket.on('connected', message => console.log(message));
    socket.on('new data', message => {
      this.setState({ current: [...this.state.current, message.data] });
    });
  }

  render() {
    const { current, saved, showTable, started } = this.state;

    let dataToDisplay = current.slice(-20);
    chartData.labels = dataToDisplay.map((value, index) => (index * 0.025).toFixed(2));
    chartData.datasets[0].data = dataToDisplay;

    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <h1>Portable Force Rig Dashboard</h1>
        <div><Line data={chartData} options={chartOptions} height={350}/></div>
        <div style={{ marginTop: '20px '}}>
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
          <button className="ui brown button" onClick={this.uploadData}>
            <i className="upload icon"></i>Upload
          </button>
          <button className="ui black button" onClick={this.showHistory}>
            <i className="list alternate outline icon"></i>History
          </button>
        </div>
        {showTable && <Table tableData={saved}/>}
      </div>
    );
  }
}
