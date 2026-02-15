from PIL import Image

from twod_to_threed_relief.core.models import PlanSettings
from twod_to_threed_relief.core.plan import build_swap_plan


def test_build_swap_plan_steps() -> None:
    img = Image.new("RGB", (64, 64), "gray")
    plan = build_swap_plan(img, PlanSettings(strategy="bands", swap_count=4))
    assert len(plan.steps) == 4
    assert plan.steps[0].layer >= 1
