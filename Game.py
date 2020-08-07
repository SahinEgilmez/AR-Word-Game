#!/usr/bin/env python
# coding: utf8
'''
    Author: Şahin Eğilmez <segilmez@outlook.com>
'''

from Library import *  # Import constants, helper functions and using libraries
from Alphabet import *  # Import alphabet, questions and answers


class Face:  # Represent to human face datas (face image, coordinates, encoding etc.)
    face_id = 0
    encoding = None
    tracker = None
    letter = None
    img = None
    x = 0
    y = 0
    w = 0
    h = 0
    enable = False

    def __init__(self, face_id, encoding):
        self.face_id = face_id
        self.encoding = encoding

    def update(self, image):  # Update face datas when needed
        quality = self.tracker.update(image)
        tracked_position = self.tracker.get_position()
        self.x = int(tracked_position.left())
        self.y = int(tracked_position.top())
        self.w = int(tracked_position.width())
        self.h = int(tracked_position.height())
        self.letter.x = self.x
        return quality

    def save(self, crop_img):  # Save cropped face image and encode it
        encode = face_recognition.face_encodings(crop_img)
        if(len(encode) > 0):
            self.encoding = encode[0]
            return True
        else:
            return False

    def checkFace(self, crop_img):  # It checks that the faces are the same.
        encode2 = face_recognition.face_encodings(crop_img)
        if(len(encode2) > 0):
            img2_encoding = encode2[0]
        else:
            return False
        results = face_recognition.compare_faces(
            [self.encoding], img2_encoding, tolerance=0.30)
        if True in results:
            return True
        else:
            return False


