import gdb
import os
import sys

class StatementTracer(gdb.Command):
    """Trace execution at the statement level and log the control flow."""
    
    def __init__(self):
        super(StatementTracer, self).__init__("trace-statements", gdb.COMMAND_USER)
        self.last_file = None
        self.last_line = None
        self.trace_count = 0
        self.nodes = {}  # Store nodes as file:line -> node_id
        self.edges = []  # Store edges as (from_node, to_node)
        self.node_count = 0
        
    def get_node_id(self, file, line):
        """Get or create a node ID for a file:line location."""
        key = f"{file}:{line}"
        if key not in self.nodes:
            self.node_count += 1
            self.nodes[key] = self.node_count
        return self.nodes[key]
    
    def invoke(self, arg, from_tty):
        # Disable pagination to avoid interruptions
        gdb.execute("set pagination off")
        
        # Start program if not already running
        try:
            gdb.execute("start " + arg)
        except gdb.error:
            print("Program already running, continuing with tracing")
        
        trace_file = "statement_trace.txt"
        dot_file = "control_flow.dot"
        
        print(f"Tracing program execution to {trace_file}")
        print("This may take a while for programs with many statements or iterations.")
        print("Press Ctrl+C to stop tracing at any time.")
        
        with open(trace_file, "w") as f:
            try:
                # Initial frame
                frame = gdb.selected_frame()
                sal = frame.find_sal()
                
                if sal.symtab:
                    self.last_file = sal.symtab.filename
                    self.last_line = sal.line
                    f.write(f"START -> {self.last_file}:{self.last_line}\n")
                
                # Main tracing loop
                while True:
                    # Execute one machine instruction
                    gdb.execute("stepi", to_string=True)
                    
                    frame = gdb.selected_frame()
                    sal = frame.find_sal()
                    
                    # Only record source lines, not assembly
                    if sal.symtab is not None and sal.line > 0:
                        current_file = sal.symtab.filename
                        current_line = sal.line
                        
                        # Only record when we move to a new line
                        if current_file != self.last_file or current_line != self.last_line:
                            # Record the edge
                            from_node = self.get_node_id(self.last_file, self.last_line)
                            to_node = self.get_node_id(current_file, current_line)
                            self.edges.append((from_node, to_node))
                            
                            # Write to trace file
                            f.write(f"{self.last_file}:{self.last_line} -> {current_file}:{current_line}\n")
                            
                            # Update current position
                            self.last_file = current_file
                            self.last_line = current_line
                            self.trace_count += 1
                            
                            # Occasional progress update
                            if self.trace_count % 100 == 0:
                                print(f"Traced {self.trace_count} statement transitions...")
                    
            except KeyboardInterrupt:
                print("Tracing stopped by user.")
            except gdb.error as e:
                print(f"Program execution completed or error occurred: {e}")
            
            print(f"Traced {self.trace_count} statement transitions.")
            
        # Generate DOT file for visualization
        self.generate_dot_file(dot_file)
        print(f"Control flow graph saved to {dot_file}")
        print("You can visualize this file using Graphviz:")
        print(f"  dot -Tpng {dot_file} -o control_flow.png")
    
    def generate_dot_file(self, filename):
        """Generate a DOT file for Graphviz visualization."""
        with open(filename, "w") as f:
            f.write("digraph ControlFlow {\n")
            f.write("  node [shape=box, style=filled, fillcolor=lightblue];\n")
            
            # Write nodes
            for loc, node_id in self.nodes.items():
                f.write(f'  node{node_id} [label="{loc}"];\n')
            
            # Write edges
            for from_node, to_node in self.edges:
                f.write(f"  node{from_node} -> node{to_node};\n")
            
            f.write("}\n")

StatementTracer()
print("Statement tracer loaded. Run 'trace-statements [program args]' to begin tracing.")