import pyvista as pv

def take_snapshots(mesh, delay):
    polydata = pv.wrap(mesh)
    # Define camera views
    views = {
        'front': {'position': [3, 0, 0], 'viewup': [0, 0, 1]},
        'back': {'position': [-3, 0, 0], 'viewup': [0, 0, 1]},
        'left': {'position': [0, 3, 0], 'viewup': [0, 0, 1]},
        'right': {'position': [0, -3, 0], 'viewup': [0, 0, 1]},
        'top': {'position': [0, 0, 3], 'viewup': [1, 0, 0]},
        'bottom': {'position': [0, 0, -3], 'viewup': [1, 0, 0]}
    }
    # Display each view one at a time and save the image
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    # Front view
    plotter.camera_position = [3, 0, 0]
    plotter.camera.up = [0, 0, 1]
    plotter.camera.focal_point = polydata.center
    plotter.show(title='View: Front', auto_close=False)
    #plotter.screenshot('front.png')

    # Back view
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    plotter.camera_position = [-3, 0, 0]
    plotter.camera.up = [0, 0, 1]
    plotter.camera.focal_point = polydata.center
    plotter.show(title='View: Back', auto_close=False)
    #plotter.screenshot('back.png')

    # Left view
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    plotter.camera_position = [0, 3, 0]
    plotter.camera.up = [0, 0, 1]
    plotter.camera.focal_point = polydata.center
    plotter.show(title='View: Left', auto_close=False)
    #plotter.screenshot('left.png')

    # Right view
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    plotter.camera_position = [0, -3, 0]
    plotter.camera.up = [0, 0, 1]
    plotter.camera.focal_point = polydata.center
    plotter.show(title='View: Right', auto_close=False)
    #plotter.screenshot('right.png')

    # Top view
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    plotter.camera_position = [0, 0, 3]
    plotter.camera.up = [0, 1, 0]
    plotter.camera.focal_point = polydata.center
    plotter.show(title='View: Top', auto_close=False)
    #plotter.screenshot('top.png')

    # Bottom view
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    plotter.camera_position = [0, 0, -3]
    plotter.camera.up = [0, 1, 0]
    plotter.camera.focal_point = polydata.center
    plotter.show(title='View: Bottom', auto_close=False)
    #plotter.screenshot('bottom.png')