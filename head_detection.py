import cv2
import numpy as np
    
#capture source video
cap = cv2.VideoCapture(0)

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

#path to face cascde
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#function to get coordinates
def get_coords(p1):
    try: return int(p1[0][0][0]), int(p1[0][0][1])
    except: return int(p1[0][0]), int(p1[0][1])

#define font and text color
font = cv2.FONT_HERSHEY_SIMPLEX


#define movement threshodls
max_head_movement = 20
movement_threshold = 50
gesture_threshold = 175

#find the face in the image
face_found = False
frame_num = 0
while frame_num < 30:
    # Take first frame and find corners in it
    frame_num += 1
    ret, frame = cap.read()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame_gray, 1.3, 5)
    #print(faces)
    (x,y,w,h) = (faces[0][0],faces[0][1],faces[0][2],faces[0][3])
    face_found = True
    cv2.imshow('Head Gesture Detection',frame)
    cv2.waitKey(1)
face_center = x+w/2, y+h/3
p0 = np.array([[face_center]], np.float32)

gesture = False
x_movement = 0
y_movement = 0
gesture_show = 60 #number of frames a gesture is shown
frame_count = 0

while True:    
    ret,frame = cap.read()
    old_gray = frame_gray.copy()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    
    #get the xy coordinates for points p0 and p1
    a,b = get_coords(p0), get_coords(p1)
    x_movement += abs(a[0]-b[0])
    y_movement += abs(a[1]-b[1])
    
    text = 'x_movement: ' + str(x_movement)
    if not gesture: cv2.putText(frame,text,(50,50), font, 0.8,(0,0,255),2)
    text = 'y_movement: ' + str(y_movement)
    if not gesture: cv2.putText(frame,text,(50,100), font, 0.8,(0,0,255),2)

    if x_movement > gesture_threshold:
        gesture = 'No'
    if y_movement > gesture_threshold:
        gesture = 'Yes'
    if gesture and gesture_show > 0:
        cv2.putText(frame,'Gesture Detected: ' + gesture,(50,50), font, 1.2,(0,0,255),3)
        gesture_show -=1
    if gesture_show == 0:
        gesture = False
        x_movement = 0
        y_movement = 0
        gesture_show = 60 #number of frames a gesture is shown
        
    if (frame_count < 12):
        p0 = p1
        frame_count += 1
    
    elif (frame_count >= 12 and frame_count <= 16):
        if (frame_count == 16):
            frame_count = 0
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame_gray, 1.3, 5)
        #for (x,y,w,h) in faces:
         #   cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        if (len(faces) != 0):
            face_center = x+w/2, y+h/3
            p0 = np.array([[face_center]], np.float32)
        else:
            p0 = p1
        frame_count += 1
            

    cv2.imshow('Head Gesture Detection',frame)
    k = cv2.waitKey(100) # change the value from the original 0 (wait forever) to something appropriate
    if k == 27:
        cv2.destroyAllWindows()
        break        

cv2.destroyAllWindows()
cap.release()