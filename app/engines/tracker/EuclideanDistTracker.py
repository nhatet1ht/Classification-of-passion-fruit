import math
class EuclideanDistTracker(object):
    def __init__(self, frame_size):
        # Storing the positions of center of the objects
        self.center_points = {}
        # Count of ID of boundng boxes
        # each time new object will be captured the id will be increassed by 1
        self.id_count = 0
        self.height, self.width = frame_size

    def update(self, objects_rect, distance_threshold=25): #(x1,y1,x2,y2)
        objects_bbs_ids = [] # (x1, y1, x2,y2)
        # Calculating the center of objects
        for rect in objects_rect:
            x1, y1, x2, y2 = rect
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            # Find if object is already detected or not
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = abs(center_y - pt[1])
                if dist < distance_threshold and (pt[0]-self.width/2)*(center_x-self.width/2) > 0:
                    self.center_points[id] = (center_x, center_y)
                    # print(self.center_points)
                    objects_bbs_ids.append([x1, y1, x2, y2, id])     
                    same_object_detected = True
                    break
           # Assign the ID to the detected object
            if same_object_detected is False:
               self.center_points[self.id_count] = (center_x, center_y)      
                               
               objects_bbs_ids.append([x1, y1, x2, y2, self.id_count])       
               self.id_count += 1
        # Cleaning the dictionary ids that are not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _,_,_,_, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center
       # Updating the dictionary with IDs that is not used
        self.center_points = new_center_points.copy()
        return objects_bbs_ids