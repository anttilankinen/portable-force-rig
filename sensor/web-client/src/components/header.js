import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <div className = "ui secondary pointing menu" style={{ textAlign: 'center', padding: '50px' }}>
      <Link to ="/"><h1>Portable Force Rig Dashboard</h1></Link>
      <div className = "right menu">
      <Link to="/history" className="ui black button"
      {/* onClick={this.showHistory} */}
      >
        <i className="list alternate outline icon"></i>History
      </Link>
      </div>
    </div>

  )

};

export default Header;
