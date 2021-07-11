"""Functions for visualizations
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
from shapely.geometry import Polygon, Point
from descartes.patch import PolygonPatch
from shapely.geometry import MultiLineString

BLUE = "#6699cc"
GRAY = "#999999"
DARKGRAY = "#333333"
YELLOW = "#ffcc33"
GREEN = "#339933"
RED = "#ff3333"
BLACK = "#000000"


def set_limits(ax, x0, xN, y0, yN):
    ax.set_xlim(x0, xN)
    # ax.set_xticks(range(x0, xN+1))
    ax.set_ylim(y0, yN)
    # ax.set_yticks(range(y0, yN+1))
    ax.set_aspect("equal")


def plot_lines(ax, ob, color=GRAY, zorder=1, linewidth=3, alpha=1):
    for line in ob:
        x, y = line.xy
        ax.plot(
            x,
            y,
            color=color,
            linewidth=linewidth,
            solid_capstyle="round",
            zorder=zorder,
            alpha=alpha,
        )


def plot_coords(ax, ob, color=GRAY, zorder=1, alpha=1):
    for line in ob:
        x, y = line.xy
        ax.plot(x, y, "o", color=color, zorder=zorder, alpha=alpha)


def plot_bounds(ax, ob, zorder=1, alpha=1):
    x, y = zip(*list((p.x, p.y) for p in ob.boundary))
    ax.plot(x, y, "o", color=BLACK, zorder=zorder, alpha=alpha)


def draw_problem(i):
    plt.close("all")
    data = read_problem(problems[i])
    hole = Polygon(data["hole"])
    xx = [x for (x, y) in data["hole"]]
    yy = [y for (x, y) in data["hole"]]
    SIZE = (3 * 3, 3)
    fig, axes = plt.subplots(ncols=3, nrows=1, figsize=SIZE, dpi=90)
    ax = axes[0]
    patch = PolygonPatch(hole, facecolor=RED, edgecolor=RED, alpha=0.5, zorder=2)
    ax.add_patch(patch)

    set_limits(ax, np.min(xx) - 1, np.max(xx) + 3, np.max(yy) + 3, np.min(yy) - 1)
    # ax.invert_yaxis()
    # figure
    ax = axes[1]
    figure = data["figure"]
    vertices = figure["vertices"]
    edges = figure["edges"]
    figure_shape = MultiLineString([(vertices[s], vertices[e]) for s, e in edges])
    plot_coords(ax, figure_shape)
    # plot_bounds(ax, figure_shape)
    plot_lines(ax, figure_shape)
    xx = [x for (x, y) in vertices]
    yy = [y for (x, y) in vertices]
    set_limits(ax, np.min(xx) - 1, np.max(xx) + 3, np.max(yy) + 3, np.min(yy) - 1)
    # both
    ax = axes[2]
    patch = PolygonPatch(hole, facecolor=RED, edgecolor=RED, alpha=0.5, zorder=2)

    ax.add_patch(patch)
    plot_coords(ax, figure_shape)
    # plot_bounds(ax, figure_shape)
    plot_lines(ax, figure_shape)
    xx = [x for (x, y) in vertices] + [x for (x, y) in data["hole"]]
    yy = [y for (x, y) in vertices] + [y for (x, y) in data["hole"]]

    set_limits(ax, np.min(xx) - 1, np.max(xx) + 3, np.max(yy) + 3, np.min(yy) - 1)
    plt.show()


def draw_pair(figure, filename=None, label="", new_vert=[], distance=-1):
    hole_poly = Polygon(figure.hole)
    # figure = data['figure']
    # vertices = figure['vertices']
    # edges = figure['edges']
    # epsilon=data['epsilon']
    figure_shape = MultiLineString(
        [(new_vert[s], new_vert[e]) for s, e in figure.edges]
    )

    fig = plt.figure(figsize=(3, 3))
    ax = plt.gca()
    patch = PolygonPatch(hole_poly, facecolor=RED, edgecolor=RED, alpha=0.5, zorder=2)
    ax.add_patch(patch)
    plot_coords(ax, figure_shape)
    # plot_bounds(ax, figure_shape)
    plot_lines(ax, figure_shape)
    if len(new_vert) == 0:
        [x.coords[:] for x in figure_shape.geoms]
        new_vert = sorted(set([c for x in figure_shape.geoms for c in x.coords[:]]))
    # print(repr(new_vert), flush=True)
    # dist = get_distance(hole_poly, figure_shape)
    # dist = get_distance(data, new_vert)
    plt.title(f"Current distance: {distance} - {label}")
    # hole_poly.bounds
    x0, y0, x1, y1 = hole_poly.union(figure_shape).bounds

    set_limits(ax, x0 - 1, x1 + 3, y1 + 3, y0 - 1)

    if filename is not None:
        fig.savefig(filename)
    plt.show()
