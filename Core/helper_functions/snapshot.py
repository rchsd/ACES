import numpy as np
import pyvista as pv
import trimesh
from pathlib import Path
from typing import Optional, Sequence, Dict
import sys


# -------------------------
# Helpers: vector utilities
# -------------------------

def unitize(v: np.ndarray) -> np.ndarray:
    """
    Return a unit-length version of v (safe for zero-length).
    Accepts shape (3,) and returns shape (3,).
    """
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def coerce_direction(norms: np.ndarray, method: str = "sum") -> np.ndarray:
    """
    Convert a normals array (3,) or (N,3) of *non-unitized* normals into a single unit direction.

    - For (N,3), 'sum' performs area-weighted aggregation (recommended when the normals
      come from np.cross(edge1, edge2), whose magnitude encodes triangle area).
    - 'mean' performs simple averaging (less sensitive to triangle size).

    Returns a single unit (3,) direction vector suitable for transforms/arrows.
    """
    norms = np.asarray(norms, dtype=float)

    # Clean any NaN/Inf
    if np.isnan(norms).any() or np.isinf(norms).any():
        norms = np.nan_to_num(norms, nan=0.0, posinf=0.0, neginf=0.0)

    if norms.ndim == 1 and norms.shape == (3,):
        return unitize(norms)

    if norms.ndim == 2 and norms.shape[1] == 3:
        if norms.size == 0:
            # Degenerate case: fallback direction
            return np.array([1.0, 0.0, 0.0], dtype=float)
        if method == "sum":
            agg = norms.sum(axis=0)      # area-weighted
        elif method == "mean":
            agg = norms.mean(axis=0)
        else:
            raise ValueError("method must be 'sum' or 'mean'")
        return unitize(agg)

    raise ValueError(f"Expected shape (3,) or (N,3), got {norms.shape}")


def pick_normals(normals_dict: Dict[str, np.ndarray], side: str, prefer: str = "ace") -> np.ndarray:
    """
    Pick a unit direction vector from normals_dict for a given side ('right' or 'left').

    Keys expected:
      - 'right_ace_normals', 'left_ace_normals'
      - optionally 'right_fossa_normals', 'left_fossa_normals'

    'prefer' can be 'ace' or 'fossa'. If the preferred flavor is not present,
    it will try the other. Aggregation uses 'sum' to preserve area weighting.
    """
    if side not in ("right", "left"):
        raise ValueError("side must be 'right' or 'left'")

    order = [prefer, "fossa" if prefer == "ace" else "ace"]
    for flavor in order:
        key = f"{side}_{flavor}_normals"
        if key in normals_dict and normals_dict[key] is not None:
            return coerce_direction(normals_dict[key], method="sum")

    raise ValueError(
        f"No normals found for side '{side}'. "
        f"Tried keys: {side}_{order[0]}_normals and {side}_{order[1]}_normals."
    )


# -------------------------
# Main function: version_view
# -------------------------

