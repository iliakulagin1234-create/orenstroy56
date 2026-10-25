"""Сборка черновика рилса «Шаурма»: кадры + движение камеры + озвучка + звуки + субтитры."""
import os, subprocess, json, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR = f"{ROOT}/frames"; VO = f"{ROOT}/build/voice_tight"; OUT = f"{ROOT}/build/out"; SFX = f"{ROOT}/build/sfx"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
W, H, FPS = 1080, 1920, 30
os.makedirs(OUT, exist_ok=True); os.makedirs(SFX, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-3000:])

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())

# ---------- звуки ----------
def tighten_voices():
    """Срезать тишину по краям реплик, ужать паузы внутри и ускорить речь в 1.12 раза."""
    os.makedirs(VO, exist_ok=True)
    src = f"{ROOT}/voice"
    for f in os.listdir(src):
        if not f.endswith(".mp3") or f.startswith("00_"): continue
        af = ("silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,"
              "areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.08,areverse,"
              "silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-42dB,atempo=1.12")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{src}/{f}", "-af", af, "-ar", "44100", "-ac", "1", f"{VO}/{f}"])

def make_sfx():
    gen = {
        "scratch": "aevalsrc='0.7*sin(2*PI*(900-700*t/0.45)*t)*random(0)':d=0.45,highpass=f=300,afade=t=out:st=0.3:d=0.15",
        "boom": "aevalsrc='0.9*sin(2*PI*48*t)*exp(-2.2*t)+0.25*sin(2*PI*96*t)*exp(-4*t)':d=1.6",
        "gavel": "aevalsrc='(0.9*sin(2*PI*210*t)+0.5*random(0))*exp(-38*t)':d=0.25,apad=pad_dur=0.12,aloop=loop=1:size=17000",
        "typing": "aevalsrc='0.5*random(0)*lt(mod(t\\,0.11)\\,0.012)*gt(random(1)\\,0.25)':d=2.2,highpass=f=1500",
        "whoosh": "anoisesrc=d=0.5:c=pink:a=0.5,bandpass=f=900:w=600,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.25",
        "ding": "aevalsrc='0.5*sin(2*PI*1320*t)*exp(-5*t)+0.3*sin(2*PI*1980*t)*exp(-6*t)':d=1.0",
    }
    for name, src in gen.items():
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", src, "-ar", "44100", "-ac", "1", f"{SFX}/{name}.wav"])

# ---------- кадры ----------
# crop: (cx, cy, w) в координатах картинки 944x1680; высота = w*16/9
FULL = (472, 840, 944)
SHOTS = [
    # id, картинка, crop_from, crop_to, голоса, субтитры, титр, sfx[(name, offset)], shake, tint, min_dur
    ("02", "02.png", FULL, (330, 760, 760), ["02a_адвокат_молчишь", "02b_подсудимый_могила"],
        ["— В суде — молчишь.", "— Могила."], "Утро того же дня", [("whoosh", 0.0)], 0, "warm", 0),
    ("03", "03.png", FULL, (462, 640, 760), ["03_судья_тяжкое"],
        ["Кража с банковского счёта. Тяжкое."], "п. «г» ч. 3 ст. 158 УК РФ", [("gavel", 0.05)], 0, None, 0),
    ("04a", "04a.png", FULL, (462, 560, 700), ["04a_прокурор_похищено"],
        ["Похищено: шаурма сырная… без лука… и пакет!"], None, [], 0, None, 0),
    ("04b", "04b.png", (476, 760, 900), (476, 520, 560), ["04b_судья_пакет-вменяете"],
        ["Пакет — тоже вменяете?"], None, [], 0, None, 0),
    ("04c", "04a.png", (462, 420, 560), (462, 360, 480), ["04c_прокурор_читать-всё"],
        ["Мне сказали читать всё."], None, [], 0, None, 0),
    ("05", "05a.png", FULL, (504, 640, 700), ["05_подсудимый_сама-пикнула"],
        ["Она САМА пикнула!", "Я думал, это знак свыше!"], None, [], 14, None, 0),
    ("06", "02.png", (260, 700, 600), (262, 560, 440), ["06_адвокат_ходатайство"],
        ["Ущерб возмещён. Потерпевшая простила.", "Прошу прекратить дело за примирением сторон."], "ч. 6 ст. 15 + ст. 76 УК РФ", [], 0, None, 0),
    ("07", "04a.png", (462, 380, 520), (440, 330, 440), ["07_прокурор_котик"],
        ["Котик… нас переигрывают."], "Входящий: Котик", [], 4, "cold", 0),
    ("08", "03.png", (462, 600, 700), (462, 440, 520), ["08_судья_обоснованно"],
        ["Обоснованно."], None, [("ding", 0.4)], 0, None, 0),
    ("09", "05a.png", (504, 700, 760), (504, 500, 520), ["09_подсудимый_додо"],
        ["Спасибо! Это первый раз!", "Ну… второй.", "«Додо» не считается, там 99 рублей!"], None, [("scratch", -1)], 6, None, 0),
    ("10", "02.png", (266, 520, 420), (266, 500, 300), [],
        [], "+1 эпизод", [("boom", 0.1)], 0, "cold", 1.8),
    ("11a", "04b.png", (476, 600, 700), (476, 500, 520), ["11a_судья_суд-фиксирует"],
        ["Суд не смеётся. Суд фиксирует."], None, [], 0, None, 0),
    ("11b", "03.png", FULL, (472, 900, 860), ["11b_секретарь_додо"],
        ["(секретарь) Додо. Девяносто девять."], None, [("typing", 0.0)], 0, None, 0),
    ("12", "04a.png", FULL, (462, 500, 640), ["12_прокурор_я-же-говорила"],
        ["Я ЖЕ ГОВОРИЛА!", "…А что я говорила?"], None, [], 10, None, 0),
    ("13", "02.png", (262, 640, 560), (266, 520, 400), ["13_адвокат_мораль"],
        ["Нашли карту — несите в банк.", "Шаурма шесть лет не стоит."], None, [], 0, None, 0),
]

