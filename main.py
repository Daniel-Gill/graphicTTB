from dataclasses import dataclass
import math
import random
import dearpygui.dearpygui as dpg
import json
dpg.create_context()

class Station:
    name: str
    y: int
    editing: bool = False
    highlighted: bool = False
    
    def __init__(self, name, y):
        self.name = name
        self.y = y
        
    def __str__(self):
        return f"Station: {self.name}"
        
class Portal (Station):
    def __init__(self, name, y):
        super().__init__(name, y)
        
    def __str__(self):
        return f"Portal: {self.name}"
    
class Service:
    ref: str
    stops: list
    colour: tuple
    
    def __init__(self, ref, stops, colour):
        self.ref = ref
        self.stops = stops
        self.colour = colour
    
class Stop:
    station: Station
    arr : int
    dep : int
    
    def __init__(self, station, arr, dep):
        self.station = station
        # convert to minutes
        if type(arr) == str and arr != "" and arr != None:
            arr = int(arr.split(":")[0])*60 + int(arr.split(":")[1])
        if type(dep) == str and dep != "" and dep != None:
            dep = int(dep.split(":")[0])*60 + int(dep.split(":")[1])
        if arr == '' or arr == None:
            arr = dep-0.25
            dep = dep+0.25
        if dep == '' or dep == None:
            dep = arr+0.25
            arr = arr-0.25
        if arr == dep:
            arr = arr-0.25
            dep = dep+0.25
        self.arr = arr
        self.dep = dep
    
stations = [Station("Station 0", 100), Station("Station 1", 200), Station("Station 2", 400), Portal("Portal 0", 50), Portal("Portal 1", 450)]

services = [
    Service("Service 1", [Stop(stations[0], 0, 2), Stop(stations[1], 10, 12), Stop(stations[2], 26, 28)], colour=(255,0,0)),
    Service("Service 2", [Stop(stations[0], 5, 6), Stop(stations[2], 30, 31)], colour=(0,255,0)),
    Service("Service 3", [Stop(stations[2], 3, 4), Stop(stations[1], 18, 19)], colour=(0,0,255))
]

def get_station(name):
    for station in stations:
        if station.name == name:
            return station
    return None 

start_time = 0
end_time = 24*60
zoom_level = (end_time - start_time)

margin = 25

def load_data():
    file = open("birmingham.ttb", "r")
    data = json.load(file)
    stations.clear()
    services.clear()
    for station in data["stations"]:
        stations.append(Station(station["name"], station["y"]))
    for service in data["services"]:
        stops = []
        for stop in service["stops"]:
            stops.append(Stop(get_station(stop["station"]), stop["arr"], stop["dep"]))
        services.append(Service(service["ref"], stops, (random.randint(50,255),random.randint(50,255),random.randint(50,255))))
    file.close()
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()

def zoom_in():
    global start_time, end_time, zoom_level
    if end_time-start_time <= 120:
        return
    start_time += 60
    end_time -= 60
    zoom_level = (end_time-start_time)
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()

def zoom_out():
    global start_time, end_time, zoom_level
    if end_time-start_time >= 24*60:
        return
    if start_time-60 < 0:
        end_time += 60
    elif end_time+60 > 24*60:
        start_time -= 60
    else: 
        start_time -= 60
        end_time += 60
    zoom_level = (end_time - start_time)
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()
    
def move_left():
    global start_time, end_time
    if start_time == 0:
        return
    start_time -= 60
    end_time -= 60
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()
    
def move_right():
    global start_time, end_time
    if end_time == 24*60:
        return
    start_time += 60
    end_time += 60
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()

def zoom_to_fit():
    global start_time, end_time, zoom_level
    start_time = 24*60
    end_time = 0
    for service in services:
        for stop in service.stops:
            if stop.arr < start_time:
                start_time = stop.arr
            if stop.dep > end_time:
                end_time = stop.dep
    # round to nearest hour
    start_time = math.floor(start_time/60)*60
    end_time = math.ceil(end_time/60)*60
    zoom_level = (end_time - start_time)
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()

