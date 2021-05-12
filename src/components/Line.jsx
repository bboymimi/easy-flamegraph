import React, { Component } from 'react'
import * as d3 from 'd3'

class Line extends Component {
   constructor(props){
      super(props)
      this.createLine = this.createLine.bind(this)
   }
   componentDidMount() {
      this.createLine()
   }
   componentDidUpdate() {
   }

   createLine() {
      const node = this.node
	// append the svg object to the body of the page
  var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 600 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

   var svg = d3.select(node)
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

    //Read the data
    d3.csv("./examples/test/memory/memfree.csv").then(

        function(data){
                data.forEach(d => { d.date = d3.timeParse("%Y-%m-%d-%H:%M:%S")(d.date) });
		data = Object.assign(data, {y: "$ Close"});
                return data;

      }).then(

      (data) => {

      // Add X axis --> it is a date format
      var x = d3.scaleTime()
        .domain(d3.extent(data, function(d) { return d.date; }))
        .range([ 0, width ]);

      var xAxis = svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear()
      .domain([0, d3.max(data, function(d) { return +d.value + 150; })])
      .range([ height, 0 ]);

    var yAxis = svg.append("g")
      .call(d3.axisLeft(y))
      .call(g => g.select(".domain").remove())
      .call(g => g.select(".tick:last-of-type text").clone()
        .attr("x", 3)
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .text(data.y))

    // Add a clipPath: everything out of this area won't be drawn.
    var clip = svg.append("defs").append("svg:clipPath")
        .attr("id", "clip")
        .append("svg:rect")
        .attr("width", width )
        .attr("height", height )
        .attr("x", 0)
        .attr("y", 0);

    // Add brushing
    var brush = d3.brushX()                   // Add the brush feature using the d3.brush function
        .extent( [ [0,0], [width,height] ] )  // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
        .on("end", updateChart)               // Each time the brush selection changes, trigger the 'updateChart' function

    // Create the line variable: where both the line and the brush take place
    var line = svg.append('g')
      .attr("clip-path", "url(#clip)")

    // Add the line
    line.append("path")
      .datum(data)
      .attr("class", "line")  // I add the class line to be able to modify this line later on.
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
        .x(function(d) { return x(d.date) })
        .y(function(d) { return y(d.value) })
        )

    line.append("path")
      .datum(data)
      .attr("class", "line1")  // I add the class line to be able to modify this line later on.
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
        .x(function(d) { return x(d.date) })
        .y(function(d) { return y(d.value) + -50 })
        )
    // Add the brushing
    line
      .append("g")
        .attr("class", "brush")
        .call(brush);

    const tooltip = svg.append("g");


    svg.on("click", (event) => {
      const { changeState } = this.props;
      const {date, value} = bisect(d3.pointer(event)[0]);

      console.log(`${formatValue(value)} ${formatDate(date)}`);
      console.log(`${value} ${date}`);
      console.log(date.getFullYear());
      console.log(date.getMonth());
      console.log(date.getDate());
      console.log(date.getHours());
      console.log(date.getMinutes());
      console.log(date.getSeconds());
      const year = date.getFullYear();
      const month = ("0" + (date.getMonth() + 1)).slice(-2);
      const day = ("0" + date.getDate()).slice(-2);
      const hour = ("0" + date.getHours()).slice(-2);
      const minute = ("0" + date.getMinutes()).slice(-2);
      const subsys = "cpu";
      const flamename = subsys + "/" + year + "-" + month + "-" + day + "-" +
		    hour + ":" + minute + "." + subsys + ".script"; 
      //console.log(flamename);
      changeState(flamename);

    });

    svg.on("touchmove mousemove", function(event) {
      const {date, value} = bisect(d3.pointer(event, this)[0]);

      tooltip
        .attr("transform", `translate(${x(date)},${y(value)})`)
        .call(callout, `${formatValue(value)} ${formatDate(date)}`);
    });

    svg.on("touchend mouseleave", () => tooltip.call(callout, null));

    function bisect(mx) {
      const bisect_r = d3.bisector(d => d.date).left;
      const date = x.invert(mx);
      console.log(date + " " + mx);
      const index = bisect_r(data, date, 1);
      const a = data[index - 1];
      const b = data[index];
      return b && (date - a.date > b.date - date) ? b : a;
    };

    function callout(g, value) {
      if (!value) return g.style("display", "none");

      g
        .style("display", null)
        .style("pointer-events", "none")
        .style("font", "10px sans-serif");

      const path = g.selectAll("path")
        .data([null])
        .join("path")
          .attr("fill", "white")
          .attr("stroke", "black");

      const text = g.selectAll("text")
        .data([null])
        .join("text")
        .call(text => text
          .selectAll("tspan")
          .data((value + "").split(/\n/))
          .join("tspan")
            .attr("x", 0)
            .attr("y", (d, i) => `${i * 1.1}em`)
            .style("font-weight", (_, i) => i ? null : "bold")
            .text(d => d));

      const {x, y, width: w, height: h} = text.node().getBBox();

      text.attr("transform", `translate(${-w / 2},${15 - y})`);
      path.attr("d", `M${-w / 2 - 10},5H-5l5,-5l5,5H${w / 2 + 10}v${h + 20}h-${w + 20}z`);
    }

    function formatValue(value) {
      return value.toLocaleString("en", {
        style: "currency",
        currency: "USD"
      });
    }

    function formatDate(date) {
      return date.toLocaleString("en", {
        month: "short",
        day: "numeric",
        year: "numeric",
	hour: "numeric",
	minute: "numeric",
	second: "numeric",
        timeZone: "UTC"
      });
    }

    // A function that set idleTimeOut to null
    var idleTimeout
    function idled() { idleTimeout = null; }

    // A function that update the chart for given boundaries
    function updateChart() {

      // What are the selected boundaries?
      var extent = d3.brushSelection(this);

      // If no selection, back to initial coordinate. Otherwise, update X axis domain
      if(!extent){
        if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); // This allows to wait a little bit
        x.domain([ 4,8])
      }else{
        x.domain([ x.invert(extent[0]), x.invert(extent[1]) ])
        line.select(".brush").call(brush.move, null) // This remove the grey brush area as soon as the selection has been done
      }

      // Update axis and line position
      xAxis.transition().duration(1000).call(d3.axisBottom(x))
      line
          .select('.line')
          .transition()
          .duration(1000)
          .attr("d", d3.line()
            .x(function(d) { return x(d.date) })
            .y(function(d) { return y(d.value) })
          )
      line
          .select('.line1')
          .transition()
          .duration(1000)
          .attr("d", d3.line()
            .x(function(d) { return x(d.date) })
            .y(function(d) { return y(d.value) - 50 })
          )
    }

    // If user right click, reinitialize the chart
    svg.on("contextmenu",function(){
      x.domain(d3.extent(data, function(d) { return d.date; }))
      xAxis.transition().call(d3.axisBottom(x))
      line
        .select('.line')
        .transition()
        .attr("d", d3.line()
          .x(function(d) { return x(d.date) })
          .y(function(d) { return y(d.value) })
      )
      line
        .select('.line1')
        .transition()
        .attr("d", d3.line()
          .x(function(d) { return x(d.date) })
          .y(function(d) { return y(d.value) - 50})
      )
      // prevent the webserver right-click menu
      event.preventDefault();

    });

      })
  }

  render() {
    return (
      <div id="my_dataviz">
        <svg ref={node => this.node = node}
          width={600} height={300}>
        </svg>
      </div>
    );
  }
}

export default Line
