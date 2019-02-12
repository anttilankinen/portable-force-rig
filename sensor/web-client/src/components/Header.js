import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <div className="ui secondary pointing menu" style={{ textAlign: 'center', padding: '30px' }}>
      <Link to="/"><h1>Portable Force Rig Dashboard</h1></Link>
      <div className="right menu">
        <Link to="/" className="ui inverted secondary button">
          <i className="home icon"></i>Home
        </Link>
        <Link to="/history" className="ui inverted secondary button">
          <i className="list alternate outline icon"></i>History
        </Link>
        <Link to="/calibrate" className="ui inverted secondary button">
          <i className="sync icon"></i>Calibrate
        </Link>
      </div>
    </div>
  )
};

export default Header;
