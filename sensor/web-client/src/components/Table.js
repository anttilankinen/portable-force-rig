import React, { Component } from 'react';

const TableHeader = props => {
  return (
    <thead>
      <tr>
        <th className="two wide">#</th>
        <th className="two wide">Date</th>
        <th className="two wide">Ant Size</th>
        <th className="ten wide">Force Readings</th>
      </tr>
    </thead>
  );
}

const TableBody = props => {
  const rows = props.tableData.map((row, index) => {
    return (
      <tr key={index}>
        <td>{index + 1}</td>
        <td>{row.date}</td>
        <td>{row.antSize}</td>
        <td>{row.readings}</td>
      </tr>
    );
  });
  return <tbody>{rows}</tbody>;
}

class Table extends Component {
  render () {
    const { tableData } = this.props;

    return (
      <table className="ui striped table" style={{ marginTop: '40px', textAlign: 'center' }}>
        <TableHeader />
        <TableBody tableData={tableData}/>
      </table>
    );
  }
}

export default Table;
