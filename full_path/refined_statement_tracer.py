import gdb
import os
import re

class RefinedStatementTracer(gdb.Command):
    """Trace execution at the statement level for your source code only."""
    
    def __init__(self):
        super(RefinedStatementTracer, self).__init__("trace-src-statements", gdb.COMMAND_USER)
        self.last_file = None
        self.last_line = None
        self.trace_count = 0
        self.nodes = {}  # Store nodes as file:line -> node_id
        self.edges = []  # Store edges as (from_node, to_node)
        self.node_count = 0
        self.program_name = None
        self.skip_count = 0
        
    def get_node_id(self, file, line):
        """Get or create a node ID for a file:line location."""
        key = f"{file}:{line}"
        if key not in self.nodes:
            self.node_count += 1
            self.nodes[key] = self.node_count
        return self.nodes[key]
    
    def is_program_source(self, filename):
        """Check if this file is part of our program source."""
        if not filename:
            return False
        
        # Only trace files that match our program name or are in current directory
        program_basename = os.path.basename(self.program_name) if self.program_name else None
        file_basename = os.path.basename(filename)
        
        # If file matches our program name (without extension)
        if program_basename and file_basename.startswith(program_basename.split('.')[0]):
            return True
            
        # Or if it's a .c/.h file in the current directory or a subdirectory
        if (file_basename.endswith('.c') or file_basename.endswith('.h')) and not '/usr/' in filename:
            return True
            
        return False
    
    def invoke(self, arg, from_tty):
        # Disable pagination to avoid interruptions
        gdb.execute("set pagination off")
        
        # Start program if not already running
        try:
            # Get program name from GDB
            self.program_name = gdb.current_progspace().filename
            
            # Start the program with arguments
            gdb.execute("set args " + arg)
            gdb.execute("start")
        except gdb.error as e:
            print(f"Error starting program: {e}")
            print("Program already running, continuing with tracing")
        
        trace_file = "statement_trace.txt"
        dot_file = "control_flow.dot"
        
        print(f"Tracing program execution to {trace_file}")
        print("Only tracing statements in your program source files.")
        print("Press Ctrl+C to stop tracing at any time.")
        
        # Set a breakpoint at main to get started
        try:
            gdb.execute("break main")
            gdb.execute("continue")
        except gdb.error:
            pass  # Already at main or main not found
        
        with open(trace_file, "w") as f:
            # Initial position
            frame = gdb.selected_frame()
            sal = frame.find_sal()
            
            if sal.symtab and self.is_program_source(sal.symtab.filename):
                self.last_file = sal.symtab.filename
                self.last_line = sal.line
                f.write(f"START -> {self.last_file}:{self.last_line}\n")
            
            try:
                # Use "next" command to step over function calls
                while True:
                    # Execute next source line, stepping over function calls
                    gdb.execute("next", to_string=True)
                    
                    frame = gdb.selected_frame()
                    sal = frame.find_sal()
                    
                    if not sal.symtab:
                        continue
                        
                    current_file = sal.symtab.filename
                    current_line = sal.line
                    
                    # Only record our source files
                    if self.is_program_source(current_file):
                        # Only record when we move to a new line
                        if current_file != self.last_file or current_line != self.last_line:
                            # Record the edge
                            if self.last_file and self.last_line:
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
                            if self.trace_count % 10 == 0:
                                print(f"Traced {self.trace_count} statements...")
                    else:
                        self.skip_count += 1
                        if self.skip_count % 100 == 0:
                            print(f"Skipped {self.skip_count} statements from library/system code...")
                    
            except KeyboardInterrupt:
                print("Tracing stopped by user.")
            except gdb.error as e:
                print(f"Program execution completed or error occurred: {e}")
            
            print(f"Traced {self.trace_count} statements from your source code.")
            print(f"Skipped {self.skip_count} statements from library/system code.")
            
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

# Register the command
RefinedStatementTracer()
print("Refined statement tracer loaded. Run 'trace-src-statements [program args]' to begin tracing.")
print("This will only trace statements in your source files, skipping library functions.")