import React, { Component } from 'react';
import { Menu, Icon } from 'semantic-ui-react';

export default class MenuExampleSecondaryPointing extends Component {
  handleItemClick = () => {};

  render() {
    return (
      <div>
        <Menu inverted borderless fixed="top">
          <Menu.Menu position='right'>
            <Menu.Item>
              Signed in as: Jace Tan
            </Menu.Item>
            <Menu.Item as='a'>
              <Icon name='power off' style={{ paddingTop: '1.5px' }}/>
              Logout
            </Menu.Item>
          </Menu.Menu>
        </Menu>
      </div>
    )
  }
}
