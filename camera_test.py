from time import sleep
import depthai
import logging


class Device(depthai.Device):
  def __init__(self):
    while True:
      try:
        logging.info("initializing depthai")
        super().__init__()
      except RuntimeError as error:
        logging.info(f'{error.args[0]}. Trying again...')
        sleep(1)
      else:
        break
    self.setLogLevel(depthai.LogLevel.DEBUG)
    self.setLogOutputLevel(depthai.LogLevel.DEBUG)
    self.pipeline = depthai.Pipeline()
    self.cameras = {}

  def load(self):
    self.startPipeline(self.pipeline)
    for device in self.cameras.values():
      device._set_queue()

  def create_stereo_pair(self):
    self.stereo = self.pipeline.create(depthai.node.StereoDepth)
    self.stereo.setRectifyEdgeFillColor(-1)
    self.stereo.setDefaultProfilePreset(
        depthai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    self.stereo.initialConfig.setMedianFilter(depthai.MedianFilter.KERNEL_7x7)
    self.stereo.setLeftRightCheck(True)
    self.stereo.setExtendedDisparity(True)
    self.stereo.setSubpixel(False)

    left_camera = Camera(
        device=self,
        stream_name='left',
        node=depthai.node.MonoCamera,
        socket=depthai.CameraBoardSocket.LEFT,
        res=depthai.MonoCameraProperties.SensorResolution.THE_400_P,
        fps=30,
        isp3a_fps=15,
    )
    right_camera = Camera(
        device=self,
        stream_name='right',
        node=depthai.node.MonoCamera,
        socket=depthai.CameraBoardSocket.RIGHT,
        res=depthai.MonoCameraProperties.SensorResolution.THE_400_P,
        fps=30,
        isp3a_fps=15,
    )

    left_camera.sensor.out.link(self.stereo.left)
    right_camera.sensor.out.link(self.stereo.right)

    self.stereo.rectifiedLeft.link(left_camera.xout.input)
    self.stereo.rectifiedRight.link(right_camera.xout.input)

    self.stream_name = 'disparity'
    disparity_xout = self.pipeline.createXLinkOut()
    disparity_xout.setStreamName(self.stream_name)
    self.stereo.disparity.link(disparity_xout.input)

    self.camera = self.cameras[self.stream_name] = self
    self.cameras[right_camera.stream_name] = right_camera
    self.cameras[left_camera.stream_name] = left_camera

  def create_rgb_camera(self):
    rgb_camera = Camera(
        device=self,
        stream_name='rgb',
        node=depthai.node.ColorCamera,
        socket=depthai.CameraBoardSocket.RGB,
        res=depthai.ColorCameraProperties.SensorResolution.THE_1080_P,
        fps=30,
        isp3a_fps=15,
        encode=True
    )
    rgb_camera.sensor.video.link(rgb_camera.encoder.input)
    rgb_camera.encoder.bitstream.link(rgb_camera.xout.input)
    self.cameras[rgb_camera.stream_name] = rgb_camera

  def get_frame(self):
    return self.disparity_queue.get().getCvFrame()

  def _set_queue(self):
    self.disparity_queue = self.getOutputQueue(
        name='disparity', maxSize=1, blocking=False)

  def __del__(self):
    try:
      self.close()
    except:
      pass


class Camera():
  def __init__(self, device, stream_name, node, socket, res, fps, isp3a_fps, encode=False):
    self.device = device
    self.stream_name = stream_name
    self.xout = device.pipeline.createXLinkOut()
    self.xout.setStreamName(self.stream_name)
    self.sensor = device.pipeline.create(node)
    self.sensor.setFps(fps)
    self.sensor.setIsp3aFps(isp3a_fps)
    self.sensor.setBoardSocket(socket)
    self.sensor.setResolution(res)
    self.xout.input.setBlocking(False)
    self.xout.input.setQueueSize(1)
    if encode:
      self.encoder = self.device.pipeline.createVideoEncoder()
      self.encoder.setDefaultProfilePreset(
          fps, depthai.VideoEncoderProperties.Profile.MJPEG)
      self.encoder.setQuality(25)
      self.get_frame = self._get_encoded_data

  def _set_queue(self):
    self.queue = self.device.getOutputQueue(
        name=self.stream_name, maxSize=1, blocking=False)

  def get_frame(self):
    return self.queue.get().getCvFrame()

  def _get_encoded_data(self):
    return self.queue.get().getData()


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  device = Device()
  device.create_stereo_pair()
  device.create_rgb_camera()
  device.load()
  logging.info("Running...")
  while True:
    for camera in device.cameras.values():
      camera.get_frame()
