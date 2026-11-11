import cudf
import datashader as ds
import datashader.transfer_functions as tf
import colorcet as cc
import pandas as pd
import numpy as np
import anndata
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re

__all__ = ["GPUUMAPPlotter", "plot_umap"]

class GPUUMAPPlotter:
    """
    A GPU-accelerated plotter API for AnnData embeddings.
    Generates high-performance static plots using cuDF and Datashader.
    
    This is an experimental utility designed for the Rapids Single Cell (RSC) ecosystem.
    """
    def __init__(self, adata, coords_keys='X_umap', color_keys=None):
        """
        Initialize and preload data to GPU.
        
        Parameters:
        - adata: AnnData object
        - coords_keys: Single string or list of strings for obsm keys (e.g., ['X_umap', 'X_tsne'])
        - color_keys: Single string or list of strings from obs to be available for plotting.
        """
        # Normalize coords_keys to a list
        if isinstance(coords_keys, str):
            self.coords_keys = [coords_keys]
        else:
            self.coords_keys = coords_keys

        # Normalize color_keys to a list
        if color_keys is None:
            self.color_keys = ['leiden'] if 'leiden' in adata.obs else [adata.obs.columns[0]]
        elif isinstance(color_keys, str):
            self.color_keys = [color_keys]
        else:
            self.color_keys = color_keys
            
        print(f"Loading data to GPU (Coords: {self.coords_keys}, Attributes: {self.color_keys})...")
        
        # Initialize GPU DataFrame
        self.gdf = cudf.DataFrame()
        
        # 1. Extract Coordinates (Multiple Bases)
        valid_bases = []
        for basis in self.coords_keys:
            if basis not in adata.obsm.keys():
                print(f"Warning: Key '{basis}' not found in adata.obsm. Skipping.")
                continue
            
            valid_bases.append(basis)
            coords = adata.obsm[basis].astype('float32')
            
            # Store with basis-specific column names
            self.gdf[f'x_{basis}'] = coords[:, 0]
            self.gdf[f'y_{basis}'] = coords[:, 1]
            
        if not valid_bases:
            raise ValueError(f"No valid coordinate keys found in {self.coords_keys}")
        self.coords_keys = valid_bases
            
        # 2. Add Color Columns (Handling Categoricals)
        for key in self.color_keys:
            if key not in adata.obs:
                print(f"Warning: Key '{key}' not found in adata.obs. Skipping.")
                continue
            
            # Convert to string numpy array FIRST to ensure consistency
            vals = adata.obs[key].values.astype(str)
            self.gdf[key] = vals
            self.gdf[key] = self.gdf[key].astype('category')

    def _get_color_map(self, key):
        """Generates a consistent color map for a given categorical key."""
        unique_cats = self.gdf[key].unique().to_pandas().tolist()
        
        # Natural sort logic: splits "Cluster 10" into ["Cluster ", 10]
        # allowing 2 to come before 10.
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split('([0-9]+)', str(s))]
        
        unique_cats.sort(key=natural_sort_key)
        
        # Use glasbey for distinct categorical colors
        palette = cc.glasbey * (len(unique_cats) // len(cc.glasbey) + 1)
        return {cat: color for cat, color in zip(unique_cats, palette)}

    def plot(self, color_key=None, coords_key=None, width=1200, height=1200, background='black', show=True, save_path=None):
        """
        Generates and displays/saves a static plot.
        
        Parameters:
        - color_key: The obs column to color by. Defaults to first key.
        - coords_key: The embedding to use. Defaults to first key.
        - width/height: Image resolution.
        - background: 'black' or 'white'.
        - show: Whether to display the plot in the notebook.
        - save_path: If provided (e.g., 'plot.png'), saves the figure to disk.
        """
        key = color_key if color_key else self.color_keys[0]
        basis = coords_key if coords_key else self.coords_keys[0]
        
        x_col = f'x_{basis}'
        y_col = f'y_{basis}'
        
        if x_col not in self.gdf.columns:
             raise ValueError(f"Basis '{basis}' not loaded on GPU.")

        # 1. Aggregation (GPU)
        cvs = ds.Canvas(plot_width=width, plot_height=height)
        agg = cvs.points(self.gdf, x_col, y_col, ds.count_cat(key))
        
        # 2. Shading (CPU/GPU)
        color_map = self._get_color_map(key)
        img = tf.shade(agg, color_key=color_map, min_alpha=100)
        img = tf.dynspread(img, threshold=0.5, max_px=4)
        img = tf.set_background(img, background)
        
        # 3. Matplotlib Figure Construction
        fig, ax = plt.subplots(figsize=(12, 12), constrained_layout=True)
        ax.imshow(img.to_pil())
        ax.axis('off')
        
        # Legend
        n_cats = len(color_map)
        ncols = max(1, n_cats // 25 + 1)
        legend_handles = [mpatches.Patch(color=c, label=str(k)) for k, c in color_map.items()]
        
        # Adjust legend text color based on background
        text_color = 'white' if background == 'black' else 'black'
        
        legend = ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), 
                          title=key, frameon=False, fontsize='10', ncol=ncols)
        plt.setp(legend.get_title(), color=text_color)
        for text in legend.get_texts():
            text.set_color(text_color)
        
        if save_path:
            # Save with transparent background outside the image, but respect plot background
            fig.savefig(save_path, facecolor=background, bbox_inches='tight')
            print(f"Saved to {save_path}")

        # Always close the figure to prevent automatic display by pyplot logic
        plt.close(fig)

        if show:
            return fig
        return None

# --- Convenience Wrapper ---
def plot_umap(adata, coords_key='X_umap', color_key='leiden', width=1200, height=1200, background='black', save_path=None):
    """One-shot wrapper for the GPU plotter."""
    plotter = GPUUMAPPlotter(adata, coords_keys=coords_key, color_keys=[color_key])
    return plotter.plot(color_key, coords_key, width, height, background, save_path=save_path)