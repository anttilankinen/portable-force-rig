import React, { Component } from 'react';
import { Header, Grid, Feed, Card, Button } from 'semantic-ui-react';
import PageContainer from './PageContainer';
import 'semantic-ui-css/semantic.min.css';
import './index.css';

export default class HomePage extends Component {
  render() {
    return (
      <PageContainer>
        <Header as="h1" style={{ fontSize: '40px' }}>
          Welcome to the Portable Force Rig Dashboard!
        </Header>
        <Grid container columns={2} style={{ padding: '30px', }}>
          <Grid.Row>
            <Grid.Column>
              <Card fluid>
                <Card.Content>
                  <Card.Header>New data readings: 42</Card.Header>
                  <Card.Description>
                    Uploaded on 11/4/2018
                  </Card.Description>
                </Card.Content>
                <Card.Content extra>
                  <Button fluid color='blue'>
                    View
                  </Button>
                </Card.Content>
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card fluid>
                <Card.Content>
                  <Card.Header>New video recordings: 6</Card.Header>
                  <Card.Description>
                    Uploaded on 11/4/2018
                  </Card.Description>
                </Card.Content>
                <Card.Content extra>
                  <Button fluid color='teal'>
                    View
                  </Button>
                </Card.Content>
              </Card>
            </Grid.Column>
          </Grid.Row>
        </Grid>

        <Header as="h3">Activity Feed</Header>
        <Feed style={{ paddingBottom: '30px' }}>
          <Feed.Event>
            <Feed.Label>
            </Feed.Label>
            <Feed.Content>
              <Feed.Summary>
                &bull; Uploaded <span>42 new data readings</span> and <span>6 new video recordings.</span>
                <Feed.Date>11/4/2018</Feed.Date>
              </Feed.Summary>
            </Feed.Content>
          </Feed.Event>
          <Feed.Event>
            <Feed.Label>
            </Feed.Label>
            <Feed.Content>
              <Feed.Summary>
                &bull; Uploaded <span>26 new data readings</span> and <span>3 new video recordings.</span>
                <Feed.Date>11/1/2018</Feed.Date>
              </Feed.Summary>
            </Feed.Content>
          </Feed.Event>
          <Feed.Event>
            <Feed.Label>
            </Feed.Label>
            <Feed.Content>
              <Feed.Summary>
                &bull; Uploaded <span>34 new data readings</span> and <span>4 new video recordings.</span>
                <Feed.Date>10/27/2018</Feed.Date>
              </Feed.Summary>
            </Feed.Content>
          </Feed.Event>
        </Feed>

      </PageContainer>
    );
  }
}
