import React, {Component} from 'react';
import {Line} from 'react-chartjs-2';
import {Grid, Form, Button, Input} from 'semantic-ui-react'
import {chartOptions, chartData} from '../chartSettings';

class Views extends Component {

  state = {
    view: [],
    clicked: false,
    emailinput: ''
  }

  componentDidMount() {

    const id = this.props.location.pathname.split("/")[2];
    fetch(`/api/rpi/data/${id}`).then(res => res.json()).then(json => {

      this.setState({view: json.row[0]});
    });

  }

  setclicked = () => {
    this.setState({clicked: true});
  }

  handleChange(event, data) {
    this.setState({emailinput: data.value});
  }

  handleSubmit(event) {

    let email = this.state.emailinput;
    console.log(email);
    {/* fetch(`/api/data-upload/csv?email=${email}`).then(res => res.text()).then(string => console.log(string)); */
    }
    event.preventDefault();
  }

  render() {
    const {view, clicked} = this.state;

    if (view.readings) {
      const readings = JSON.parse(view.readings);
      chartData.labels = readings.map((value, index) => (index * 0.025).toFixed(3));
      chartData.datasets[0].data = readings;
    }

    return (<div>

      <Grid columns={2}>
        <Grid.Row>
          <Grid.Column>
            <div style={{
                textAlign: 'left',
                paddingTop: '20px',
                paddingLeft: '40px'
              }}>
              <h3 >Date & Time : {view.date_time}</h3>
              <h3>Size of ant : {view.ant_size}</h3>
              <h3>Max Bite Force : {view.readings && Math.max(...JSON.parse(view.readings))}
              </h3>
            </div>
          </Grid.Column>
          <Grid.Column>
            <div style={{
                textAlign: 'right',
                paddingTop: '20px',
                paddingRight: '40px'
              }}>
              {
                !clicked && <button className="ui green button" style={{
                      margin: '0.25em'
                    }} onClick={this.setclicked}>
                    <i className="file excel outline icon"></i>Export CSV
                  </button>
              }

              {
                clicked && <div>
                    <Form onSubmit={this.handleSubmit.bind(this)}>
                      <Input onChange={this.handleChange.bind(this)} placeholder="Enter email"/>
                      <Button className="ui red button" style={{
                          margin: '0.25em'
                        }}>
                        <i className="mail outline icon"></i>Send</Button>
                    </Form>
                  </div>
              }
            </div>
          </Grid.Column>
        </Grid.Row>
      </Grid>

      <div style={{
          textAlign: 'center',
          padding: '20px'
        }}>
        <div>
          <h4>Readings</h4>
          <Line data={chartData} options={chartOptions} height={350}/></div>
        <div style={{
            textAlign: 'right',
            padding: '20px'
          }}></div>
      </div>
    </div>)
  }

}

export default Views;
