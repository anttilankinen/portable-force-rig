import React, { Component } from 'react';
import { BrowserRouter, Route } from 'react-router-dom'

import Dashboard from './streams/dashboard';
import History from './streams/history';
import Header from './header.js';


class App extends Component {
  render(){
    return (
      <div className = "ui container">
        <BrowserRouter>
          <div>
            <Header/>
            <Route path ="/" exact component = {Dashboard} />
            <Route path ="/history" exact component = {History} />
          </div>
        </BrowserRouter>
      </div>
    );
  }


}

export default App;
