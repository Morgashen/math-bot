import os
import random
import shutil
import subprocess
import textwrap
from sympy import symbols, solve, factor, latex
from gtts import gTTS


# =============================
# CONFIG
# =============================
SCENE_FILE  = "scene.py"
DEFAULT_OUT = "final.mp4"

FFMPEG_SEARCH_PATHS = [
    r"C:\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    os.path.join(os.environ.get("USERPROFILE", ""), "ffmpeg", "bin", "ffmpeg.exe"),
    os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "ffmpeg", "bin", "ffmpeg.exe"),
]


# =============================
# STEP 1: GENERATE PROBLEM
# =============================
def generate_quadratic(force_distinct: bool = True):
    a = 1
    for _ in range(100):
        r1 = random.randint(-9, 9)
        r2 = random.randint(-9, 9)
        if force_distinct and r1 == r2:
            continue
        b = -(r1 + r2)
        c = r1 * r2
        return a, b, c
    return 1, -5, 6


# =============================
# STEP 2: SOLVE PROBLEM
# =============================
def solve_quadratic(a, b, c):
    x = symbols('x')
    eq = a * x**2 + b * x + c
    return eq, factor(eq), solve(eq, x)


# =============================
# HELPERS
# =============================
def build_eq_tex(b: int, c: int) -> str:
    parts = ["x^2"]
    if b == 1:       parts.append("+ x")
    elif b == -1:    parts.append("- x")
    elif b > 0:      parts.append(f"+ {b}x")
    elif b < 0:      parts.append(f"- {abs(b)}x")
    if c > 0:        parts.append(f"+ {c}")
    elif c < 0:      parts.append(f"- {abs(c)}")
    parts.append("= 0")
    return " ".join(parts)


def spoken_signed(n: int) -> str:
    return f"minus {abs(n)}" if n < 0 else f"plus {n}"


def spoken_solutions(solutions) -> str:
    parts = [str(s) for s in solutions]
    return " or ".join(parts)


def find_ffmpeg() -> str:
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    for path in FFMPEG_SEARCH_PATHS:
        if os.path.isfile(path):
            print(f"  Found ffmpeg at: {path}")
            return path
    raise FileNotFoundError(
        "\nFFmpeg not found.\n"
        "  1. Download: https://www.gyan.dev/ffmpeg/builds/\n"
        "     (ffmpeg-release-essentials.zip)\n"
        "  2. Extract to C:\\ffmpeg\n"
        "  3. Add C:\\ffmpeg\\bin to system PATH\n"
        "  4. Restart terminal\n"
    )


def find_manim() -> list:
    if shutil.which("manim"):
        return ["manim"]
    return ["python", "-m", "manim"]


