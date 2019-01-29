import React, { Component } from 'react';
import { BrowserRouter, Route , Link } from 'react-router-dom'

import Dashboard from './streams/dashboard';
import History from './streams/history';



class App extends Component {
  render(){
    return (

      <BrowserRouter>
        <div>
          <Route path ="/" exact component = {Dashboard} />
          <Route path ="/history" exact component = {History} />
        </div>
      </BrowserRouter>

    );
  }


}

export default App;
