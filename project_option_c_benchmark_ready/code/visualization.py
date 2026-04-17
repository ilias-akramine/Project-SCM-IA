from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import folium

COLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']


def plot_routes(depot, customers, routes, title, out_path, highlight_id=None):
    cust = {c.id: c for c in customers}
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.scatter([depot['x']], [depot['y']], marker='s', s=120, label='Depot')
    for idx, route in enumerate(routes):
        xs = [depot['x']]
        ys = [depot['y']]
        for cid in route:
            xs.append(cust[cid].x)
            ys.append(cust[cid].y)
        xs.append(depot['x'])
        ys.append(depot['y'])
        ax.plot(xs, ys, marker='o', linewidth=2, color=COLORS[idx % len(COLORS)], label=f'Vehicle {idx+1}')
    for c in customers:
        ax.text(c.x + 0.8, c.y + 0.8, str(c.id), fontsize=8)
        if highlight_id == c.id:
            ax.scatter([c.x], [c.y], s=180, marker='*')
    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(alpha=0.25)
    ax.legend(loc='best', fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def comparison_table_png(df, out_path):
    fig, ax = plt.subplots(figsize=(9.5, 2.8))
    ax.axis('off')
    show = df.copy()
    show['distance'] = show['distance'].map(lambda x: f'{x:.1f}')
    show['time_window_respect_pct'] = show['time_window_respect_pct'].map(lambda x: f'{x:.1f}%')
    show['co2_kg'] = show['co2_kg'].map(lambda x: f'{x:.1f}')
    cols = ['scenario', 'method', 'distance', 'vehicles_used', 'time_window_respect_pct', 'co2_kg']
    tbl = ax.table(cellText=show[cols].values, colLabels=['Instance','Method','Distance','Vehicles','TW respect','CO2 (kg)'], loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.4)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_text_props(weight='bold')
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close(fig)


def dashboard(df, out_path):
    pivot = df.pivot(index='scenario', columns='method', values='distance')
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
    df.pivot(index='scenario', columns='method', values='distance').plot(kind='bar', ax=axes[0], title='Distance')
    df.pivot(index='scenario', columns='method', values='vehicles_used').plot(kind='bar', ax=axes[1], title='Vehicles')
    df.pivot(index='scenario', columns='method', values='time_window_respect_pct').plot(kind='bar', ax=axes[2], title='Time window respect %')
    for ax in axes:
        ax.grid(axis='y', alpha=0.25)
        ax.tick_params(axis='x', rotation=0)
        ax.set_xlabel('')
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def dynamic_impact(before_metrics, after_metrics, out_path):
    df = pd.DataFrame([
        {'phase': 'Before', 'distance': before_metrics['distance'], 'vehicles': before_metrics['vehicles_used'], 'tw': before_metrics['time_window_respect_pct']},
        {'phase': 'After', 'distance': after_metrics['distance'], 'vehicles': after_metrics['vehicles_used'], 'tw': after_metrics['time_window_respect_pct']},
    ])
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.3))
    df.plot(x='phase', y='distance', kind='bar', legend=False, ax=axes[0], title='Distance')
    df.plot(x='phase', y='vehicles', kind='bar', legend=False, ax=axes[1], title='Vehicles')
    df.plot(x='phase', y='tw', kind='bar', legend=False, ax=axes[2], title='TW respect %')
    for ax in axes:
        ax.grid(axis='y', alpha=0.25)
        ax.set_xlabel('')
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def create_map(depot, customers, routes, out_path, highlight_id=None):
    center = [depot['y'], depot['x']]
    m = folium.Map(location=center, zoom_start=11)
    folium.Marker(center, popup='Depot', icon=folium.Icon(color='black')).add_to(m)
    cust = {c.id: c for c in customers}
    for c in customers:
        color = 'red' if c.id == highlight_id else 'blue'
        folium.CircleMarker([c.y, c.x], radius=5, popup=f'C{c.id} [{c.ready},{c.due}]', color=color, fill=True).add_to(m)
    for idx, route in enumerate(routes):
        pts = [(depot['y'], depot['x'])] + [(cust[c].y, cust[c].x) for c in route] + [(depot['y'], depot['x'])]
        folium.PolyLine(pts, color=['blue','green','orange','purple'][idx % 4], weight=4, opacity=0.8).add_to(m)
    m.save(str(out_path))
