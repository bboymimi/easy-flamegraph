import React, { Component } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import clsx from 'clsx';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Chart from '../Chart';
import BarChart from '../BarChart';
import Scatter from '../Scatter';
import Scatterv5 from '../Scatterv5';
import Line from '../Line';
import { FlameGraph } from '../../components'

//const Memory = () => (
class Memory extends Component {
  constructor(props){
    super(props)
    //this.createScatter = this.createScatter.bind(this)

    this.changeState = this.changeState.bind(this)
    this.changeState2 = this.changeState2.bind(this)
    this.state = {
      pname: '',
      value: 'test/numad-perf.script',
      value2: 'examples/perf.data.kvm.svg'
    };
  }
  componentDidMount() {
    //this.createScatter()
    const { projectname } = this.props.match.params;
    console.log(projectname);
    this.setState({pname: projectname});
    console.log("this.state." + this.state.pname);
  }
  componentDidUpdate() {
    //this.createScatter()
  }

  changeState() {
    const set_value = this.state.value === 'test/perf.stacks01' ?
      'test/numad-perf.script' : 'test/perf.stacks01';
    this.setState({ value: set_value });
  }

  changeState2() {
    const set_value = this.state.value2 === 'examples/perf.data.kvm.svg' ?
      'examples/pagesteal.svg' : 'examples/perf.data.kvm.svg';
    this.setState({ value2: set_value });
  }

        //<Paper className={fixedHeightPaper}>
  render() {
    return (
      <div>
          <Line changeState={this.changeState}/>
	  <div>
	    <div onClick={this.changeState}>{this.state.value}</div>
	  <FlameGraph type={"perf"} filename={this.state.value} />
	  </div>
          <Scatter />
          <Scatterv5 />
        <Paper>
          <BarChart data={[5,10,1,3]} size={[500,500]} />
        </Paper>
      </div>
    );
  }
}

export default Memory;
