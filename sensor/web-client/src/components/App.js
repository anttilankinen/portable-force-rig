import React, { Component } from 'react';
import { BrowserRouter, Route } from 'react-router-dom'

import Dashboard from './streams/dashboard.js';
import History from './streams/history.js';
// import Views from './streams/views.js';
import Header from './header.js';

class App extends Component {
  render(){
    return (
      <div className="ui container">
        <BrowserRouter>
          <div>
            <Header/>
            <Route path="/" exact component={Dashboard} />
            <Route path="/history" exact component={History} />
            <Route path="/history/:rowdate"  component={Views}/>
          </div>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;

const Views = ({ match }) => (
  <div>{match.params.rowdate}</div>
)
