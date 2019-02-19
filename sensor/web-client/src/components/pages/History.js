import React, { Component } from 'react';
import Table from '../Table';

export default class History extends Component {
  state = {
    saved: [],
    status: '',
  }

  uploadData = () => {
    fetch('/api/data-upload/')
    .then(res => res.text())
    .then(string => {
      console.log(string);
      this.setState({ saved: [], status: 'Data uploaded successfully!' });
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
      this.setState({saved: history});
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
    });
  }

  render() {
    const { saved, status } = this.state;
    return (
      <div style={{ textAlign: 'center', padding: '30px' }}>
        <button className="ui brown button" onClick={this.uploadData}>
          <i className="upload icon"></i>Upload
        </button>
        <h4 style={{ marginTop: '20px' }}>{status}</h4>
        <Table tableData={saved} handleDelete={this.deleteData}/>
      </div>
    );
  }
}
