## Face Alignment

I have a lot of old photos and I wanted to create something like [these youtube videos](https://www.youtube.com/watch?v=65nfbW-27ps). To run this:
- Add photos to a `/photos` folder (make sure the photos are dated so they can be put in order)
- `pip install -r requirements.txt`
- Download and extract [dlib's trained face detection model](https://github.com/davisking/dlib-models/blob/master/shape_predictor_5_face_landmarks.dat.bz2)
- Add some example photos of faces to a `/faces` folder
- Run `alignment.ipynb`

Here's an example:
![Example](example.gif)