class Game:  # Logic class of all project. It uses all other classes. Main.py call it dor rendering by each frame
    faces = {}
    faceTrackers = {}
    count = 3
    alphabet = None
    currentQuestion = None
    LEVEL = 1
    time = 60  # secs per minute
    resultImage = None
    ORDER_FLAG = False

    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier("./assets/haarcascade_frontalface_default.xml")
        cv2.startWindowThread()

        self.currentImage = 0  # the first image is selected
        self.currentImageID = 0
        self.rectangleColor = (0, 165, 255)
        self.frameCounter = 0
        self.currentFaceID = 0
        self.setPlayer(self.count)

    def setCapture(self, cap):  # set camera capture for initilization
        # Open the first webcame device
        self.capture = cap
        self.frameWidth = int(self.capture.get(3))  # float
        self.frameHeight = int(self.capture.get(4))  # float

    def setPlayer(self, count):  # set player number and get questions according to this.
        self.count = count
        self.alphabet = Alphabet(count)

        self.currentQuestion = self.alphabet.getQuestion()
        for i in range(0, count):
            self.faces[i] = Face(i, None)
            self.faceTrackers[i] = None
            if(self.faces[i].letter is None):
                self.faces[i].letter = self.currentQuestion.answer[i]

    def render(self):  # rendering function of game. Main.py calls it each frame
        # Retrieve the latest image from the webcam
        rc, baseImage = self.capture.read()
        baseImage = cv2.flip(baseImage, 1)  # mirror effect

        # Copy base image
        self.resultImage = baseImage.copy()

        # Increase the framecounter
        self.frameCounter += 1

        # Update all the trackers and remove the ones for which the update
        # indicated the quality was not good enough
        fidsToDelete = []
        for i in range(self.count):
            if(self.faces[i].tracker is not None):
                trackingQuality = self.faces[i].update(baseImage)
                # If the tracking quality is good enough, we must delete
                # this tracker
                if trackingQuality < 7:
                    self.faces[i].tracker = None

        # Every 10 frames, we will have to determine which faces
        # are present in the frame
        if (self.frameCounter % 10) == 0:
            # For the face detection, we need to make use of a gray
            # colored image so we will convert the baseImage to a
            # gray-based image
            gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
            # Now use the haar cascade detector to find all faces
            # in the image
            localFaces = self.faceCascade.detectMultiScale(gray, 1.3, 5)

            # Loop over all faces and check if the area for this
            # face is the largest so far
            # We need to convert it to int here because of the
            # requirement of the dlib tracker. If we omit the cast to
            # int here, you will get cast errors since the detector
            # returns numpy.int32 and the tracker requires an int
            for (_x, _y, _w, _h) in localFaces:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)

                # calculate the centerpoint
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                # Variable holding information which faceid we
                # matched with
                matchedFid = None

                # Now loop over all the trackers and check if the
                # centerpoint of the face is within the box of a
                # tracker
                for i in range(self.count):
                    if(self.faces[i].tracker is not None):
                        self.faces[i].update(baseImage)
                        pos = self.faces[i].tracker.get_position()

                        t_x = int(pos.left())
                        t_y = int(pos.top())
                        t_w = int(pos.width())
                        t_h = int(pos.height())

                        # calculate the centerpoint
                        t_x_bar = t_x + 0.5 * t_w
                        t_y_bar = t_y + 0.5 * t_h

                        # check if the centerpoint of the face is within the
                        # rectangleof a tracker region. Also, the centerpoint
                        # of the tracker region must be within the region
                        # detected as a face. If both of these conditions hold
                        # we have a match
                        if ((t_x <= x_bar <= (t_x + t_w)) and
                            (t_y <= y_bar <= (t_y + t_h)) and
                            (x <= t_x_bar <= (x + w)) and
                                (y <= t_y_bar <= (y + h))):
                            matchedFid = True

                # If no matched fid, then we have to create a new tracker
                if matchedFid is None:
                    # Create and store the tracker
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(baseImage, dlib.rectangle(x, y, x+w, y+h))
                    pos = tracker.get_position()

                    t_x = int(pos.left())
                    t_y = int(pos.top())
                    t_w = int(pos.width())
                    t_h = int(pos.height())

                    for i in range(self.count):
                        if(self.faces[i].tracker is None):
                            if(self.faces[i].encoding is None):
                                if(self.faces[i].save(baseImage[t_y:t_y+t_h, t_x:t_x+t_w]) is True):
                                    self.faces[i].tracker = tracker
                                    self.faces[i].update(baseImage)
                                    break
                            else:
                                crop = baseImage[t_y:t_y + t_h, t_x:t_x+t_w]
                                if(self.faces[i].checkFace(crop) is True):
                                    self.faces[i].tracker = tracker
                                    self.faces[i].update(baseImage)
                                    break
                    # Increase the currentFaceID counter
                    self.currentFaceID += 1

        for i in range(self.count):
            if(self.faces[i].tracker is not None):
                t_x = int(self.faces[i].x)
                t_y = int(self.faces[i].y)
                t_w = int(self.faces[i].w)
                t_h = int(self.faces[i].h)

                replaceImg = read_transparent_png(self.faces[i].letter)
                rows, cols, ch = replaceImg.shape
                # this points are necesary for the transformation
                pts1 = np.float32(
                    [[0, 0], [cols, 0], [cols, rows], [0, rows]])
                self.currentImage += 1
                # pts2 is used for defining the perspective transform
                pts2 = np.float32([[t_x, (DISTANCE_OF_LETTER*t_y)], [(t_x+t_w), (DISTANCE_OF_LETTER*t_y)],
                                   [(t_x+t_w), ((DISTANCE_OF_LETTER*t_y)+t_h)], [t_x, ((DISTANCE_OF_LETTER*t_y)+t_h)]])
                # compute the transform matrix
                M = cv2.getPerspectiveTransform(pts1, pts2)
                rows, cols, ch = self.resultImage.shape
                # make the perspective change in a image of the size of the camera input
                dst = cv2.warpPerspective(replaceImg, M, (cols, rows))
                # A mask is created for adding the two images
                # maskThreshold is a variable because that allows to substract the black background from different images
                ret, mask = cv2.threshold(cv2.cvtColor(
                    dst, cv2.COLOR_BGR2GRAY), MASK_TRESHOLD, 1, cv2.THRESH_BINARY_INV)
                # Erode and dilate are used to delete the noise
                mask = cv2.erode(mask, (3, 3))
                mask = cv2.dilate(mask, (3, 3))
                # The two images are added using the mask
                for c in range(0, 3):
                    self.resultImage[:, :, c] = dst[:, :, c] * \
                        (1-mask[:, :]) + self.resultImage[:, :, c]*mask[:, :]

                cv2.rectangle(self.resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), self.rectangleColor, 2)

        # draw question
        self.resultImage = self.drawQuestion(self.currentQuestion.question, self.frameHeight, self.frameWidth)

        if(self.isOrderTrue() is True):
            self.ORDER_FLAG = True
            print("ORDER IS TRUE")
            self.nextQuestion()
        return self.resultImage

    def dispose(self):  # dispose all datas when game closed or finished game
        # Destroy any OpenCV windows and exit the application
        self.capture.release()
        cv2.CAP_MSMF = 0
        cv2.destroyAllWindows()

    def isOrderTrue(self):  # checker for right order
        order = True
        lst = []
        for i in range(self.count):
            lst.append(self.faces[i].letter)
        lst.sort(key=lambda x: x.id, reverse=False)

        for i in range(self.count-1):
            x1 = lst[i].x
            x2 = lst[i+1].x
            if(x1 >= x2):  # if before x is bigger return false, otherwise true
                order = False
                break
        return order

    def nextQuestion(self):  # get next wuestion from Alphabet class
        self.LEVEL += 1
        self.currentQuestion = self.alphabet.getQuestion()
        for i in range(0, self.count):
            self.faces[i] = Face(-1, None)
            self.faceTrackers[i] = None
            if(self.faces[i].letter is None):
                self.faces[i].letter = self.currentQuestion.answer[i]

    def drawQuestion(self, word, fHeight, fWidth):  # draw question using OpenCV
        fontpath = "./assets/TTWPGOTT.ttf"
        (r, g, b, a) = (125, 222, 205, 1)
        line = word
        ft = ImageFont.truetype(fontpath, 20)
        img_pil = Image.fromarray(self.resultImage)
        draw = ImageDraw.Draw(img_pil)
        if(len(line) > 60):
            draw.rectangle(
                [(40, fHeight - 45), (fWidth-40, fHeight-5)], (61, 0, 59, 1))
            line1 = line[0:60]
            line2 = line[60:len(line)]
            draw.text((50, fHeight - 45),  line1,
                      font=ft, fill=(r, g, b, a))
            draw.text((50, fHeight - 25),  line2,
                      font=ft, fill=(r, g, b, a))
        else:
            draw.rectangle(
                [(40, fHeight - 45), (fWidth-40, fHeight-5)], (61, 0, 59, 1))
            draw.text((50, fHeight - 30),  line,
                      font=ft, fill=(r, g, b, a))

        # level
        draw.text((fWidth - 50, 5), str("LEVEL"), font=ft, fill=(61, 0, 59, 1))
        draw.ellipse([(fWidth - 50, 25), (fWidth-10, 65)], (61, 0, 59, 1))
        draw.text((fWidth - 40, 35), str("{:02d}".format(self.LEVEL)), font=ft, fill=(r, g, b, a))

        # time
        draw.text((15, 5), str("SÜRE"), font=ft, fill=(61, 0, 59, 1))
        draw.ellipse([(10, 25), (50, 65)], (61, 0, 59, 1))
        draw.text((20, 35), str("{:02d}".format(self.time)), font=ft, fill=(r, g, b, a))

        return np.array(img_pil)
