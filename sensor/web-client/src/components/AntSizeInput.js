import React, { Component } from "react";
import { Button, Form } from 'semantic-ui-react'

const options = [{
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
}]

export default class AntSizeInput extends Component {
  constructor(props) {
    super(props);
    this.state = {
      antsize: "",
      status: "Key in the size of the ant before starting"
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event, data) {
    const { value } = data;
    console.log(value);
    this.setState({ antsize: value });
  }

  handleSubmit(event) {
    this.setState({
      status: "An ant size was submitted: " + this.state.antsize
    });
    event.preventDefault();
  }
  render() {
    const { antsize, status } = this.state;

    return (<div>

              <Form onSubmit={this.handleSubmit}>
                <h4>{status}</h4>
                <Form.Group >
                  <Form.Select value={options.value} onChange={this.handleChange} options={options} placeholder="Ant Size"/>
                  <Button>Submit</Button>
                </Form.Group>

              </Form>

    </div>);
  }
}