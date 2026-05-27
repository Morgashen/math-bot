EQ_TEX       = 'x^2 + 3x - 54 = 0'
FACTORED_TEX = '\\left(x - 6\\right) \\left(x + 9\\right) = 0'
ANSWER_TEX   = 'x = -9 \\quad \\text{or} \\quad x = 6'
VO_LINE1     = 'Most students get this wrong.'
VO_LINE2     = 'Solve: x squared plus 3 x minus 54 equals zero.'
VO_LINE3     = 'Step one. Factorise the expression.'
VO_LINE4     = 'Step two. Solve each factor.'
VO_LINE5     = 'The solutions are x equals -9 or 6.'
VO_LINE6     = 'Follow for more daily exam tips.'

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
