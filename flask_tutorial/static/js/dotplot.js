<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
        <title>Dot chart with D3</title>
        <script src="http://d3js.org/d3.v3.min.js"></script>
        <style type="text/css">

            rect {
                fill: #eee;
            }

            circle {
                fill: teal;
            }

        </style>
    </head>
    <body>
        <script type="text/javascript">

            //Define data
            var dataset = [
                [ 25, 95 ],
                [ 15, 92 ],
                [ 37, 77 ],
                [ 25, 36 ],
                [ 34, 46 ],
                [ 31, 83 ],
                [ 25, 66 ],
                [ 65, 35 ],
                [ 58, 55 ],
                [ 68, 31 ]
            ];

            //Define variables for size of chart
            var width = 500;
            var height = 300;
            var padding = 50;

            //Define scales
            var xScale = d3.scale.linear()
                                 .domain([
                                    d3.min(dataset, function(d) { return d[0]; }),
                                    d3.max(dataset, function(d) { return d[0]; })
                                 ])
                                 .range([padding, width - padding]);

            var yScale = d3.scale.linear()
                                 .domain([
                                    d3.min(dataset, function(d) { return d[1]; }),
                                    d3.max(dataset, function(d) { return d[1]; })
                                 ])
                                 .range([padding, height - padding]);

            //Create a new SVG element
            var svg = d3.select("body").append("svg")
                        .attr("width", width)
                        .attr("height", height);

            //Create a single rect as the background
            svg.append("rect")
               .attr("x", 0)
               .attr("y", 0)
               .attr("width", width)
               .attr("height", height);

            //Create one circle element for each value pair in dataset
            svg.selectAll("circle")
                .data(dataset)
                .enter()
                .append("circle")
                .attr("cx", function(d) {
                    return xScale(d[0]);
                })
                .attr("cy", function(d) {
                    return yScale(d[1]);
                })
                .attr("r", 3);

        </script>
    </body>
</html>