import React, {Component} from 'react';

import Table from '../Table';

class History extends Component {
  state = {
    saved: []
  }

  componentDidMount() {
    fetch('/api/rpi/data').then(res => res.json()).then(json => {
      const history = json.rows.map(row => ({id: row.id, date: row.date_time, antSize: row.ant_size, readings: row.readings}))
      this.setState({saved: history});
    });
  }
  deleteData = (id) => {
    const rowId = id;
    fetch(`/api/rpi/data/${rowId}/delete`, {
      method: 'delete',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({id: 'rowId'})
    }).then(res => res.json()).then(json => {
      const history = json.rows.map(row => ({id: row.id, date: row.date_time, antSize: row.ant_size, readings: row.readings}))
      this.setState({saved: history});
    });
  }

  render() {
    const {saved} = this.state;
    console.log(saved);
    return (<div style={{
        textAlign: 'center',
        padding: '30px'
      }}>
      <Table tableData={saved} deleteprop={this.deleteData}/>

    </div>);
  }
}

export default History;
