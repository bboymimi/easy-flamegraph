import React, { Component } from 'react'
import * as d3 from 'd3v5'
import * as d3lasso from 'd3-lasso'
//import { lasso } from 'd3-lasso'
import './Scatterv5.css'



class Scatterv5 extends Component {
  constructor(props){
    super(props)
    this.createScatter = this.createScatter.bind(this)
  }
  componentDidMount() {
    this.createScatter()
  }
  componentDidUpdate() {
    //this.createScatter()
  }
  createScatter() {
    const node = this.node
    //d3.lasso = d3lasso
    //d3.lasso=require('d3-lasso').lasso
    // append the svg object to the body of the page
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
      width = 500 - margin.left - margin.right,
      height = 450 - margin.top - margin.bottom;

    var x = d3.scaleLinear()
      .range([0, width]);

    var y = d3.scaleLinear()
      .range([height, 0]);

    //var color = d3.scale.category10();
    var color = d3.scaleOrdinal(d3.schemeCategory10);

    //var xAxis = d3.svg.axis()
    //    .scale(x)
    //    .orient("bottom");
    var xAxis = d3.axisBottom(x);

    //var yAxis = d3.svg.axis()
    //    .scale(y)
    //    .orient("left");
    //var yAxis = d3.axisLeft(y);
    var yAxis = d3.axisLeft(y);

    //var svg = d3.select("body").append("svg")
    var svg = d3.select(node).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Lasso functions to execute while lassoing
    var lasso_start = function() {
      lasso.items()
        .attr("r",5) // reset size
        //.style("fill",null) // clear all of the fills
        .style("fill","#3C555C") // clear all of the fills
        //.classed({"not_possible":true,"selected":false}); // style as not possible
    };

    var lasso_draw = function() {
      // Style the possible dots
      //lasso.items().filter(function(d) {console.log(d);if(d.possible===true) {console.log(d); return true;}})
      lasso.items().filter(function(d) {return this.__lasso.possible===true})
        //.attr("r",15) // reset size
        .style("fill","#FFFFFF") // clear all of the fills
        //.classed({"not_possible":false,"possible":true});

      // Style the not possible dot
      //lasso.items().filter(function(d) {return d.possible===false})
      lasso.items().filter(function(d) {return this.__lasso.possible===false})
        //.classed({"not_possible":true,"possible":false});
    };

    var lasso_end = function() {
      // Reset the color of all dots
      lasso.items()
         .style("fill", function(d) { return color(d.species); });

      // Style the selected dots
      lasso.items().filter(function(d) {return this.__lasso.selected===true})
        //.classed({"not_possible":false,"possible":false})
        .attr("r",7);

      // Reset the style of the not selected dots
      lasso.items().filter(function(d) {return this.__lasso.selected===false})
        //.classed({"not_possible":false,"possible":false})
        .attr("r",3.5);

    };

    // Create the area where the lasso event can be triggered
    var lasso_area = svg.append("rect")
                          .attr("width",width)
                          .attr("height",height)
                          .style("opacity",0);

    // Define the lasso

    var lasso = d3lasso.lasso()
    //d3.lasso = d3lasso.lasso()
    //var lasso = lasso()
          .closePathDistance(175) // max distance for the lasso loop to be closed
          .closePathSelect(true) // can items be selected by closing the path?
          .hoverSelect(true) // can items by selected by hovering over them?
          .targetArea(lasso_area) // area where the lasso can be started
          .on("start",lasso_start) // lasso start function
          .on("draw",lasso_draw) // lasso draw function
          .on("end",lasso_end); // lasso end function
          //.on("end",function() { alert("lasso pig!"); }); // lasso end function

    // Init the lasso on the svg:g that contains the dots
    svg.call(lasso);

    d3.tsv("./data.tsv").then(function(data) {
      console.log(JSON.stringify(data.length));
      console.log(data.map(function(d) { return d.sepalLength }));
      //for (var i = 0; i < data.length; i++) {
        //console.log(data.sepalLength);
        //console.log(data.sepalWidth);
        //console.log(data.species);
        //data[i].sepalLength = +data[i].sepalLength;
        //data[i].sepalWidth = +data[i].sepalWidth;
      //};

      x.domain(d3.extent(data, function(d) { return d.sepalWidth; })).nice();
      y.domain(d3.extent(data, function(d) { return d.sepalLength; })).nice();

      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)
        .append("text")
          .attr("class", "label")
          .attr("x", width)
          .attr("y", -6)
          .style("text-anchor", "end")
          .text("Sepal Width (cm)");

      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("class", "label")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Sepal Length (cm)")

      svg.selectAll(".dot")
          .data(data.filter(function(d,i){return i<150}))
          .enter()
          .append("circle")
          .attr("id",function(d,i) {return "dot_" + i;}) // added
          .attr("class", "dot")
          .attr("r", 3.5)
          .attr("cx", function(d) { return x(d.sepalWidth); })
          .attr("cy", function(d) { return y(d.sepalLength); })
          .style("fill", function(d) { return color(d.species); });

      lasso.items(d3.selectAll(".dot"));
      console.log(lasso.items());

      var legend = svg.selectAll(".legend")
          .data(color.domain())
        .enter().append("g")
          .attr("class", "legend")
          .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

      legend.append("rect")
          .attr("x", width - 18)
          .attr("width", 18)
          .attr("height", 18)
          .style("fill", color);

      legend.append("text")
          .attr("x", width - 24)
          .attr("y", 9)
          .attr("dy", ".35em")
          .style("text-anchor", "end")
          .text(function(d) { return d; });

    }); // d3.tsv()

  } // createScatter()

  render() {
    return (
      <div id="my_dataviz">
        <svg ref={node => this.node = node}
          width={500} height={450}>
        </svg>
      </div>
    );
  }
}

export default Scatterv5
