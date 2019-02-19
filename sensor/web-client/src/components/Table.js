import React, {Component} from 'react';
import {Link} from 'react-router-dom';

const TableHeader = props => {
  return (<thead>
    <tr>
      <th className="one wide">#</th>
      <th className="two wide">Date, Time</th>
      <th className="two wide">Ant Size</th>
      <th className="two wide">Max. Bite Force</th>
      <th className="five wide"></th>
      {/* <th className="three wide"></th> */}
    </tr>
  </thead>);
}

const TableBody = props => {

  const rows = props.tableData.map((row, index) => {

    return (<tr key={index}>
      <td>{index + 1}</td>
      <td>{row.date}</td>
      <td>{row.antSize}</td>
      <td>{Math.max(...JSON.parse(row.readings))}</td>
      <td>

        <div key={index + 1}>
          <Link to={{
              pathname: `/history/${row.id}`
            }} className="ui violet button" style={{
              margin: '0.25em'
            }}>
            <i className="info circle icon"></i>View
          </Link>

          <button id={row.id} onClick={() => props.delete(row.id)} className="ui red button">
            <i className="trash alternate outline icon"></i>Delete
          </button>
        </div>
      </td>
    </tr>);
  });
  return <tbody>{rows}</tbody>;
}

class Table extends Component {
  render() {
    const {tableData} = this.props;

    return (<table className="unstackable ui striped table" style={{
        marginTop: '40px',
        textAlign: 'center'
      }}>
      <TableHeader/>
      <TableBody delete={this.props.deleteprop} tableData={tableData}/>
    </table>);
  }
}

export default Table;
