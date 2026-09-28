#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""KWin region/video recording with independently mixed desktop and microphone audio."""
import argparse,json,os,re,signal,subprocess,sys,tempfile,time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--output',required=True);p.add_argument('--geometry',default='');p.add_argument('--monitor',default='')
for name in ('desk','mic'):
 p.add_argument('--'+name+'-vol',type=float,default=1);p.add_argument('--'+name+'-mute',default='false')
p.add_argument('--mic-dev',default='')
a=p.parse_args();runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'velum'
state=json.loads((runtime/'kwin.json').read_text());screens=state['screens']
if a.geometry:
 match=re.fullmatch(r'(-?\d+),(-?\d+) (\d+)x(\d+)',a.geometry)
 if not match:raise SystemExit('Invalid recording region')
 region=list(map(int,match.groups()))
else:
 screen=next((s for s in screens if s['name']==(a.monitor or state['activeScreen'])),screens[0]);region=[screen[k] for k in ('x','y','width','height')]
if region[2]<2 or region[3]<2:raise SystemExit('Recording region is too small')
# Even dimensions work with every H.264 encoder; output settings are untouched.
region[2]-=region[2]%2;region[3]-=region[3]%2
stopping=False
def stop(*_):
 global stopping;stopping=True
signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
def finish(proc):
 if proc and proc.poll() is None:
  proc.send_signal(signal.SIGINT)
  try:proc.wait(timeout=12)
  except subprocess.TimeoutExpired:proc.kill();proc.wait();raise RuntimeError('Recorder did not finalize')
video=audio=None
try:
 with tempfile.TemporaryDirectory(prefix='record-',dir=runtime) as tmp:
  tmp=Path(tmp);vp=tmp/'video.mp4';ap=tmp/'audio.mka'
  video=subprocess.Popen([str(Path(__file__).with_name('velum-recorder')),*map(str,region),'0',str(vp)],stdout=subprocess.PIPE,text=True)
  if video.stdout.readline().strip()!='RECORDING':raise RuntimeError('KWin could not start recording')
  started=time.monotonic()
  inputs=[];filters=[]
  if a.desk_mute!='true':inputs.append(('default_output',a.desk_vol))
  if a.mic_mute!='true':inputs.append((a.mic_dev or 'default_input',a.mic_vol))
  cmd=['ffmpeg','-nostdin','-v','error','-y']
  for i,(device,vol) in enumerate(inputs):
   if device=='default_output':device=subprocess.check_output(['pactl','get-default-sink'],text=True).strip()+'.monitor'
   if device=='default_input':device=subprocess.check_output(['pactl','get-default-source'],text=True).strip()
   cmd+=['-thread_queue_size','512','-f','pulse','-i',device]
   filters.append(f'[{i}:a]volume={max(0,min(2,vol))}[a{i}]')
  if inputs:
   filters.append(''.join(f'[a{i}]' for i in range(len(inputs)))+f'amix=inputs={len(inputs)}:normalize=0[mix]')
   audio=subprocess.Popen(cmd+['-filter_complex',';'.join(filters),'-map','[mix]','-c:a','pcm_s16le',str(ap)])
  print('RECORDING',flush=True)
  while not stopping and video.poll() is None:
   if audio and audio.poll() is not None:raise RuntimeError('Audio capture stopped unexpectedly')
   time.sleep(.1)
  elapsed=time.monotonic()-started
  finish(video);finish(audio)
  if video.returncode!=0:raise RuntimeError('Video capture failed')
  # KWin emits frames only when pixels change. Give the final packet its real
  # screen time so a still image does not truncate the video or desktop audio.
  info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-select_streams','v:0','-count_packets','-show_entries','stream=nb_read_packets','-of','json',str(vp)]))
  last=int(info['streams'][0]['nb_read_packets'])-1
  duration=f'setts=duration=if(eq(N\\,{last})\\,max(DURATION\\,{elapsed:.6f}/TB-DTS)\\,DURATION)'
  mux=['ffmpeg','-nostdin','-v','error','-y','-i',str(vp)]
  if audio:mux+=['-i',str(ap),'-map','0:v','-map','1:a','-c:a','aac']
  mux+=['-c:v','copy','-bsf:v',duration,'-movflags','+faststart',a.output]
  subprocess.run(mux,check=True)

except Exception as e:
 finish(video);finish(audio)
 subprocess.run(['notify-send','-u','critical','Velum recording',str(e)])
 raise
