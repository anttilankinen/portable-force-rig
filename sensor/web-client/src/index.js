import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import socketIOClient from 'socket.io-client';
import './index.css';

class App extends Component {
  state = {
    data: [],
    api: null
  }

  saveData = () => {
    const JSONdata = JSON.stringify({ data: this.state.data })
    fetch('/api/core/data', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSONdata,
    }).then(res => res.text())
    .then(data => console.log(data));
  }

  uploadData = () => {
    fetch('/api/data-upload/')
    .then(res => res.text())
    .then(data => console.log(data));
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
      <div style={{ textAlign: 'center' }}>
        <h1>Portable Force Rig API</h1>
        <h4>{this.state.data.join(', ')}</h4>
        <button onClick={this.saveData}>Save</button>
        <button onClick={this.uploadData}>Upload</button>
      </div>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));
