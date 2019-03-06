import React, { Component } from 'react';
import Table from '../Table';
import { Input } from 'semantic-ui-react';

export default class History extends Component {
  state = {
    saved: [],
    status: '',
    emailInput: ''
  }

  uploadData = () => {
    fetch('/api/cloud-db/upload')
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ status: 'Data uploaded successfully!' });
    });
  }

  deleteData = (rowId) => {
    fetch(`/api/rpi/data/${rowId}/delete`, {
      method: 'delete',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: rowId })
    }).then(res => res.json())
    .then(json => {
      const history = json.rows.map(row => ({
        id: row.id,
        date: row.date_time,
        antSize: row.ant_size,
        readings: row.readings
      }));
      this.setState({ saved: history });
    });
  }

  updateEmail = (email) => {
    this.setState({ emailInput: email });
  }

  sendCSV = () => {
    fetch(`/api/cloud-db/csv?email=${this.state.emailInput}`)
      .then(res => res.text())
      .then(string => {
        console.log(string);
        this.setState({ emailInput: '' });
      });
  }

  componentDidMount() {
    fetch('/api/rpi/data')
    .then(res => res.json())
    .then(json => {
      const history = json.rows.map(row => ({
        id: row.id,
        date: row.date_time,
        antSize: row.ant_size,
        readings: row.readings
      }));
      this.setState({ saved: history });
    })
    .catch(err => console.log(err));
  }

  render() {
    const { saved, status, emailInput } = this.state;
    return (
      <div style={{ textAlign: 'center', padding: '15px' }}>
        <Input onChange={(event, { value }) => this.updateEmail(value)} placeholder="Enter email" value={emailInput}/>
        <button className="ui green button" style={{ margin: '5px' }} onClick={this.sendCSV}>
          <i className="file excel outline icon"></i>Export CSV
        </button>
        <button className="ui brown button" onClick={this.uploadData}>
          <i className="upload icon"></i>Upload
        </button>
        <h4 style={{ marginTop: '20px' }}>{status}</h4>
        <Table tableData={saved} handleDelete={this.deleteData}/>
      </div>
    );
  }
}
