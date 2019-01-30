import React, { Component } from 'react';
import { Link } from 'react-router-dom';

const TableHeader = props => {
  return (
    <thead>
      <tr>
        <th className="one wide">#</th>
        <th className="two wide">Date</th>
        <th className="two wide">Ant Size</th>
        <th className="six wide">Force Readings</th>
        <th className="two wide">Max. Bite Force</th>
        <th className="three wide"></th>
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
        <td>{typeof(row.readings)}</td>
        <td>
          <Link to={`/history/${row.date}`} className="ui violet button">
            <i Link="info circle icon"></i>View
          </Link>
        </td>
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
