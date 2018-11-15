import React, { Component } from 'react';
import { Container } from 'semantic-ui-react';
import 'semantic-ui-css/semantic.min.css';
import './index.css';

export default class PageContainer extends Component {
  render() {
    return (
      <Container align="center" style={{ paddingTop: '50px', height: '100vh-40px' }}>
        {this.props.children}
      </Container>
    );
  }
}
