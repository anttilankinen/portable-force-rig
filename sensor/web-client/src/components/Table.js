import React, { Component } from 'react';
import { Link } from 'react-router-dom';

const TableHeader = props => {
  return (
    <thead>
      <tr>
        <th className="one wide">#</th>
        <th className="four wide">Date</th>
        <th className="three wide">Ant Size</th>
        <th className="three wide">Max. Bite Force</th>
        <th className="five wide"></th>
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
        <td>{Math.max(...JSON.parse(row.readings))}</td>
        <td>
          <Link to={{ pathname:`/history/${row.id}` }} className="ui violet button" style={{ margin: '10px 0'}}>
            <i className="info circle icon"></i>View
          </Link>
          <button onClick={() => props.handleDelete(row.id)} className="ui red button">
            <i className="trash alternate outline icon"></i>Delete
          </button>
        </td>
      </tr>
    );
  });
  return <tbody>{rows}</tbody>;
}

class Table extends Component {
  render () {
    const { tableData, handleDelete } = this.props;

    return (
      <table className="ui striped table" style={{ marginTop: '40px', textAlign: 'center' }}>
        <TableHeader />
        <TableBody tableData={tableData} handleDelete={handleDelete}/>
      </table>
    );
  }
}

export default Table;
