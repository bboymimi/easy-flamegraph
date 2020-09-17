import React, { Component } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import clsx from 'clsx';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Chart from '../Chart';
import BarChart from '../BarChart';
import Scatter from '../Scatter';
import Scatterv5 from '../Scatterv5';
import { FlameGraph } from '../../components'

//const Memory = () => (
class Memory extends Component {
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
          <Scatter />
          <Scatterv5 />
	  <FlameGraph type={"perf"} filename={"numad-perf.script"} />
        <Paper>
          <BarChart data={[5,10,1,3]} size={[500,500]} />
        </Paper>
      </div>
    );
  }
}

export default Memory;