def take_snapshots(
    mesh: trimesh.Trimesh,
    cents: np.ndarray,                       # shape (2, 3): [right_center, left_center]
    normals_dict: Dict[str, np.ndarray],     # e.g., {'right_ace_normals': (N,3), 'left_ace_normals': (M,3), ...}
    radii: Optional[Sequence[float]] = None, # optional [r_right, r_left] for spheres
    output_dir: Optional[str] = None,        # folder to save PNGs; if None and show=False, save to CWD
    show: bool = False,                      # interactive windows; defaults False for automated saving
    window_size: int = 2048,                 # screenshot size if saving
    normals_prefer: str = "ace",             # 'ace' or 'fossa' for normal-based views
    draw_arrows: bool = True,                # make arrow drawing optional
    base_color: Sequence[float] = (1.00, 0.90, 0.80),  # bone beige
    arrow_color: Sequence[float] = (0.25, 1.00, 0.00), # greenish arrows
    sphere_color: str = "green",             # sphere color (PyVista string or RGB)
    sphere_opacity: float = 0.05,             # sphere translucency
    filename_prefix: Optional[str] = None,   # optional prefix for saved filenames
    save_even_if_show: bool = True,          # save screenshots even when show=True
    use_exe_dir: bool = False,               # PyInstaller: save in executable directory
):
    """
    Render orientations for a trimesh using PyVista, using pre-provided normals.

    Views produced: front, back, left, right, bottom, left_normal, right_normal.
    'version_top' is intentionally omitted.

    Saving:
      - If output_dir is provided: saves <prefix_or_meshname>_<view_name>.png into that folder.
      - If output_dir is None and show=False: saves to current working directory.
      - If use_exe_dir=True: saves to the executable directory (PyInstaller-friendly).
      - If show=True and save_even_if_show=True: still saves screenshots.

    Lighting:
      - Clears default lights, adds a single low-intensity headlight,
        and reduces specular highlights on meshes for softer appearance.
    """
    # ---- Validate inputs ----
    cents = np.asarray(cents, dtype=float)
    if cents.shape != (2, 3):
        raise ValueError("cents must be shape (2, 3): [right_center, left_center].")

    # ---- Choose normals for normal views ----
    normals_prefer = str(normals_prefer).lower()
    if normals_prefer not in ("ace", "fossa"):
        raise ValueError("normals_prefer must be 'ace' or 'fossa'")

    n_right = pick_normals(normals_dict, "right", prefer=normals_prefer)
    n_left  = pick_normals(normals_dict, "left",  prefer=normals_prefer)

    # ---- Scene scale and camera distance ----
    aabb = mesh.bounds  # [[xmin,ymin,zmin],[xmax,ymax,zmax]]
    extent = aabb[1] - aabb[0]
    view_distance = 3.0 * float(np.max(extent))
    view_target = aabb.mean(axis=0)

    # ---- PyVista mesh (wrap trimesh) ----
    pv_mesh = pv.wrap(mesh)

    # ---- Optional spheres at centers ----
    spheres = []
    if radii is not None:
        radii = np.asarray(radii, dtype=float)
        if radii.shape != (2,):
            raise ValueError("'radii' must be length-2: [r_right, r_left].")
        spheres = [
            pv.Sphere(radius=float(radii[0]), center=cents[0]),
            pv.Sphere(radius=float(radii[1]), center=cents[1]),
        ]

    # ---- Camera up vectors ----
    up_default = np.array([0.0, 0.0, 1.0], dtype=float)
    up_bottom  = np.array([1.0, 0.0, 0.0], dtype=float)

    # ---- Define views (exclude top) ----
    views = {
        "version_front":        {"offset": np.array([view_distance, 0.0, 0.0]), "up": up_default},
        "version_back":         {"offset": np.array([-view_distance, 0.0, 0.0]), "up": up_default},
        "version_left":         {"offset": np.array([0.0, +view_distance, 0.0]), "up": up_default},
        "version_right":        {"offset": np.array([0.0, -view_distance, 0.0]), "up": up_default},
        "version_bottom":       {"offset": np.array([0.0, 0.0, -view_distance]), "up": up_bottom},
        "version_left_normal":  {"offset": view_distance * n_left,  "up": up_default},
        "version_right_normal": {"offset": view_distance * n_right, "up": up_default},
    }

    # ---- Arrows aligned to supplied normals (optional) ----
    arrow_length = 0.04 * view_distance
    def make_arrow(start, direction) -> pv.PolyData:
        return pv.Arrow(
            start=start,
            direction=unitize(direction),
            tip_length=0.20,
            tip_radius=0.15,
            shaft_radius=0.07,
            scale=arrow_length,
        )

    arrows = []
    if draw_arrows:
        arrows = [
            make_arrow(cents[0], n_right),  # right center arrow
            make_arrow(cents[1], n_left),   # left center arrow
        ]

    # ---- Output directory & filename prefix ----
    name = mesh.metadata.get("name", "mesh")
    if filename_prefix is None:
        filename_prefix = name

    # PyInstaller-friendly executable directory (optional)
    exe_dir = Path(getattr(sys, "_MEIPASS", Path.cwd())) if use_exe_dir else Path.cwd()
    outdir = Path(output_dir) if output_dir else (exe_dir if not show else None)
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)

    # ---- Render each view ----
    for view_name, spec in views.items():
        # Always use off-screen to ensure screenshots work reliably
        plotter = pv.Plotter(off_screen=True)  # important for saving

        # Softer background to avoid harsh contrast (you can set "white" if you prefer)
        plotter.set_background("white")

        # Main mesh with softer lighting parameters
        plotter.add_mesh(
            pv_mesh,
            color=tuple(base_color),
            smooth_shading=False,
            ambient=0.30,
            diffuse=0.60,
            specular=0.00,
        )

        # Optional arrows
        for arrow in arrows:
            plotter.add_mesh(
                arrow,
                color=tuple(arrow_color),
                ambient=0.25,
                diffuse=0.65,
                specular=0.00,
            )

        # Optional spheres
        for s in spheres:
            plotter.add_mesh(
                s,
                color=sphere_color,
                opacity=sphere_opacity,
                ambient=0.30,
                diffuse=0.60,
                specular=0.00,
            )

        # Camera positions (campos, target, camup)
        cam_pos = (view_target + spec["offset"]).tolist()
        plotter.camera_position = [cam_pos, view_target.tolist(), spec["up"].tolist()]

        # Lighting: clear defaults, add a single low-intensity headlight
        try:
            plotter.clear_lights()
        except Exception:
            pass

        try:
            headlight = pv.Light(
                position=cam_pos,              # follow camera
                focal_point=view_target.tolist(),
                light_type="headlight",        # headlight if supported
                intensity=0.6,                 # keep it gentle
                color=(1.0, 1.0, 1.0),
            )
            plotter.add_light(headlight)
        except Exception:
            # Fallback: light kit but keep shading parameters subdued
            plotter.enable_lightkit()

        # --- Save screenshot first (reliable), then optionally show ---
        filename = None
        if outdir:
            filename = outdir / f"{filename_prefix}_{view_name}.png"
        elif not show:
            # No output_dir and not showing -> save to current/exe directory
            filename = exe_dir / f"{filename_prefix}_{view_name}.png"

        # Render + screenshot
        plotter.render()
        if filename is not None:
            plotter.screenshot(str(filename), window_size=[window_size, window_size])
        # Optionally show interactively AFTER capturing the screenshot
        if show:
            plotter.show(window_size=[window_size // 2, window_size // 2], auto_close=True)
        else:
            plotter.close()