def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")

def wrap(lines, width=24):
    out = []
    for l in lines:
        out += textwrap.wrap(l, width) or [""]
    return out

def crop_box(c):
    cx, cy, w = c; h = w * 16 / 9
    x = min(max(cx - w / 2, 0), 944 - w); y = min(max(cy - h / 2, 0), 1680 - h)
    return x, y, w, h

def build_shot(s):
    sid, img, c0, c1, voices, subs, title, sfx, shake, tint, min_dur = s
    lead, gap, tail = 0.12, 0.15, 0.3
    vlen = [dur(f"{VO}/{v}.mp3") for v in voices]
    D = max(lead + sum(vlen) + gap * max(len(vlen) - 1, 0) + tail, min_dur or 1.7)
    N = int(D * FPS)
    x0, y0, w0, h0 = crop_box(c0); x1, y1, w1, h1 = crop_box(c1)
    # плавное движение камеры: интерполяция окна кадрирования (ease in-out)
    p = f"(0.5-0.5*cos(PI*min(n/{N}\\,1)))"
    cw = f"({w0}+({w1}-{w0})*{p})"; ch = f"({h0}+({h1}-{h0})*{p})"
    cx = f"({x0}+({x1}-{x0})*{p})"; cy = f"({y0}+({y1}-{y0})*{p})"
    vf = [f"scale=1888:3360,crop=w='2*{cw}':h='2*{ch}':x='2*{cx}':y='2*{cy}':exact=1,scale={W}:{H}:flags=lanczos,setsar=1"]
    if shake:
        vf.append(f"pad={W+2*shake}:{H+2*shake}:{shake}:{shake}:color=black,scale={W+4*shake}:{H+4*shake},crop={W}:{H}:x='{2*shake}+{shake}*sin(t*43)':y='{2*shake}+{shake}*cos(t*37)'")
    if tint == "warm":
        vf.append("colorbalance=rs=0.08:gs=0.02:bs=-0.08,vignette=PI/4")
    elif tint == "cold":
        vf.append("colorbalance=rs=-0.05:bs=0.08,vignette=PI/3.5")
    if title:
        tf = f"{OUT}/{sid}_title.txt"; open(tf, "w").write(title)
        vf.append(f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=54:fontcolor=black:box=1:boxcolor=0xFFD400@0.95:boxborderw=22:x=(w-tw)/2:y=170")
    if subs:
        lines = wrap(subs)
        sf = f"{OUT}/{sid}_sub.txt"; open(sf, "w").write("\n".join(lines))
        vf.append(f"drawtext=fontfile={FONT}:textfile={sf}:fontsize=68:fontcolor=white:borderw=7:bordercolor=black:line_spacing=14:text_align=C:x=(w-tw)/2:y=h*0.70-th/2")
    vf.append(f"fps={FPS},format=yuv420p")

    # звук: голоса подряд + эффекты
    inputs = ["-loop", "1", "-framerate", str(FPS), "-i", f"{FR}/{img}"]
    af, mix, t, k = [], [], lead, 1
    for v, L in zip(voices, vlen):
        inputs += ["-i", f"{VO}/{v}.mp3"]
        ms = int(t * 1000); af.append(f"[{k}:a]aresample=44100,aformat=channel_layouts=mono,adelay={ms}|{ms}[a{k}]"); mix.append(f"[a{k}]")
        t += L + gap; k += 1
    for name, off in sfx:
        off = D - 1.0 if off < 0 else off
        inputs += ["-i", f"{SFX}/{name}.wav"]
        ms = int(off * 1000); af.append(f"[{k}:a]volume=0.55,adelay={ms}|{ms}[a{k}]"); mix.append(f"[a{k}]"); k += 1
    inputs += ["-f", "lavfi", "-t", str(D), "-i", "anullsrc=r=44100:cl=mono"]
    mix.append(f"[{k}:a]")
    af.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{D},apad=whole_dur={D}[aout]")
    fc = f"[0:v]{','.join(vf)}[vout];" + ";".join(af)
    out = f"{OUT}/{sid}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
         "-t", str(D), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", out])
    return out, D

def build_hook():
    src = f"{ROOT}/video/кадр01_ГОТОВ_x1.4.mp4"
    tf = f"{OUT}/01_title.txt"; open(tf, "w").write("Нашёл карту → оплатил шаурму")
    D = dur(src)
    out = f"{OUT}/01.mp4"
    fc = (f"[0:v]scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},"
          f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=58:fontcolor=black:box=1:boxcolor=0xFFD400@0.95:boxborderw=24:x=(w-tw)/2:y=170,format=yuv420p[v];"
          f"[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];[1:a]volume=0.6,adelay={int((D-0.45)*1000)}|{int((D-0.45)*1000)},aformat=channel_layouts=stereo[a1];"
          f"[a0][a1]amix=inputs=2:normalize=0:duration=first[a]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", f"{SFX}/scratch.wav", "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", out])
    return out, D

