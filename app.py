import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

with st.sidebar:
    st.header("📂 Upload Data")
    uploaded_file = st.file_uploader("Upload your .csv file", type=['csv'])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    columns = data.columns.tolist()
    
    with st.sidebar:
        st.divider()
        st.header("⚙️ Settings")
        
        main_title = st.text_input("📝 Main Title", value="New Figure")
        show_legend = st.checkbox("Show Legend?", value=False)
        num_graphs = st.number_input("Number of plots", min_value=1, max_value=10, value=1, step=1)
        share_x = st.checkbox("Shared X-Axis?", value=True)
            
        v_spacing = st.slider("↕️ Vertical Spacing", min_value=0.0, max_value=0.5, value=0.1, step=0.01)
        
        st.markdown("### 🎨 Color Settings")
        c_bg1, c_bg2, c_bg3 = st.columns(3)
        with c_bg1:
            fg_color = st.color_picker("Foreground", "#fafafa")
        with c_bg2:
            bg_color = st.color_picker("Background", "#0e1117")
        with c_bg3:
            grid_color = st.color_picker("Grid", "#ffffff")
            hex_c = grid_color.lstrip('#')
            rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
        
        grid_alpha = st.slider("Grid Alpha", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
        grid_rgba = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {grid_alpha})"
        
        st.divider()
        st.markdown("### 🎚️ Figure Settings")
        graph_settings = []
        
        for i in range(num_graphs):
            with st.expander(f"Figure {i+1}", expanded=(i==0)): 
                graph_title = st.text_input("📝 Title", value="", key=f"title_input_{i}")
                
                x_col = st.selectbox(f"X-axis", columns, index=0, key=f"x_col_{i}")
                y_cols = st.multiselect(
                    f"Y-axis", 
                    columns, 
                    default=[columns[min(i+1, len(columns)-1)]], 
                    key=f"y_cols_{i}"
                )
                
                st.markdown("🎨 **Figure Colors**")
                
                default_colors = ['#00B4D8', '#FF6B6B', '#4ECDC4', '#FFE66D', '#845EC2', '#FF9671']
                
                line_colors_dict = {}
                
                if len(y_cols) > 0:
                    color_cols = st.columns(min(len(y_cols), 3))
                    for j, y_col in enumerate(y_cols):
                        with color_cols[j % 3]:
                            def_color = default_colors[j % len(default_colors)]
                            
                            picked_color = st.color_picker(f"{y_col}", def_color, key=f"color_{i}_{y_col}")
                            line_colors_dict[y_col] = picked_color
                
                c1, c2 = st.columns(2)
                with c1:
                    is_x_log = st.checkbox("Log X", key=f"x_log_{i}")
                with c2:
                    is_y_log = st.checkbox("Log Y", key=f"y_log_{i}")
                
                x_scale = "log" if is_x_log else "linear"
                y_scale = "log" if is_y_log else "linear"
                
                graph_settings.append({
                    "title": graph_title,
                    "x_col": x_col, "y_cols": y_cols, 
                    "x_scale": x_scale, "y_scale": y_scale,
                    "line_colors": line_colors_dict
                })
    
    titles_list = [setting["title"] for setting in graph_settings]

    fig = make_subplots(
        rows=num_graphs, cols=1,
        shared_xaxes=share_x,
        vertical_spacing=v_spacing,
        subplot_titles=titles_list
    )

    for i, setting in enumerate(graph_settings):
        row_num = i + 1
        
        for y_col in setting["y_cols"]:
            specific_color = setting["line_colors"][y_col]
            
            fig.add_trace(
                go.Scatter(
                    x=data[setting["x_col"]], 
                    y=data[y_col], 
                    name=f"{y_col}",
                    line=dict(color=specific_color)
                ),
                row=row_num, col=1
            )
        
        y_axis_title = setting["y_cols"][0] if len(setting["y_cols"]) == 1 else ""
        fig.update_yaxes(
            title_text=y_axis_title,
            type=setting["y_scale"],
            row=row_num, col=1,
            zeroline=False,
            gridcolor=grid_rgba
        )
        
        if share_x and row_num < num_graphs:
            fig.update_xaxes(
                type=setting["x_scale"],
                row=row_num, col=1,
                zeroline=False,
                gridcolor=grid_rgba
            )
        else:
            fig.update_xaxes(
                title_text=setting["x_col"],
                type=setting["x_scale"],
                row=row_num, col=1,
                zeroline=False,
                gridcolor=grid_rgba
            )

    fig.update_layout(
        title_text=main_title,
        title_x=0.5,
        title_xanchor='center',
        height=max(400, 300 * num_graphs),
        showlegend=show_legend,
        hovermode="x unified",plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=fg_color)
    )
    
    st.plotly_chart(fig, width='stretch', theme=None)
    
    with st.expander("🔎 Raw Data"):
        st.dataframe(data, width='stretch')

else:
    st.info("👈 Please upload your CSV on the left hand sidebar to start the plot.")