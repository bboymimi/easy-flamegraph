import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Link
} from 'react-router-dom';


class Projects extends Component {
  constructor(props){
    super(props)
    //this.createScatter = this.createScatter.bind(this)
  }
  componentDidMount() {
    //this.createScatter()
  }
  componentDidUpdate() {
    //this.createScatter()
  }

        //<Paper className={fixedHeightPaper}>
  render() {
    return (
      <div>
        <h1>Projects</h1>
        <strong>Welcome!</strong>
      </div>
    );
  }
}

export default Projects;

