import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <div  className = "ui secondary pointing menu">
      <Link to ="/"><h1>Portable Force Rig Dashboard</h1></Link>
    </div>

  )

};

export default Header;
