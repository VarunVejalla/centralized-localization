#!/usr/bin/env python3
"""
Script to visualize the statement trace from GDB and generate a cleaner control flow graph.
This handles simplifying the trace by removing repetitions and creating a more readable graph.
"""

import sys
import re
import os

def parse_trace_file(trace_file):
    """Parse the statement trace file to extract execution flow."""
    transitions = []
    
    with open(trace_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '->' in line:
                parts = line.split('->')
                source = parts[0].strip()
                target = parts[1].strip()
                transitions.append((source, target))
    
    return transitions

def simplify_transitions(transitions):
    """Simplify transitions by removing consecutive duplicates."""
    if not transitions:
        return []
        
    simplified = [transitions[0]]
    for i in range(1, len(transitions)):
        if transitions[i] != transitions[i-1]:
            simplified.append(transitions[i])
    
    return simplified

def extract_file_info(location):
    """Extract filename and line number from location string."""
    if ':' in location:
        parts = location.split(':')
        filename = parts[0].split('/')[-1]  # Get just the filename, not the full path
        line = parts[1]
        return filename, line
    return location, "?"

def generate_dot_file(transitions, output_file):
    """Generate a DOT file for visualization with Graphviz."""
    nodes = {}
    edges = []
    node_count = 0
    
    # Create DOT file
    with open(output_file, 'w') as f:
        f.write("digraph ControlFlow {\n")
        f.write("  node [shape=box, style=filled, fillcolor=lightblue];\n")
        f.write("  edge [color=darkblue];\n")
        f.write("  rankdir=LR;\n")  # Left to right layout
        
        # Process each transition to build nodes and edges
        for source, target in transitions:
            # Handle source node
            if source == "START":
                if "START" not in nodes:
                    nodes["START"] = "start"
                    f.write('  start [label="START", shape=oval, fillcolor=green];\n')
                source_id = "start"
            else:
                source_file, source_line = extract_file_info(source)
                source_key = f"{source_file}:{source_line}"
                if source_key not in nodes:
                    node_count += 1
                    node_id = f"node{node_count}"
                    nodes[source_key] = node_id
                    f.write(f'  {node_id} [label="{source_file}\\nLine {source_line}"];\n')
                source_id = nodes[source_key]
            
            # Handle target node
            target_file, target_line = extract_file_info(target)
            target_key = f"{target_file}:{target_line}"
            if target_key not in nodes:
                node_count += 1
                node_id = f"node{node_count}"
                nodes[target_key] = node_id
                f.write(f'  {node_id} [label="{target_file}\\nLine {target_line}"];\n')
            target_id = nodes[target_key]
            
            # Add edge if it's not already there
            edge = (source_id, target_id)
            if edge not in edges:
                edges.append(edge)
                f.write(f"  {source_id} -> {target_id};\n")
        
        f.write("}\n")
    
    return len(nodes), len(edges)

def create_annotated_source(trace_file, source_file):
    """Create an annotated version of the source file showing execution order."""
    if not os.path.exists(source_file):
        print(f"Warning: Source file {source_file} not found.")
        return
    
    # Extract execution order by line
    executions = {}
    with open(trace_file, 'r') as f:
        order = 1
        for line in f:
            line = line.strip()
            if '->' in line:
                target = line.split('->')[1].strip()
                if ':' in target:
                    file_path, line_num = target.split(':')
                    filename = file_path.split('/')[-1]
                    if filename == os.path.basename(source_file):
                        try:
                            line_num = int(line_num)
                            if line_num not in executions:
                                executions[line_num] = []
                            executions[line_num].append(order)
                            order += 1
                        except ValueError:
                            continue
    
    # Read source file
    with open(source_file, 'r') as f:
        source_lines = f.readlines()
    
    # Create annotated file
    annotated_file = f"{source_file}.annotated.txt"
    with open(annotated_file, 'w') as f:
        f.write(f"ANNOTATED SOURCE: {source_file}\n")
        f.write("Line numbers show execution order\n")
        f.write("-" * 60 + "\n\n")
        
        for i, line in enumerate(source_lines, 1):
            if i in executions:
                exec_order = ", ".join(map(str, executions[i]))
                f.write(f"{i:4d} [{exec_order:10s}] {line}")
            else:
                f.write(f"{i:4d} [          ] {line}")
    
    print(f"Annotated source created: {annotated_file}")
    return annotated_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python trace_visualizer.py <trace_file> [source_file]")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    source_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Parsing trace file: {trace_file}")
    transitions = parse_trace_file(trace_file)
    print(f"Found {len(transitions)} transitions")
    
    simplified = simplify_transitions(transitions)
    print(f"Simplified to {len(simplified)} unique transitions")
    
    dot_file = "simplified_control_flow.dot"
    nodes, edges = generate_dot_file(simplified, dot_file)
    print(f"Generated DOT file with {nodes} nodes and {edges} edges: {dot_file}")
    print("To visualize, run:")
    print(f"  dot -Tpng {dot_file} -o control_flow.png")
    
    # Create annotated source if source file is provided
    if source_file and os.path.exists(source_file):
        create_annotated_source(trace_file, source_file)

if __name__ == "__main__":
    main()