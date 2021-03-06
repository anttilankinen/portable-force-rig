import React, { Component } from 'react';
import { Select } from 'semantic-ui-react';

const options = [
  {
    key: 's',
    text: 'Small',
    value: 'Small'
  },
  {
    key: 'm',
    text: 'Medium',
    value: 'Medium'
  },
  {
    key: 'l',
    text: 'Large',
    value: 'Large'
  }
];

export default class AntSizeInput extends Component {
  state = {
    status: 'Select ant size before starting'
  }

  handleSubmit = () => {
    this.setState({ status: `Selected ant size: ${this.props.antSize}` });
  }

  render() {
    const { handleChange } = this.props;

    return (
      <div>
        <h4>{this.state.status}</h4>
        <div style={{ margin: '20px 0' }}>
          <Select
            defaultValue={'Large'}
            value={options.value}
            onChange={(event, {value}) => handleChange(value)}
            options={options}
            placeholder="Ant size"
          />
          <button className="ui button grey" onClick={this.handleSubmit}>Select</button>
        </div>
      </div>
    );
  }
}
