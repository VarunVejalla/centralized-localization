import gdb
import os
import re

class RobustStatementTracer(gdb.Command):
    """Trace execution at the statement level for your source code only."""
    
    def __init__(self):
        super(RobustStatementTracer, self).__init__("trace-src-statements", gdb.COMMAND_USER)
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
    
    def get_current_location(self):
        """Safely get current source location or return None if unavailable."""
        try:
            frame = gdb.selected_frame()
            if frame:
                sal = frame.find_sal()
                if sal and sal.symtab:
                    return sal.symtab.filename, sal.line
        except (gdb.error, AttributeError):
            pass
        return None, None
    
    def invoke(self, arg, from_tty):
        """Run the statement tracer."""
        # Disable pagination to avoid interruptions
        gdb.execute("set pagination off")
        
        # Get the program name
        try:
            self.program_name = gdb.current_progspace().filename
            print(f"Tracing program: {self.program_name}")
        except (gdb.error, AttributeError):
            print("Warning: Could not determine program name")
        
        trace_file = "statement_trace.txt"
        dot_file = "control_flow.dot"
        
        print(f"Tracing program execution to {trace_file}")
        print("Only tracing statements in your program source files.")
        print("Press Ctrl+C to stop tracing at any time.")
        
        # Set arguments if provided
        if arg:
            try:
                gdb.execute(f"set args {arg}")
                print(f"Set program arguments: {arg}")
            except gdb.error as e:
                print(f"Warning: Could not set arguments: {e}")
        
        # Make sure the program is loaded and ready
        try:
            # Check if program is already running
            gdb.execute("info frame", to_string=True)
            print("Program is already running, continuing with tracing")
        except gdb.error:
            # Start the program
            try:
                print("Starting program...")
                gdb.execute("start", to_string=True)
            except gdb.error as e:
                print(f"Error starting program: {e}")
                print("Please ensure the program is loaded and run 'start' manually before tracing")
                return
        
        with open(trace_file, "w") as f:
            # Get initial position
            current_file, current_line = self.get_current_location()
            
            if current_file and self.is_program_source(current_file):
                self.last_file = current_file
                self.last_line = current_line
                f.write(f"START -> {self.last_file}:{self.last_line}\n")
                print(f"Starting trace at {self.last_file}:{self.last_line}")
            else:
                print("Warning: Could not determine initial position in source code")
                f.write(f"START -> Unknown\n")
            
            try:
                # Main tracing loop
                while True:
                    # Execute next source line, stepping over function calls
                    try:
                        gdb.execute("next", to_string=True)
                    except gdb.error as e:
                        print(f"Program execution completed or error occurred: {e}")
                        break
                    
                    # Get new position
                    current_file, current_line = self.get_current_location()
                    
                    if not current_file:
                        continue
                        
                    # Only record our source files
                    if self.is_program_source(current_file):
                        # Only record when we move to a new line
                        if current_file != self.last_file or current_line != self.last_line:
                            # Record the edge if we have a previous position
                            if self.last_file and self.last_line:
                                from_node = self.get_node_id(self.last_file, self.last_line)
                                to_node = self.get_node_id(current_file, current_line)
                                self.edges.append((from_node, to_node))
                                
                                # Write to trace file
                                f.write(f"{self.last_file}:{self.last_line} -> {current_file}:{current_line}\n")
                            else:
                                # First time seeing a valid location
                                f.write(f"START -> {current_file}:{current_line}\n")
                            
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
                clean_loc = loc.replace('"', '\\"')
                f.write(f'  node{node_id} [label="{clean_loc}"];\n')
            
            # Write edges
            for from_node, to_node in self.edges:
                f.write(f"  node{from_node} -> node{to_node};\n")
            
            f.write("}\n")

# Register the command
RobustStatementTracer()
print("Robust statement tracer loaded. Run 'trace-src-statements [program args]' to begin tracing.")
print("This will only trace statements in your source files, skipping library functions.")