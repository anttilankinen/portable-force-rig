import React, { Component } from 'react';
import { Input } from 'semantic-ui-react';

export default class Calibrate extends Component {
  state = {
    started: false,
    ready: true,
    count: 0,
    weight: '',
    status: 'Click \'Calibrate\' to start calibrating'
  }

  start = () => {
    this.setState({ started: true, status: 'Remove all weights and click \'Run\' to start zeroing' });
  }

  run = () => {
    const { count, weight } = this.state;

    this.setState({ ready: false, status: 'Calibrating..' });
    let value = count ? (weight ? weight : 0) : 0;

    fetch('http://localhost:7006/calibration/begin', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ weight: value }),
    }).then(res => res.text())
    .then(string => {
      this.setState({
        ready: true,
        count: count + 1,
        weight: '',
        status: 'Run calibration against a known weight'
      });
    });
  }

  end = () => {
    fetch('http://localhost:7006/calibration/end')
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ started: false, count: 0, status: 'Calibration done!' });
    });
  }

  handleChange = (event, data) => {
    this.setState({ weight: parseFloat(event.target.value) });
  }

  render() {
    const { started, ready, count, weight, status } = this.state;

    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div style={{ margin: '20px 0' }}>
          {!started &&
            <button className="ui teal button" onClick={this.start}>
              <i className="sync icon"></i>Calibrate
            </button>
          }
          {started &&
            <button className="ui teal button" onClick={this.end} disabled={!ready}>
              <i className="stop icon"></i>End
            </button>
          }
          {started &&
            <button className="ui teal button" onClick={this.run} disabled={!ready}>
              <i className="play icon"></i>Run
            </button>
          }
          <Input
            type="number"
            disabled={!count}
            loading={!ready}
            onChange={this.handleChange}
            placeholder='Enter weight (g)'
            value={weight}
          />
        </div>
        <h4>{status}</h4>
      </div>
    )
  }
}