# =============================
# STEP 3: CREATE MANIM SCRIPT
# =============================
def create_manim_script(a: int, b: int, c: int, factored, solutions):
    """
    FIX 1 - LAYOUT: Use absolute Y positions on a 16-unit tall frame
             so each element occupies its own band — nothing overlaps.
    FIX 2 - VOICEOVER: Use Manim's VoiceoverScene with GTTSService so
             animations are automatically synced to speech timing.
             Falls back to plain scene if manim-voiceover isn't installed.
    """
    eq_tex       = build_eq_tex(b, c)
    factored_tex = latex(factored) + " = 0"
    sol_parts    = [f"x = {latex(s)}" for s in solutions]
    answer_tex   = r" \quad \text{or} \quad ".join(sol_parts)

    b_spoken = spoken_signed(b)
    c_spoken = spoken_signed(c)
    sols_spoken = spoken_solutions(solutions)

    vo_line1 = f"Most students get this wrong."
    vo_line2 = f"Solve: x squared {b_spoken} x {c_spoken} equals zero."
    vo_line3 = f"Step one. Factorise the expression."
    vo_line4 = f"Step two. Solve each factor."
    vo_line5 = f"The solutions are x equals {sols_spoken}."
    vo_line6 = f"Follow for more daily exam tips."

    constants = (
        f"EQ_TEX       = {repr(eq_tex)}\n"
        f"FACTORED_TEX = {repr(factored_tex)}\n"
        f"ANSWER_TEX   = {repr(answer_tex)}\n"
        f"VO_LINE1     = {repr(vo_line1)}\n"
        f"VO_LINE2     = {repr(vo_line2)}\n"
        f"VO_LINE3     = {repr(vo_line3)}\n"
        f"VO_LINE4     = {repr(vo_line4)}\n"
        f"VO_LINE5     = {repr(vo_line5)}\n"
        f"VO_LINE6     = {repr(vo_line6)}\n\n"
    )

    # ── Layout constants (frame is 9 wide × 16 tall, origin = centre) ──
    # Y positions (top = +8, bottom = -8):
    #   +6.8  title
    #   +4.5  equation
    #   +3.0  divider
    #   +1.8  step1 label
    #   +0.4  factored form
    #   -1.2  step2 label
    #   -2.6  answer
    #   -7.0  outro

    scene_code = textwrap.dedent("""\
        from manim import *

        config.pixel_width  = 1080
        config.pixel_height = 1920
        config.frame_width  = 9
        config.frame_height = 16
        config.background_color = "#0f172a"

        # ── Try to import voiceover support (pip install manim-voiceover) ──
        try:
            from manim_voiceover import VoiceoverScene
            from manim_voiceover.services.gtts import GTTSService
            USE_VOICEOVER = True
        except ImportError:
            USE_VOICEOVER = False

        # ── Base class chosen at import time ──
        _Base = VoiceoverScene if USE_VOICEOVER else Scene


        class AutoVideo(_Base):
            def construct(self):
                if USE_VOICEOVER:
                    self.set_speech_service(GTTSService())

                # ── helper: speak if voiceover available ──────────────
                def say(text):
                    if USE_VOICEOVER:
                        return self.voiceover(text=text)
                    # return a dummy context manager when not available
                    from contextlib import nullcontext
                    return nullcontext()

                # ══════════════════════════════════════════════════════
                # LAYOUT  (all positions are explicit — nothing relative)
                # ══════════════════════════════════════════════════════

                # ── Title  (y = +6.2) ─────────────────────────────────
                title = Text(
                    "Most students get this wrong",
                    font_size=46, color=YELLOW, weight=BOLD
                )
                title.move_to(UP * 6.2)

                # ── Equation  (y = +4.2) ──────────────────────────────
                eq = MathTex(EQ_TEX, font_size=72)
                eq.set_color(WHITE)
                eq.move_to(UP * 4.2)

                # ── Divider  (y = +3.0) ───────────────────────────────
                divider = Line(LEFT * 3.8, RIGHT * 3.8,
                               color=BLUE_E, stroke_width=2)
                divider.move_to(UP * 3.0)

                # ── Step 1 label  (y = +1.9) ──────────────────────────
                step1_lbl = Text(
                    "Step 1: Factorise",
                    font_size=38, color=BLUE_B, weight=BOLD
                )
                step1_lbl.move_to(UP * 1.9)

                # ── Factored form  (y = +0.5) ─────────────────────────
                step1 = MathTex(FACTORED_TEX, font_size=68)
                step1.set_color(GREEN_B)
                step1.move_to(UP * 0.5)

                # ── Step 2 label  (y = -1.2) ──────────────────────────
                step2_lbl = Text(
                    "Step 2: Solve each factor",
                    font_size=38, color=BLUE_B, weight=BOLD
                )
                step2_lbl.move_to(DOWN * 1.2)

                # ── Answer  (y = -2.7) ────────────────────────────────
                answer = MathTex(ANSWER_TEX, font_size=72)
                answer.set_color(YELLOW)
                answer.move_to(DOWN * 2.7)

                # ── Highlight box (built around answer) ───────────────
                box = SurroundingRectangle(
                    answer, color=YELLOW, buff=0.3, corner_radius=0.15
                )

                # ── Outro  (y = -6.5) ─────────────────────────────────
                outro = Text(
                    "Follow for daily exam tips",
                    font_size=36, color=GRAY_A
                )
                outro.move_to(DOWN * 6.5)

                # ══════════════════════════════════════════════════════
                # ANIMATIONS  (each wrapped in voiceover context)
                # ══════════════════════════════════════════════════════

                with say(VO_LINE1):
                    self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.8)
                    self.wait(0.3)

                with say(VO_LINE2):
                    self.play(Write(eq), run_time=1.2)
                    self.play(GrowFromCenter(divider), run_time=0.5)
                    self.wait(0.3)

                with say(VO_LINE3):
                    self.play(FadeIn(step1_lbl, shift=RIGHT * 0.2), run_time=0.6)
                    self.play(TransformFromCopy(eq, step1), run_time=1.4)
                    self.wait(0.3)

                with say(VO_LINE4):
                    self.play(FadeIn(step2_lbl, shift=RIGHT * 0.2), run_time=0.6)

                with say(VO_LINE5):
                    self.play(Write(answer), run_time=1.4)
                    self.play(Create(box), run_time=0.7)
                    self.wait(0.5)

                with say(VO_LINE6):
                    self.play(FadeIn(outro, shift=UP * 0.2), run_time=0.7)
                    self.wait(1.5)
    """)

    with open(SCENE_FILE, "w", encoding="utf-8") as fh:
        fh.write(constants + scene_code)

    print(f"  scene.py written  |  EQ = '{eq_tex}'  |  voiceover = {_check_voiceover()}")


