# Since mermaid is having network connectivity issues, let's create the flowchart using plotly
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Define the flowchart nodes and their properties
nodes = {
    'A': {'text': 'Start: User wants\nto verify cert', 'x': 0, 'y': 14, 'type': 'start', 'color': '#A5D6A7'},
    'B': {'text': 'Enter cert hash', 'x': 0, 'y': 12, 'type': 'process', 'color': '#B3E5EC'},
    'C': {'text': 'Hash format\nvalid?', 'x': 0, 'y': 10, 'type': 'decision', 'color': '#FFEB8A'},
    'D': {'text': 'Show error\nmessage', 'x': -3, 'y': 8, 'type': 'error', 'color': '#FFCDD2'},
    'E': {'text': 'Search blockchain\ndatabase', 'x': 0, 'y': 8, 'type': 'process', 'color': '#B3E5EC'},
    'F': {'text': 'Cert found in\nblockchain?', 'x': 0, 'y': 6, 'type': 'decision', 'color': '#FFEB8A'},
    'G': {'text': 'Cert not found\n/invalid', 'x': -3, 'y': 4, 'type': 'error', 'color': '#FFCDD2'},
    'H': {'text': 'Check cert status', 'x': 0, 'y': 4, 'type': 'process', 'color': '#B3E5EC'},
    'I': {'text': 'Cert revoked?', 'x': 0, 'y': 2, 'type': 'decision', 'color': '#FFEB8A'},
    'J': {'text': 'Show revoked\nstatus & reason', 'x': 3, 'y': 0, 'type': 'error', 'color': '#FFCDD2'},
    'K': {'text': 'Verify digital\nsignature', 'x': 0, 'y': 0, 'type': 'process', 'color': '#B3E5EC'},
    'L': {'text': 'Signature valid?', 'x': 0, 'y': -2, 'type': 'decision', 'color': '#FFEB8A'},
    'M': {'text': 'Cert tampered\n/invalid', 'x': -3, 'y': -4, 'type': 'error', 'color': '#FFCDD2'},
    'N': {'text': 'Cert verified\nsuccessfully', 'x': 0, 'y': -4, 'type': 'process', 'color': '#B3E5EC'},
    'O': {'text': 'End: Display\ncert details', 'x': 0, 'y': -6, 'type': 'end', 'color': '#A5D6A7'}
}

# Define the connections (edges)
edges = [
    ('A', 'B'), ('B', 'C'), ('C', 'D'), ('C', 'E'), ('E', 'F'), 
    ('F', 'G'), ('F', 'H'), ('H', 'I'), ('I', 'J'), ('I', 'K'), 
    ('K', 'L'), ('L', 'M'), ('L', 'N'), ('N', 'O')
]

# Create the figure
fig = go.Figure()

# Add edges (connections) first so they appear behind nodes
for start, end in edges:
    start_node = nodes[start]
    end_node = nodes[end]
    
    fig.add_trace(go.Scatter(
        x=[start_node['x'], end_node['x']],
        y=[start_node['y'], end_node['y']],
        mode='lines',
        line=dict(color='#333333', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add arrowheads
    dx = end_node['x'] - start_node['x']
    dy = end_node['y'] - start_node['y']
    if dx != 0 or dy != 0:
        length = np.sqrt(dx**2 + dy**2)
        dx_norm = dx / length
        dy_norm = dy / length
        
        # Arrow position (slightly before the end node)
        arrow_x = end_node['x'] - 0.3 * dx_norm
        arrow_y = end_node['y'] - 0.3 * dy_norm
        
        fig.add_annotation(
            x=arrow_x, y=arrow_y,
            ax=start_node['x'], ay=start_node['y'],
            xref='x', yref='y',
            axref='x', ayref='y',
            arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#333333',
            showarrow=True,
            text=""
        )

# Add decision labels
decision_labels = {
    'C': [('No', -1.5, 9), ('Yes', 0, 9)],
    'F': [('No', -1.5, 5), ('Yes', 0, 5)],
    'I': [('Yes', 1.5, 1), ('No', 0, 1)],
    'L': [('No', -1.5, -3), ('Yes', 0, -3)]
}

for node_id, labels in decision_labels.items():
    for label, x_offset, y_pos in labels:
        fig.add_annotation(
            x=x_offset, y=y_pos,
            text=label,
            showarrow=False,
            font=dict(size=10, color='#333333'),
            bgcolor='white',
            bordercolor='#333333',
            borderwidth=1
        )

# Add nodes
for node_id, node in nodes.items():
    # Determine shape based on type
    if node['type'] in ['decision']:
        # Diamond shape for decisions (using scatter with diamond symbol)
        fig.add_trace(go.Scatter(
            x=[node['x']],
            y=[node['y']],
            mode='markers+text',
            marker=dict(
                symbol='diamond',
                size=80,
                color=node['color'],
                line=dict(color='#333333', width=2)
            ),
            text=node['text'],
            textposition='middle center',
            textfont=dict(size=9, color='#333333'),
            showlegend=False,
            hoverinfo='skip'
        ))
    else:
        # Rectangle shape for other nodes
        fig.add_trace(go.Scatter(
            x=[node['x']],
            y=[node['y']],
            mode='markers+text',
            marker=dict(
                symbol='square',
                size=100,
                color=node['color'],
                line=dict(color='#333333', width=2)
            ),
            text=node['text'],
            textposition='middle center',
            textfont=dict(size=9, color='#333333'),
            showlegend=False,
            hoverinfo='skip'
        ))

# Update layout
fig.update_layout(
    title='Certificate Verification Workflow',
    showlegend=False,
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-4, 4]
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-7, 15]
    ),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Save the figure
fig.write_image('certificate_workflow.png')
fig.write_image('certificate_workflow.svg', format='svg')

print("Certificate verification flowchart created successfully!")
print("Saved as: certificate_workflow.png and certificate_workflow.svg")