def build_end():
    tf = f"{OUT}/end.txt"; open(tf, "w").write("Скинь другу,\nкоторый «просто проверил,\nработает ли карта»")
    tf2 = f"{OUT}/end2.txt"; open(tf2, "w").write("Подпишись — следующее заседание\nв гражданском суде")
    D = 2.8; out = f"{OUT}/99_end.mp4"
    vf = (f"scale=1888:3360,crop=1888:3360,scale={W}:{H},gblur=sigma=18,eq=brightness=-0.25,"
          f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=76:fontcolor=white:borderw=6:bordercolor=black:line_spacing=16:text_align=C:x=(w-tw)/2:y=h*0.38-th/2,"
          f"drawtext=fontfile={FONT}:textfile={tf2}:fontsize=46:fontcolor=0xFFD400:borderw=4:bordercolor=black:line_spacing=10:text_align=C:x=(w-tw)/2:y=h*0.62,fps={FPS},format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", f"{FR}/02.png", "-i", f"{SFX}/ding.wav",
         "-filter_complex", f"[0:v]{vf}[v];[1:a]volume=0.5,apad=whole_dur={D}[a]", "-map", "[v]", "-map", "[a]", "-t", str(D),
         "-c:v", "libx264", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", out])
    return out, D

if __name__ == "__main__":
    tighten_voices()
    make_sfx()
    parts = [build_hook()]
    for s in SHOTS:
        parts.append(build_shot(s)); print("ok", s[0], round(parts[-1][1], 2), flush=True)
    parts.append(build_end())
    lst = f"{OUT}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p, _ in parts))
    final = f"{ROOT}/ШАУРМА_черновик.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])
    print("FINAL", final, round(sum(d for _, d in parts), 1))
