import os, json, shutil, subprocess, glob, random
LEVELS = "/sdcard/ModData/com.beatgames.beatsaber/Mods/SongCore/CustomLevels"

def get_info(f):
    p = f + "/Info.dat" if os.path.exists(f + "/Info.dat") else f + "/info.dat"
    return (p, json.loads(open(p, "rb").read().decode("utf-8-sig"))) if os.path.exists(p) else (None, None)

def slice_dat(dp, sb, eb, off, rat):
    d = json.loads(open(dp, "rb").read().decode("utf-8-sig"))
    def sh(items, k):
        out = []
        for it in items:
            t = float(it.get(k, 0))
            if sb <= t <= eb:
                it[k] = round(((t - sb) * rat) + off, 4)
                out.append(it)
        return out
    for k in ["_notes", "_obstacles", "_events"]:
        if k in d: d[k] = sh(d[k], "_time")
    for k in ["colorNotes", "bombNotes", "obstacles", "basicBeatmapEvents"]:
        if k in d: d[k] = sh(d[k], "b")
    if "_customData" in d and "_BPMChanges" in d["_customData"]: del d["_customData"]["_BPMChanges"]
    if "bpmEvents" in d: d["bpmEvents"] = []
    return d

print("=== Shaffuru Medley & Mashup Cutter ===")
mode = input("Mode (1=Single Cut, 2=2-Song Mashup, 3=Random Shaffuru Medley): ").strip()
clips, setlist = [], []
if mode == "3":
    cnt = int(input("How many songs (e.g. 5): ").strip())
    sec = float(input("Seconds per song (e.g. 20): ").strip())
    dm = {"1": "ExpertPlusStandard.dat", "2": "ExpertStandard.dat", "3": "HardStandard.dat"}
    td = dm.get(input("Diff (1=Ex+, 2=Ex, 3=Hard): ").strip(), "ExpertPlusStandard.dat")
    pool = [d for d in glob.glob(LEVELS + "/*") if "Shaffuru" not in d and os.path.exists(os.path.join(d, td))]
    for i, f in enumerate(random.sample(pool, min(cnt, len(pool)))):
        _, inf = get_info(f)
        aud = os.path.join(f, inf.get("_songFilename", "song.egg"))
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", aud], capture_output=True, text=True)
        dur = float(r.stdout.strip()) if r.stdout.strip() else 120.0
        st = round(random.uniform(max(10.0, dur * 0.25), max(12.0, dur * 0.65)), 1)
        en = min(dur - 2.0, st + sec)
        t_s = int(i * sec)
        setlist.append(f"{t_s//60}:{t_s%60:02d} {inf.get('_songName')}")
        print(f"Slice {i+1}: {inf.get('_songName')} ({st}s-{en}s)")
        clips.append((f, st, en))
    dst = f"{LEVELS}/Shaffuru_Medley_{len(clips)}x{int(sec)}s_{random.randint(100,999)}"
    title, sub = f"Shaffuru Medley ({len(clips)}x{int(sec)}s)", " | ".join(setlist)
else:
    for n in range(1, 3 if mode == "2" else 2):
        q = input(f"Search Song {n}: ").strip().lower()
        ms = [d for d in sorted(glob.glob(LEVELS + "/*")) if q in os.path.basename(d).lower()]
        for i, m in enumerate(ms[:12]): print(f"{i}: {os.path.basename(m)}")
        f = ms.__getitem__(int(input("Pick #: ").strip()))
        st, en = float(input("Start (s): ")), float(input("End (s): "))
        clips.append((f, st, en))
    _, i1 = get_info(clips.__getitem__(0).__getitem__(0))
    dst = f"{LEVELS}/Custom_Mashup_{random.randint(100,999)}"
    title, sub = f"{i1.get('_songName')} Mashup", "Custom Cut/Mashup"

shutil.copytree(clips.__getitem__(0).__getitem__(0), dst)
_, bi = get_info(dst)
bbpm = float(bi.get("_beatsPerMinute", 120))
tmps = []
for i, (f, st, en) in enumerate(clips):
    _, inf = get_info(f)
    tf = os.path.join(dst, f"t{i}.ogg")
    subprocess.run(["ffmpeg", "-y", "-ss", str(st), "-to", str(en), "-i", os.path.join(f, inf.get("_songFilename", "song.egg")), "-vn", "-ar", "44100", "-ac", "2", "-c:a", "libvorbis", "-q:a", "5", tf], check=True)
    tmps.append(tf)
oa = os.path.join(dst, bi.get("_songFilename", "song.egg"))
if len(tmps) == 1: os.replace(tmps.__getitem__(0), oa)
else:
    inp, flt = [], ""
    for i, tf in enumerate(tmps): inp.extend(["-i", tf]); flt += f"[{i}:a]"
    mo = os.path.join(dst, "m.ogg")
    subprocess.run(["ffmpeg", "-y"] + inp + ["-filter_complex", flt + f"concat=n={len(tmps)}:v=0:a=1[a]", "-map", "[a]", "-c:a", "libvorbis", "-q:a", "5", mo], check=True)
    os.replace(mo, oa)
    for tf in tmps: os.remove(tf)
bi["_songName"], bi["_songSubName"], bi["_songTimeOffset"] = title, sub, 0
for bs in bi.get("_difficultyBeatmapSets", []):
    for df in bs.get("_difficultyBeatmaps", []):
        df["_noteJumpMovementSpeed"], df["_noteJumpStartBeatOffset"] = 16.0, 0.0
        fn = df.get("_beatmapFilename", "")
        do = os.path.join(dst, fn)
        if not os.path.exists(do): continue
        md, cur = None, 0.0
        for f, st, en in clips:
            _, inf = get_info(f)
            bpm = float(inf.get("_beatsPerMinute", 120))
            sb, eb, rat = (st * bpm) / 60.0, (en * bpm) / 60.0, bbpm / bpm
            ds = os.path.join(f, fn)
            if os.path.exists(ds):
                sl = slice_dat(ds, sb, eb, cur, rat)
                if md is None: md = sl
                else:
                    for k in ["_notes", "_obstacles", "_events", "colorNotes", "bombNotes", "obstacles", "basicBeatmapEvents"]:
                        if k in md and k in sl: md[k].extend(sl[k])
            cur += (eb - sb) * rat
        if md: json.dump(md, open(do, "w", encoding="utf-8"))
json.dump(bi, open(dst + ("/Info.dat" if os.path.exists(dst + "/Info.dat") else "/info.dat"), "w", encoding="utf-8"), indent=2)
print("Done! Created:", title)
