import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Create figure
fig = go.Figure()

# Define positions for blocks (vertical chain for better space utilization)
block_positions = {
    'Genesis': (2, 3),
    'Block 1': (2, 2),
    'Block 2': (2, 1), 
    'Block 3': (2, 0)
}

# Define colors for institutions
colors = {
    'system': '#2E8B57',  # Sea green for genesis
    'MIT': '#1FB8CD',     # Strong cyan
    'Stanford': '#D2BA4C', # Moderate yellow
    'Harvard': '#DB4545'   # Bright red
}

# Block data with timestamps and detailed info
blocks_data = {
    'Genesis': {
        'index': 0, 'hash': '00000a1b2c3d4e5f', 'prev_hash': '0',
        'validator': 'system', 'timestamp': '2024-01-01 00:00:00',
        'data': 'Genesis Block'
    },
    'Block 1': {
        'index': 1, 'hash': '1a2b3c4d5e6f7890', 'prev_hash': '00000a1b2c3d4e5f',
        'validator': 'MIT', 'timestamp': '2024-01-02 10:30:00',
        'student': 'Alice Johnson', 'degree': 'BS Computer Sci', 'type': 'issue'
    },
    'Block 2': {
        'index': 2, 'hash': '2b3c4d5e6f789012', 'prev_hash': '1a2b3c4d5e6f7890',
        'validator': 'Stanford', 'timestamp': '2024-01-03 14:15:00',
        'student': 'Bob Smith', 'degree': 'MBA', 'type': 'issue'
    },
    'Block 3': {
        'index': 3, 'hash': '3c4d5e6f78901234', 'prev_hash': '2b3c4d5e6f789012',
        'validator': 'Harvard', 'timestamp': '2024-01-04 09:45:00',
        'cert_hash': '1a2b3c4d...', 'reason': 'Academic misconduct', 'type': 'revoke'
    }
}

# Add detailed blocks as annotations
for block_name, (x, y) in block_positions.items():
    block = blocks_data[block_name]
    validator = block['validator']
    
    # Create detailed block text
    if block_name == 'Genesis':
        block_text = f"<b>📦 {block_name}</b><br>" + \
                    f"<b>Header:</b><br>" + \
                    f"Index: {block['index']}<br>" + \
                    f"Timestamp: {block['timestamp']}<br>" + \
                    f"Prev Hash: {block['prev_hash']}<br>" + \
                    f"Hash: {block['hash']}<br>" + \
                    f"Validator: {block['validator']}<br>" + \
                    f"<b>Data:</b> {block['data']}"
    elif block_name == 'Block 3':
        block_text = f"<b>📦 {block_name}</b><br>" + \
                    f"<b>Header:</b><br>" + \
                    f"Index: {block['index']}<br>" + \
                    f"Timestamp: {block['timestamp']}<br>" + \
                    f"Prev Hash: {block['prev_hash'][:12]}...<br>" + \
                    f"Hash: {block['hash']}<br>" + \
                    f"Validator: {block['validator']}<br>" + \
                    f"<b>Certificate:</b><br>" + \
                    f"Hash: {block['cert_hash']}<br>" + \
                    f"Reason: {block['reason']}<br>" + \
                    f"Type: ❌ {block['type']}"
    else:
        block_text = f"<b>📦 {block_name}</b><br>" + \
                    f"<b>Header:</b><br>" + \
                    f"Index: {block['index']}<br>" + \
                    f"Timestamp: {block['timestamp']}<br>" + \
                    f"Prev Hash: {block['prev_hash'][:12]}...<br>" + \
                    f"Hash: {block['hash']}<br>" + \
                    f"Validator: {block['validator']}<br>" + \
                    f"<b>Certificate:</b><br>" + \
                    f"Student: {block['student']}<br>" + \
                    f"Degree: {block['degree']}<br>" + \
                    f"Type: ✅ {block['type']}"
    
    # Add block as a rectangle annotation
    fig.add_shape(
        type="rect",
        x0=x-0.8, y0=y-0.35, x1=x+0.8, y1=y+0.35,
        fillcolor=colors[validator],
        line=dict(color="white", width=3),
        opacity=0.9
    )
    
    # Add block text
    fig.add_annotation(
        x=x, y=y,
        text=block_text,
        showarrow=False,
        font=dict(size=9, color="white"),
        align="left",
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)"
    )

# Add hash chain connections with detailed arrows
connections = [
    ('Genesis', 'Block 1'),
    ('Block 1', 'Block 2'), 
    ('Block 2', 'Block 3')
]

for start, end in connections:
    x_start, y_start = block_positions[start]
    x_end, y_end = block_positions[end]
    
    # Add hash chain arrow
    fig.add_annotation(
        x=x_end, y=y_end + 0.35,
        ax=x_start, ay=y_start - 0.35,
        xref="x", yref="y",
        axref="x", ayref="y",
        arrowhead=2,
        arrowsize=2,
        arrowwidth=4,
        arrowcolor="#5D878F",
        text="🔗",
        font=dict(size=14),
        showarrow=True
    )

# Add PoA explanation
fig.add_annotation(
    x=4.5, y=3,
    text="<b>🏛️ Proof-of-Authority (PoA) Consensus</b><br>" + \
         "Only authorized universities can validate:<br>" + \
         "• MIT validates Block 1<br>" + \
         "• Stanford validates Block 2<br>" + \
         "• Harvard validates Block 3<br>" + \
         "Each validator cryptographically signs their block",
    showarrow=False,
    font=dict(size=10, color="#333"),
    align="left",
    bgcolor="rgba(248,248,248,0.9)",
    bordercolor="#ccc",
    borderwidth=2,
    width=280
)

# Add legend
legend_items = [
    ("🏛️ PoA Validators:", "white", 12),
    ("🔵 MIT", colors['MIT'], 10),
    ("🟡 Stanford", colors['Stanford'], 10), 
    ("🔴 Harvard", colors['Harvard'], 10),
    ("", "white", 8),  # spacer
    ("📋 Certificate Types:", "white", 12),
    ("✅ Issue Certificate", "#2E8B57", 10),
    ("❌ Revoke Certificate", "#DB4545", 10),
    ("", "white", 8),  # spacer
    ("🔗 Hash Chain Links", "#5D878F", 10)
]

legend_text = ""
for item, color, size in legend_items:
    if item:
        legend_text += f"<span style='font-size:{size}px'>{item}</span><br>"

fig.add_annotation(
    x=4.5, y=1.5,
    text=legend_text,
    showarrow=False,
    font=dict(size=10, color="#333"),
    align="left",
    bgcolor="rgba(249,249,249,0.9)",
    bordercolor="#ddd",
    borderwidth=2,
    width=250
)

# Update layout
fig.update_layout(
    title='Academic Cert Verification Blockchain',
    xaxis=dict(range=[0, 6], showgrid=False, showticklabels=False, zeroline=False),
    yaxis=dict(range=[-0.8, 3.8], showgrid=False, showticklabels=False, zeroline=False),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial", size=12)
)

# Save the chart as both PNG and SVG
fig.write_image('blockchain_diagram.png')
fig.write_image('blockchain_diagram.svg', format='svg')

print("Enhanced blockchain diagram created successfully!")
fig.show()