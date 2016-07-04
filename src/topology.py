"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."
        
        # Initialize topology
        Topo.__init__( self )
        
        # Add hosts and switches
        cliente = self.addHost( 'h1' )
        serv1 = self.addHost( 'h2' )
        serv2 = self.addHost( 'h3' )
        serv3 = self.addHost( 'h4' )
        serv4 = self.addHost( 'h5' )
        serv5 = self.addHost( 'h6' )

        switch1 = self.addSwitch( 's1' )
        switch2 = self.addSwitch( 's2' )
        switch3 = self.addSwitch( 's3' )
        switch4 = self.addSwitch( 's4' )
        switch5 = self.addSwitch( 's5' )
        
        # Add links
        self.addLink(switch1, switch2)
        self.addLink(switch2, switch3)
        self.addLink(switch3, switch4)
        self.addLink(switch4, switch5)
	
        self.addLink(cliente, switch1)
        self.addLink(switch1, serv1)

        self.addLink(switch2, serv2)

        self.addLink(switch3, serv3)

        self.addLink(switch4, serv4)

        self.addLink(switch5, serv5)




topos = { 'mytopo': ( lambda: MyTopo() ) }
