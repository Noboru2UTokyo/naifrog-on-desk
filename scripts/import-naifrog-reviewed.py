#!/usr/bin/env python3
"""Package approved local review assets without regenerating or retiming pixels."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image, ImageSequence
import numpy as np

p=argparse.ArgumentParser();p.add_argument('review',type=Path);p.add_argument('--version',required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];theme=root/'themes/naifrog';assets=theme/'assets'
manifest=json.loads((args.review/'review-manifest.json').read_text())
selection=json.loads((args.review/'selection-policy.json').read_text())
assert selection['publicationAuthorized'] and not selection['pendingUserReview'], 'User acceptance is required'
byid={a['id']:a for a in manifest['actions']}
mapping={'idle-retained':'idle','happy-retained':'happy','building-pose-v5':'work-building','typing-pose-v3':'working','headphones-v1':'work-headphones','thinking-reference-v5':'thinking','sleep-pose-v3':'sleeping','bubble-pose-v3':'bubble','sleep-down-pose-v3':'yawning','wake-pose-v3':'waking'}
assert set(mapping)==set(selection['allowedActionIds'])
provenance=[]
for candidate,dest in mapping.items():
    a=byid[candidate]
    for key,suffix in [('webp','.webp'),('poster','-poster.png')]:
        source=args.review/a[key];target=assets/(dest+suffix)
        shutil.copyfile(source,target)
        if key=='webp':
            provenance.append({'candidate':candidate,'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frames':a['frames'],'durationMs':a['durationMs'],'loop':a['loop']})
# Older reading/notes remain auxiliary display hints, never automatic rotation.
keep=set(mapping.values())|{'work-reading','work-notes'}
for asset in assets.iterdir():
    stem=asset.stem.removesuffix('-poster')
    if stem not in keep and asset.suffix in {'.webp','.png'}:asset.unlink()

cfg=json.loads((theme/'theme.json').read_text());cfg['version']=args.version
cfg['description']='保留惊鸿一瞥和 12 秒大笑；按会话数量循环打字、上一版耳机和施工，原图托腮，趴睡及连续入睡／醒来，空闲吹泡泡。取消杂耍和爬行，保留原音效。'
cfg['states'].update(working=['working.webp'],juggling=['work-headphones.webp'],roam={'files':[],'fallbackTo':'idle'},yawning=['yawning.webp'],dozing=['sleeping.webp'],collapsing=['sleeping.webp'],sleeping=['sleeping.webp'],waking=['waking.webp'])
cfg['workingTiers']=[{'minSessions':3,'file':'work-building.webp'},{'minSessions':2,'file':'work-headphones.webp'},{'minSessions':1,'file':'working.webp'}]
cfg['jugglingTiers']=[{'minSessions':1,'file':'work-headphones.webp'}]
cfg['idleAnimations']=[{'file':'bubble.webp','duration':byid['bubble-pose-v3']['durationMs']}]
cfg['timings'].update(yawnDuration=8000,collapseDuration=1,wakeDuration=8000)
cfg['reactions']['clickRight']['duration']=byid['thinking-reference-v5']['durationMs']
cfg['fileHitBoxes']={}
for file in sorted(assets.glob('*.webp')):
    bounds=[]
    for frame in ImageSequence.Iterator(Image.open(file)):
        alpha=np.array(frame.convert('RGBA'))[:,:,3];ys,xs=np.where(alpha>32)
        if len(xs):bounds.append([int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)])
    a=np.array(bounds);x,y=a[:,:2].min(0);right,bottom=a[:,2:].max(0)
    cfg['fileHitBoxes'][file.name]={'x':int(x),'y':int(y),'w':int(right-x),'h':int(bottom-y)}
cfg['hitBoxes']['default']=cfg['fileHitBoxes']['idle.webp'];cfg['hitBoxes']['sleeping']=cfg['fileHitBoxes']['sleeping.webp']
cfg['transitions']={file:{'in':140,'out':140} for file in cfg['fileHitBoxes']}
for file in ['yawning.webp','sleeping.webp','waking.webp']:cfg['transitions'][file]={'in':0,'out':0}
cfg['rendering']['lowPowerStaticImageOverrides']={state:{'from':files[0],'to':files[0].replace('.webp','-poster.png')} for state,files in cfg['states'].items() if isinstance(files,list)}
(theme/'theme.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
report={'version':args.version,'approval':'User accepted the local review and authorized local/GitHub release.','reviewRevision':manifest['revision'],'assets':provenance,'removedAnimations':['juggling','roam'],'workRotation':'repeat until upstream state or tier changes','subagents':'headphones at every count','sleepMapping':'yawning=entry; dozing/collapsing/sleeping=prone; waking=rise; no second entry replay','generator':'Full MiniMax H3, 1440x1440, 24fps; retained idle/laugh unchanged'}
(theme/'approved-assets.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':args.version,'copied':len(provenance),'animationFiles':len(cfg['fileHitBoxes'])}))