def draw_grid():
    height = dpg.get_item_height(drawlist)
    width = dpg.get_item_width(drawlist)
    dpg.draw_line((margin,margin), (width-margin,margin), color=(255,255,255), thickness=3, parent=drawlist)
    dpg.draw_line((margin,margin), (margin,height-margin), color=(255,255,255), thickness=3, parent=drawlist)
    dpg.draw_line((margin,height-margin), (width-margin,height-margin), color=(255,255,255), thickness=3, parent=drawlist)
    
    # Drawing station lines
    for station in stations:
        if station is Portal:
            dpg.draw_text((margin+5,station.y+5), station.name, color=(150,150,150), parent=drawlist, size=16)
            dpg.draw_line((margin,station.y+margin), (width-margin,station.y+margin), color=(150,150,150), thickness=1.5 if station.highlighted else 0.5, parent=drawlist, tag=station.name)
        else:
            dpg.draw_text((margin+5,station.y+5), station.name, color=(255,255,255), parent=drawlist, size=16)
            dpg.draw_line((margin,station.y+margin), (width-margin,station.y+margin), color=(255,255,255), thickness=3 if station.highlighted else 1, parent=drawlist, tag=station.name)
    
    # Drawing time lines
    print(zoom_level)
    gap = 60
    interval = (width-2*margin)/(end_time-start_time)
    for i in range(start_time, end_time, gap):
        dpg.draw_text((margin+(i-start_time)*interval,margin-20), f"{i//60:02d}:{i%60:02d}", color=(255,255,255), parent=drawlist, size=16)
        dpg.draw_line((margin+(i-start_time)*interval,margin), (margin+(i-start_time)*interval,height-margin), color=(255,255,255), thickness=1, parent=drawlist)
    if zoom_level <= 360:
        for i in range(start_time+30, end_time, gap):
            dpg.draw_line((margin+(i-start_time)*interval,margin), (margin+(i-start_time)*interval,height-margin), color=(255,255,255), thickness=0.5, parent=drawlist)
            if zoom_level <= 300:
                dpg.draw_text((margin+(i-start_time)*interval,margin-20), f"{i//60:02d}:{i%60:02d}", color=(255,255,255), parent=drawlist, size=13)
    if zoom_level <= 180:
        for i in range(start_time+15, end_time, int(gap/2)):
            dpg.draw_line((margin+(i-start_time)*interval,margin), (margin+(i-start_time)*interval,height-margin), color=(255,255,255), thickness=0.5, parent=drawlist)
            if zoom_level <= 120:
                dpg.draw_text((margin+(i-start_time)*interval,margin-20), f"{i//60:02d}:{i%60:02d}", color=(255,255,255), parent=drawlist, size=13)
    dpg.draw_line((margin+(end_time-start_time)*interval,margin), (margin+(end_time-start_time)*interval,height-margin), color=(255,255,255), thickness=1, parent=drawlist)
    

    # Drawing services
    for service in services:
        for i in range(len(service.stops)-1):
            start = service.stops[i]
            next = service.stops[i+1]
            dpg.draw_line((margin+(start.arr-start_time)*interval, start.station.y+margin), (margin+(start.dep-start_time)*interval, start.station.y+margin), color=service.colour, thickness=3, parent=drawlist)
            dpg.draw_line((margin+(start.dep-start_time)*interval, start.station.y+margin), (margin+(next.arr-start_time)*interval, next.station.y+margin), color=service.colour, thickness=3, parent=drawlist)
            if i == len(service.stops)-2:
                dpg.draw_line((margin+(next.arr-start_time)*interval, next.station.y+margin), (margin+(next.dep-start_time)*interval, next.station.y+margin), color=service.colour, thickness=3, parent=drawlist)
            
def editor_save(sender, app_data, user_data):
    new_name = dpg.get_value("new_station_name")
    new_y = dpg.get_value("new_station_y")
    user_data.name = new_name
    user_data.y = new_y
    user_data.editing = False
    user_data.highlighted = False
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()
    dpg.delete_item(editor_group, children_only=True)
    draw_editor()
    
def editor_cancel(sender, app_data):
    for station in stations:
        station.editing = False
        station.highlighted = False
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()
    dpg.delete_item(editor_group, children_only=True)
    draw_editor()

def draw_editor():
    for station in stations:
        if station.editing:
            dpg.add_input_text(label="Name", default_value=station.name, parent=editor_group, tag="new_station_name")
            dpg.add_input_int(label="Y", default_value=station.y, parent=editor_group, tag="new_station_y")
            
            dpg.add_button(label="Save", parent=editor_group, callback=editor_save, user_data=station)
            dpg.add_button(label="Cancel", parent=editor_group, callback=editor_cancel)

def hover_handler(sender, app_data):
    x,y = dpg.get_mouse_pos()
    border_correction = 5
    for station in stations:
        if y-margin-border_correction > station.y-10 and y-margin-border_correction < station.y+10 and x > margin and x < 1000 - margin:
            station.highlighted = True
        else:
            station.highlighted = False
            
    # Add highlighting to already editing station
    for station in stations:
        if station.editing:
            station.highlighted = True
    dpg.delete_item(drawlist, children_only=True)
    draw_grid()
    
def click_handler(sender, app_data):
    x,y = dpg.get_mouse_pos()    
    # Checking for clicks within the grid
    border_correction = 5
    for station in stations:
        if y-margin-border_correction > station.y-10 and y-margin-border_correction < station.y+10 and x > margin and x < dpg.get_item_width(drawlist)-margin:
            for otherstation in stations:
                if otherstation != station:
                    otherstation.editing = False
                    otherstation.highlighted = False
            station.editing = True
            station.highlighted = True
            dpg.delete_item(drawlist, children_only=True)
            draw_grid()
            dpg.delete_item(editor_group, children_only=True)
            draw_editor()

with dpg.handler_registry() as registry:
    dpg.add_mouse_move_handler(callback=hover_handler)
    dpg.add_mouse_click_handler(callback=click_handler)

with dpg.theme() as canvas_theme, dpg.theme_component():
    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0,0)

with dpg.window() as window:

    with dpg.group(horizontal=True):
        dpg.add_button(label="Save")
        dpg.add_button(label="Load", callback=load_data)
        dpg.add_button(label="Export")
        dpg.add_button(label="Zoom In", callback=zoom_in)
        dpg.add_button(label="Zoom Out", callback=zoom_out)
        dpg.add_button(label="Move Left", callback=move_left)
        dpg.add_button(label="Move Right", callback=move_right)
        dpg.add_button(label="Zoom to Fit", callback=zoom_to_fit)
    
    with dpg.group(horizontal=True):
        with dpg.child_window(width=1000, height=600) as canvas:
            dpg.bind_item_theme(canvas, canvas_theme)
            drawlist = dpg.add_drawlist(width=1000, height=600)
            draw_grid()
        with dpg.child_window(width=400, height=600, tag="editor"):
            editor_group = dpg.add_group()
            draw_editor()
            
dpg.set_primary_window(window, True)
dpg.create_viewport(width=1200, height=800, title="Timetable Editor")
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
dpg.destroy_context()