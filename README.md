# FTP_image_app
An application to pull images from an FTP server implementation.

--------------
## Demo
threading_success:

![Threading success!](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/threading_success.gif)

## Progress
- 2/29: Created producer and GUI threading
- 3/6: Created worker threading
- 3/8: Created MySQL container and tables
- 3/10: Established test db/ftp server, connected eq selection to DB

## TODO
- Add reject_code support to GUI
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