def _check_voiceover() -> str:
    try:
        import manim_voiceover  # noqa: F401
        return "manim-voiceover (synced)"
    except ImportError:
        return "manual merge (install manim-voiceover for sync)"


# =============================
# STEP 4: RENDER VIDEO
# =============================
def render_video():
    cmd = find_manim() + ["-pqh", SCENE_FILE, "AutoVideo"]
    print(f"  Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


# =============================
# STEP 5: FIND RENDERED FILE
# =============================
def find_rendered_video() -> str:
    candidates = []
    for root, _dirs, files in os.walk("."):
        for fname in files:
            if fname.endswith(".mp4") and "AutoVideo" in fname:
                candidates.append(os.path.join(root, fname))

    if candidates:
        candidates.sort(key=os.path.getmtime, reverse=True)
        print(f"  Rendered video: {candidates[0]}")
        return candidates[0]

    all_mp4s = [
        os.path.join(r, f)
        for r, _, files in os.walk(".")
        for f in files if f.endswith(".mp4")
    ]
    hint = f"Other mp4s: {all_mp4s}" if all_mp4s else "No mp4 files found at all."
    raise FileNotFoundError(
        "AutoVideo.mp4 not found.\n" + hint + "\n"
        "Try running manually: manim -pqh scene.py AutoVideo"
    )


# =============================
# STEP 6: GENERATE VOICE
# =============================
def generate_voice(b: int, c: int, solutions) -> str:
    """
    Build a single complete voiceover mp3.
    Only used when manim-voiceover is NOT installed.
    When manim-voiceover IS installed, audio is already baked into the video.
    """
    try:
        import manim_voiceover  # noqa: F401
        print("  manim-voiceover detected — audio already baked into video, skipping gTTS.")
        return None
    except ImportError:
        pass

    text = (
        f"Most students get this wrong. "
        f"Solve: x squared {spoken_signed(b)} x {spoken_signed(c)} equals zero. "
        f"Step one. Factorise the expression. "
        f"Step two. Solve each factor. "
        f"The solutions are x equals {spoken_solutions(solutions)}. "
        f"Follow for more daily exam tips."
    )
    path = "voice.mp3"
    gTTS(text).save(path)
    print(f"  Voiceover saved: {path}")
    return path


# =============================
# STEP 7: MERGE VIDEO + AUDIO
# =============================
def merge_video(video_file: str, voice_file: str | None, output_name: str):
    """
    If voice_file is None (manim-voiceover baked it in), just copy/rename.
    Otherwise merge with FFmpeg.
    """
    if voice_file is None:
        # Audio already embedded by manim-voiceover — just rename
        import shutil as _shutil
        _shutil.copy2(video_file, output_name)
        print(f"  Copied (audio already embedded)  →  {output_name}")
        return

    ffmpeg = find_ffmpeg()
    subprocess.run(
        [
            ffmpeg, "-y",
            "-i", video_file,
            "-i", voice_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_name,
        ],
        check=True,
    )
    print(f"  Merged  →  {output_name}")


# =============================
# MAIN PIPELINE
# =============================
def main(output_name: str = DEFAULT_OUT):
    print(f"\n{'=' * 54}")
    print(f"  Generating: {output_name}")

    a, b, c = generate_quadratic(force_distinct=True)
    print(f"  Quadratic: x² + ({b})x + ({c}) = 0")

    _eq, factored, solutions = solve_quadratic(a, b, c)
    print(f"  Factored:  {factored}")
    print(f"  Solutions: {solutions}")

    create_manim_script(a, b, c, factored, solutions)

    print("  Rendering with Manim (30–90s)...")
    render_video()

    video = find_rendered_video()

    audio = generate_voice(b, c, solutions)

    print(f"  Finalising  →  {output_name} ...")
    merge_video(video, audio, output_name)

    print(f"\n  Done!  →  {output_name}")
    print('=' * 54)


# =============================
# BATCH MODE
# =============================
def batch(n: int = 5):
    """python main.py batch 10"""
    for i in range(n):
        main(output_name=f"final_{i}.mp4")


# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        batch(count)
    else:
        main()