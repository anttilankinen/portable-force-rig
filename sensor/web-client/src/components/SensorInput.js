import React, { Component } from 'react';
import { Select } from 'semantic-ui-react';


const options = [
  {
    key: 1,
    text: 'Sensor 1 (L)',
    value: 1
  },
  {
    key: 2,
    text: 'Sensor 2 (R)',
    value: 2
  }
];

export default class SensorInput extends Component {
  state = {
    status: 'Select sensor to calibrate'
  }

  handleSubmit = () => {
    this.setState({ status: `Selected sensor: ${this.props.sensor}` });
  }

  render() {
    const { handleChange } = this.props;

    return (
      <div>
        <h4>{this.state.status}</h4>
        <div style={{ margin: '20px 0' }}>
          <Select
            defaultValue={1}
            value={options.value}
            onChange={(event, {value}) => handleChange(value)}
            options={options}
            placeholder="Sensor selection"
          />
          <button className="ui button grey" onClick={this.handleSubmit}>Select</button>
        </div>
      </div>
    );
  }
}
