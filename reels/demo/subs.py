"""Субтитры и титры для демо «Шаурма v3» в формате ASS (цвет по персонажу)."""
H, C1, C2, C3 = 0.0, 3.54, 10.79, 16.94

# цвета ASS: &HBBGGRR
STYLES = {
    "L": "&H00FFFFFF",  # адвокат — белый
    "V": "&H0066E0FF",  # Витя — жёлтый
    "J": "&H00FFD9A6",  # судья — голубой
}
SUBS = [
    (H, 0.15, 1.6, "V", "ШЕСТЬ ЛЕТ?!"),
    (H, 1.65, 3.54, "V", "ЗА ШАУРМУ?!"),
    (C1, 0.0, 1.95, "L", "Витёк, коротко. Карту нашёл?"),
    (C1, 2.1, 2.95, "V", "Нашёл."),
    (C1, 3.05, 3.9, "L", "Потратил?"),
    (C1, 3.95, 4.75, "V", "Чуть-чуть."),
    (C1, 4.8, 5.85, "L", "Сколько?"),
    (C1, 5.95, 7.25, "V", "Триста сорок семь."),
    (C2, 0.0, 0.85, "L", "На что?"),
    (C2, 0.9, 1.85, "V", "Шаурма."),
    (C2, 1.9, 2.55, "L", "Всё?"),
    (C2, 2.6, 3.45, "V", "Всё."),
    (C2, 3.5, 4.45, "L", "Красава."),
    (C2, 4.5, 6.15, "L", "Пять минут — и домой."),
    (C3, 0.0, 1.6, "J", "Кража с банковского счёта."),
    (C3, 1.65, 3.5, "J", "Тяжкое. До шести лет."),
    (C3, 3.55, 5.25, "V", "Ты, блин, сказал пять минут!"),
    (C3, 5.3, 7.45, "L", "Пять минут — это я про свою речь."),
]
TITLES = [
    (H, 0.0, 3.54, "Нашёл карту → оплатил шаурму"),
    (C3, 0.0, 3.5, "п. «г» ч. 3 ст. 158 УК РФ"),
]

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
for k, col in STYLES.items():
    head += f"Style: {k},Inter ExtraBold,74,{col},&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,2,70,70,520,1\n"
head += "Style: T,Inter ExtraBold,54,&H00000000,&H000000FF,&H0000D4FF,&H0000D4FF,-1,0,0,0,100,100,0,0,3,18,0,8,60,60,190,1\n"
head += "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

ev = []
for base, a, b, st, txt in SUBS:
    # лёгкий «поп»: текст появляется с увеличением
    ev.append(f"Dialogue: 0,{ts(base+a)},{ts(base+b)},{st},,0,0,0,,{{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}}{txt}")
for base, a, b, txt in TITLES:
    ev.append(f"Dialogue: 1,{ts(base+a)},{ts(base+b)},T,,0,0,0,,{txt}")
open("subs.ass", "w").write(head + "\n".join(ev) + "\n")
print("ok", len(ev))
