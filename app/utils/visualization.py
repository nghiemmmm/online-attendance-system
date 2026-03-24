import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA

def visualize_embeddings(all_embeddings, label_map, query_embedding=None, matches=None):
    """
    Visualize embeddings in 3D space using PCA with highlighted points and similarity lines.
    
    Args:
        all_embeddings (np.ndarray): All face embeddings
        label_map (np.ndarray): Labels for embeddings
        query_embedding (np.ndarray): Query embedding to highlight
        matches (list): List of matches (name, similarity, idx)
    """
    if all_embeddings is None or len(all_embeddings) < 3:
        return
    
    # Prepare data for visualization
    embeddings_to_plot = all_embeddings.copy()
    labels = label_map.copy()
    colors = ['blue'] * len(all_embeddings)
    sizes = [8] * len(all_embeddings)
    hover_names = []
    for i, name in enumerate(labels):
        if query_embedding is not None and i < len(all_embeddings):
            # Calculate similarity from this point to query
            dist = np.linalg.norm(all_embeddings[i] - query_embedding)
            hover_names.append(f"Employee: {name} (Dist: {dist:.4f})")
        else:
            hover_names.append(f"Employee: {name}")
    
    # Add query embedding if available
    query_idx = None
    if query_embedding is not None:
        query_idx = len(embeddings_to_plot)
        embeddings_to_plot = np.vstack([embeddings_to_plot, query_embedding])
        labels = np.append(labels, "Query Face")
        colors.append('red')
        sizes.append(12)
        hover_names.append("Your Face (Query)")
    
    # Highlight matches if available
    if matches:
        for i, (name, similarity, idx) in enumerate(matches):
            if idx < len(colors):
                colors[idx] = 'green' if i == 0 else 'orange'
                sizes[idx] = 12
                hover_names[idx] = f"Match {i+1}: {name} (Similarity: {similarity:.4f})"
    
    # Reduce dimensionality with PCA (3D)
    pca = PCA(n_components=3, random_state=42)
    embeddings_3d = pca.fit_transform(embeddings_to_plot)
    
    # Create DataFrame for Plotly
    df = pd.DataFrame({
        'x': embeddings_3d[:, 0],
        'y': embeddings_3d[:, 1],
        'z': embeddings_3d[:, 2],
        'label': labels,
        'color': colors,
        'size': sizes,
        'hover_name': hover_names
    })
    
    # Create 3D interactive plot
    fig = px.scatter_3d(
        df, 
        x='x', y='y', z='z',
        color='color', size='size', hover_name='hover_name',
        title='Face Embeddings in 3D Space',
        color_discrete_map={
            'blue': 'rgba(30, 136, 229, 0.7)',
            'red': 'rgba(229, 57, 53, 1)',
            'green': 'rgba(67, 160, 71, 1)',
            'orange': 'rgba(255, 152, 0, 1)'
        }
    )
    
    # Add similarity lines
    if query_embedding is not None and matches:
        for i, (name, similarity, idx) in enumerate(matches[:5]):
            if idx < len(embeddings_3d):
                fig.add_trace(go.Scatter3d(
                    x=[embeddings_3d[query_idx, 0], embeddings_3d[idx, 0]],
                    y=[embeddings_3d[query_idx, 1], embeddings_3d[idx, 1]],
                    z=[embeddings_3d[query_idx, 2], embeddings_3d[idx, 2]],
                    mode='lines',
                    line=dict(color='purple' if i == 0 else 'gray', width=3 if i == 0 else 1),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f"Similarity: {similarity:.4f}"
                ))
    
    fig.update_layout(
        scene=dict(xaxis_title='Dimension 1', yaxis_title='Dimension 2', zaxis_title='Dimension 3'),
        showlegend=False, hovermode='closest', margin=dict(l=0, r=0, b=0, t=30)
    )
    
    # Add annotations
    if matches:
        for i, (name, similarity, idx) in enumerate(matches[:5]):
            if idx < len(embeddings_3d):
                fig.add_annotation(
                    x=embeddings_3d[idx, 0], y=embeddings_3d[idx, 1],
                    text=f"Match {i+1}" if i > 0 else "Best Match",
                    showarrow=True, arrowhead=1, font=dict(size=12, color="black")
                )
    
    import streamlit as st
    st.plotly_chart(fig, use_container_width=True)
    
    # Add similarity table
    if matches:
        st.subheader("Match Distances")
        match_data = [{"Rank": i+1, "Name": name, "Similarity": f"{similarity:.4f}"} for i, (name, similarity, _) in enumerate(matches)]
        df_matches = pd.DataFrame(match_data)
        st.dataframe(df_matches.style.highlight_max(subset=["Similarity"], color='lightgreen'), use_container_width=True)