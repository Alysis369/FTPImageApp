# FTP_image_app
An application to pull images from an FTP server implementation.

--------------
## Demo
Demo:

![Overall Demo](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/draft_demo.gif)

## Prerequisite

## Demo Limitation
- date limitation

## Progress
- 2/29: Created producer and GUI threading
- 3/6: Created worker threading
- 3/8: Created MySQL container and tables
- 3/10: Established test db/ftp server, connected eq selection to DB

## TODO
- Add reject_code support to GUI
- Use threading to execute db calls to both db, prod might be slow and IO bound
- ImgPath list and txid list comparison is O(N*M)
  - possible for chunking and multiprocessing?
  - after every cross check, add job to queue instead of processing whole list, figure out how to determine job size
- Only support single equipment selection
- On prod, feature to automatically sort folder
- with workers not locking ftp curr dir, unable to support multiple directory
- Add feature for ALL images, and add support for VV images
- FTP requires spawning a different connection for each img download.. not sure if this is effective

## Launch
#### Start DB Container
```commandline
cd DB
docker compose up
```
#### Start App
```python
python ftp_app_main.py
```

