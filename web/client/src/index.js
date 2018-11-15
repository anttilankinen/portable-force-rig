import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import SideNavbar from './SideNavbar';
import TopNavbar from './TopNavbar';
import HomePage from './HomePage';
import 'semantic-ui-css/semantic.min.css';
import './index.css';

class App extends Component {
  render() {
    return (
      <div>
        <SideNavbar />
        <TopNavbar />
        <HomePage />
      </div>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));
