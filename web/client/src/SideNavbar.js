import React, { Component } from 'react';
import { Icon, Menu, Sidebar } from 'semantic-ui-react';

export default class SidebarExampleSidebar extends Component {
  render() {
    return (
      <Sidebar
        as={Menu}
        animation='overlay'
        icon='labeled'
        inverted
        vertical
        visible
        style={{ paddingTop: '40px' }}>
        <Menu.Item as='a'>
          <Icon name='home' />
          Home
        </Menu.Item>
        <Menu.Item as='a'>
          <Icon name='database' />
          Data
        </Menu.Item>
        <Menu.Item as='a'>
          <Icon name='line graph' />
          Analyze
        </Menu.Item>
        <Menu.Item as='a'>
          <Icon name='video camera' />
          Recordings
        </Menu.Item>
        <Menu.Item as='a'>
          <Icon name='setting' />
          Settings
        </Menu.Item>
      </Sidebar>
    )
  }
}
