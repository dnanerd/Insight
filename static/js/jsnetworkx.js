var G3 = jsnx.Graph();

G3.add_nodes_from([1,2,3,4], {group:0});
G3.add_nodes_from([5,6,7], {group:1});
G3.add_nodes_from([8,9,10,11], {group:2});

G3.add_path([1,2,5,6,7,8,11]);
G3.add_edges_from([[1,3],[1,4],[3,4],[2,3],[2,4],[8,9],[8,10],[9,10],[11,10],[11,9]]);

var color = d3.scale.category20();
jsnx.draw(G3, {
    element: '#chart3',
    layout_attr: {
        charge: -120,
        linkDistance: 20
    },
    node_attr: {
        r: 5,
        title: function(d) { return d.label;}
    },
    node_style: {
        fill: function(d) { 
            return color(d.data.group); 
        },
        stroke: 'none'
    },
    edge_style: {
        stroke: '#999'
    }
}, true);