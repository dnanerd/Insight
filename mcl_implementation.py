#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#http://igraph.wikidot.com/community-detection-in-python


def generate_mcl_matrix(G):
    mcifile = ""
    mclheader = (
        ("\n(mclheader\n"),
        ("mcltype matrix\n"),
        ( "dimensions %sx%s\n)\n" % (G.vcount(), G.vcount()) ),
        ("(mclmatrix\n"),
        ("begin\n")
    )
    for mhline in mclheader:
        mcifile += mhline
    for v in G.vs:
        mcifile += str(v.index) + " "
        for n in G.neighbors(v.index):
            mcifile += str(n) + " "
        mcifile += " $\n"
    mcifile += ")\n"
    return mcifile
 
def create_graph_image(mcl_line, base_name, G):
    from subprocess import Popen
    nodes = mcl_line.split()
    nodes = nodes[1:-1]     
    subG = G.subgraph([int(node) for node in nodes])
    subG.write_dot(base_name+".dot")
    cmd = "dot -T png -o " + base_name + ".png " + base_name + ".dot"
    Popen(cmd, shell=True)
 
def run_mcl_cluster(G):
    from subprocess import Popen, PIPE
    mcistr = generate_mcl_matrix(G)
    print mcistr + "\n"
    cmd = "mcl - -scheme 6 -I 1.6 -o -"
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
    sout,serr = p.communicate(mcistr)
    p.wait()
    print "return code: %i\n" % p.returncode
    if p.returncode==0 and len(sout)>0:
        lines = sout.splitlines()
        idx_begin = lines.index("begin")+1
        idx_end = lines[idx_begin:].index(")")+idx_begin
        num = 0
        for line in lines[idx_begin:idx_end]:
            print line
            create_graph_image(line, "mcl-ex-"+str(num), G)
            num+=1
 
if __name__ == "__main__":
    G = igraph.Graph.Read_GraphML("ow.graphml")
    print "Edges: " + str(G.ecount())
    print "Nodes: " + str(G.vcount())
    G.simplify()
    # create labels from the id's so that GraphViz outputs subgraphs with original labels
    for n in G.vs:
            n['label']=n['id'][1:]
    run_mcl_cluster(G)