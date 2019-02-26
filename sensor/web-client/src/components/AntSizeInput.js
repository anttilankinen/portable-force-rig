import React, {Component} from "react";
import {Button, Form} from 'semantic-ui-react'

const options = [
  {
    key: 's',
    text: 'Small',
    value: 'Small'
  }, {
    key: 'm',
    text: 'Medium',
    value: 'Medium'
  }, {
    key: 'l',
    text: 'Large',
    value: 'Large'
  }
]

export default class AntSizeInput extends Component {
  constructor(props) {
    super(props);
    this.state = {
      antsize: "",
      status: "Key in the size of the ant before starting"
    };

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    this.setState({
      status: "An ant size was submitted: " + this.state.antsize
    });
    event.preventDefault();
  }

  render() {
    const {status} = this.state;

    return (<div class="ui one column stackable center aligned page grid">

      <Form class="column twelve wide" onSubmit={this.handleSubmit}>
        <h4>{status}</h4>
        <Form.Group >
          <Form.Select value={options.value} onChange={this.props.handleChange} options={options} placeholder="Ant Size"/>
          <Button>Submit</Button>
        </Form.Group>

      </Form>

    </div>);
  }
}
